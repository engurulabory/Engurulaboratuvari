import Foundation

public enum Screen: String, CaseIterable { case overview, now, projects }
public enum Availability: String { case fresh = "FRESH", stale = "STALE", offline = "OFFLINE", hold = "HOLD" }
public struct ProjectGroup {
    public let name: String
    public let rows: [ProjectRow]
    public let countText: String
}

/// Immutable four-screen state. No portfolio percentage or global priority is invented.
public struct ScreenState {
    public let portfolio: Portfolio?
    public let availability: Availability
    public let sourceAgeSeconds: Double?
    public let isCache: Bool
    public let reason: String
    public var projectCount: Int? { portfolio?.projects.count }
    public var qualifiedCount: Int? { portfolio?.qualifiedCount }
    public var globalActiveSelection: String { "HOLD · GLOBAL_PRIORITY_NOT_PROVEN" }
    public var p02: ProjectRow? { portfolio?.projects.first { $0.projectId == "ENGURU_PLIVE_P02_USER_SCREEN" } }
    public var sourceRevision: String? { portfolio?.sourceRevision }
    public var projectionDigest: String? { portfolio?.projectionDigest }
    // The verified portfolio currently has no source-bound productionArea/facet.
    // Keep five headings N/A and every project visible, without heuristic classification.
    public func projectGroups(search: String = "") -> [ProjectGroup] {
        let rows = (portfolio?.projects ?? []).filter {
            search.isEmpty || $0.key.localizedCaseInsensitiveContains(search) || $0.projectId.localizedCaseInsensitiveContains(search)
        }
        let areas = [("ENGINE", "Motor"), ("CORE", "Çekirdek"), ("WEB", "Web"), ("APP", "App"), ("AGENT", "Agent")]
        let source = portfolio?.sourceClassification ?? [:]
        let known = Set(areas.map { $0.0 })
        return areas.map { code, label in
            let members = rows.filter { source[$0.key]?.productionArea == code }
            return ProjectGroup(name: label, rows: members, countText: members.isEmpty ? "N/A" : String(members.count))
        } + [ProjectGroup(name: "Kaynak eşlemesi bekleniyor", rows: rows.filter { !known.contains(source[$0.key]?.productionArea ?? "") }, countText: String(rows.filter { !known.contains(source[$0.key]?.productionArea ?? "") }.count))]

    }
    public var accessibilityAnnouncement: String {
        "\(availability.rawValue)\(isCache ? " · son bilinen kayıt" : ""), \(projectCount.map(String.init) ?? "N/A") proje, \(qualifiedCount.map(String.init) ?? "N/A") doğrulanmış sayaç, resmî kabul HOLD"
    }
}

/// Atomic publication boundary. Reader request tokens prevent old completions replacing newer ones.
@MainActor public final class PresentationStore {
    public private(set) var state = ScreenState(portfolio: nil, availability: .hold, sourceAgeSeconds: nil, isCache: false, reason: "SOURCE_NOT_READ")
    public private(set) var selectedScreen: Screen = .overview
    public private(set) var evidenceIsOpen = false
    public private(set) var focusTarget = "overview.heading"
    private var evidenceOpener = "evidence.button"
    private var generation = 0
    private var lastGood: Portfolio?
    private let staleAfter: TimeInterval
    public init(staleAfter: TimeInterval = 60) { self.staleAfter = staleAfter.isFinite && staleAfter > 0 ? staleAfter : 60 }
    @discardableResult public func beginRefresh() -> Int { generation += 1; return generation }
    public func accept(_ data: Data, trust: SourceIdentity, request: Int, now: Date) throws {
        guard request == generation else { throw PresentationHold.obsoleteRequest }
        do {
            let p = try Portfolio.decode(data, trust: trust, now: now)
            lastGood = p
            publish(p, now: now, offline: false)
        } catch {
            state = ScreenState(portfolio: nil, availability: .hold, sourceAgeSeconds: nil, isCache: false, reason: "SOURCE_VALIDATION_HOLD")
            throw error
        }
    }
    private func publish(_ p: Portfolio, now: Date, offline: Bool) {
        let age = now.timeIntervalSince(Portfolio.date(p.sourceReadAt)!)
        guard age >= 0 else { state = ScreenState(portfolio: nil, availability: .hold, sourceAgeSeconds: nil, isCache: false, reason: "CLOCK_HOLD"); return }
        state = ScreenState(portfolio: p, availability: offline ? .offline : (age > staleAfter ? .stale : .fresh), sourceAgeSeconds: age, isCache: offline, reason: offline ? "LAST_KNOWN_CACHE" : "SOURCE_BOUND")
    }
    /// Call on clock ticks; time passage alone can make a snapshot stale.
    public func tick(now: Date) {
        guard let p = state.portfolio else { return }; publish(p, now: now, offline: state.availability == .offline)
    }
    public func disconnected(request: Int, now: Date) {
        guard request == generation else { return }
        if let p = lastGood { publish(p, now: now, offline: true) }
        else { state = ScreenState(portfolio: nil, availability: .offline, sourceAgeSeconds: nil, isCache: false, reason: "NO_CACHE") }
    }
    public func navigate(_ screen: Screen) {
        guard !evidenceIsOpen else { return }; selectedScreen = screen; focusTarget = screen.rawValue + ".heading"
    }
    public func openEvidence(from control: String = "evidence.button") {
        guard !evidenceIsOpen else { return }; evidenceOpener = control; evidenceIsOpen = true; focusTarget = "evidence.heading"
    }
    public func closeEvidence() { evidenceIsOpen = false; focusTarget = evidenceOpener }
    public func escape() { if evidenceIsOpen { closeEvidence() } }
}
