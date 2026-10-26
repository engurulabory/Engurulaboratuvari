import Foundation
import CryptoKit

public enum PresentationHold: Error { case invalidSource, invalidCounter, invalidTime, obsoleteRequest }

/// Supplied by the verified reader, never inferred from the incoming wire itself.
public struct SourceIdentity {
    public let revision: String
    public let pins: [String: String]
    public let digest: String
    public let wireSha256: String
    public init(revision: String, pins: [String: String], digest: String, wireSha256: String) {
        self.revision = revision; self.pins = pins; self.digest = digest; self.wireSha256 = wireSha256
    }
}

public struct ProjectRow: Decodable, Equatable, Identifiable {
    public var id: String { projectId }
    public let key: String
    public let projectId: String
    public let status: String
    public let reason: String
    public let done: Int?
    public let total: Int?
    public let percent: Double?
    public let activeItem: String?
    public let activePackage: String?
    public let nextAction: String?
    public let canonicalFinish: String?
    public let finish: String
    public let officialAcceptance: String
    public let closed: Bool
    public var counterText: String {
        guard let done, let total, let percent else { return "N/A · HOLD" }
        return "\(done)/\(total) · %\(percent)"
    }
    public var accessibilityLabel: String {
        "\(key), \(counterText), teknik finiş \(finish), resmî kabul \(officialAcceptance)"
    }
}

public struct Portfolio: Decodable {
    public let schema: String
    public let sourceRevision: String
    public let sourcePins: [String: String]
    public let projectionDigest: String
    public let projects: [ProjectRow]
    public struct Classification: Decodable { public let projectId: String; public let state: String?; public let worklist: String?; public let productionArea: String?; public let productionFacet: String? }
    public let sourceClassification: [String: Classification]?
    public let sourceReadAt: String
    public let adapterBuiltAt: String
    public let uiRenderedAt: String?
    public let uiPublication: String
    public let canonicalWrite: String
    public let productionGrant: String
    public let verifiedFinish: String
    public let technicalPassIsOfficial: Bool
    public struct Coverage: Decodable { let projects: Int; let qualifiedCounters: Int; let sourceBoundObservations: Int }
    public let factCoverage: Coverage
    public struct Observation: Decodable { let sourceReadAt: String }
    public let sourceObservations: [String: Observation]
    public var qualifiedCount: Int { projects.filter { $0.status == "PASS_CORE_READ_ONLY" }.count }

    public static func date(_ text: String) -> Date? {
        let parser = ISO8601DateFormatter()
        parser.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return parser.date(from: text) ?? ISO8601DateFormatter().date(from: text)
    }
    private static func matches(_ value: String, _ regex: String) -> Bool {
        value.range(of: regex, options: .regularExpression) != nil
    }
    public static func decode(_ data: Data, trust: SourceIdentity, now: Date) throws -> Portfolio {
        guard data.count <= 4 * 1024 * 1024 else { throw PresentationHold.invalidSource }
        struct Wire: Decodable { let schema: String; let snapshot: Portfolio; let canonicalProjection: String }
        let wireHash = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
        guard wireHash == trust.wireSha256 else { throw PresentationHold.invalidSource }
        let wire = try JSONDecoder().decode(Wire.self, from: data)
        let p = wire.snapshot
        let hash = SHA256.hash(data: Data(wire.canonicalProjection.utf8)).map { String(format: "%02x", $0) }.joined()
        guard wire.schema == "enguru.pilive.screen-wire/v1", p.schema == "enguru.pilive.core-portfolio/v1",
              matches(trust.revision, "^[a-f0-9]{40}$"), matches(trust.digest, "^[a-f0-9]{64}$"),
              !trust.pins.isEmpty, trust.pins.allSatisfy({ matches($0.value, "^[a-f0-9]{64}$") }),
              p.sourceRevision == trust.revision, p.sourcePins == trust.pins,
              p.projectionDigest == trust.digest, hash == trust.digest,
              p.canonicalWrite == "NONE", p.productionGrant == "HOLD", p.verifiedFinish == "HOLD", !p.technicalPassIsOfficial,
              p.uiRenderedAt == nil, p.uiPublication == "NOT_EXECUTED"
        else { throw PresentationHold.invalidSource }
        // Compare authenticated canonical content with the wire's presentation fields.
        guard let envelope = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let snapshot = envelope["snapshot"] as? [String: Any],
              let canonical = try JSONSerialization.jsonObject(with: Data(wire.canonicalProjection.utf8)) as? [String: Any]
        else { throw PresentationHold.invalidSource }
        let fields = ["sourceRevision", "sourcePins", "projects", "canonicalWrite", "productionGrant", "verifiedFinish", "technicalPassIsOfficial"]
        let content = snapshot.filter { fields.contains($0.key) }
        guard NSDictionary(dictionary: content).isEqual(to: canonical) else { throw PresentationHold.invalidSource }
        guard let read = date(p.sourceReadAt), let built = date(p.adapterBuiltAt), read <= built, built <= now,
              p.sourceObservations.values.allSatisfy({ o in
                  guard let t = date(o.sourceReadAt) else { return false }; return read <= t && t <= built
              }) else { throw PresentationHold.invalidTime }
        guard !p.projects.isEmpty, p.projects.count <= 1000,
              Set(p.projects.map(\.key)).count == p.projects.count,
              Set(p.projects.map(\.projectId)).count == p.projects.count,
              p.projects.map(\.key) == p.projects.map(\.key).sorted(),
              Set(p.sourceObservations.keys).isSubset(of: Set(p.projects.map(\.key))),
              p.factCoverage.projects == p.projects.count, p.factCoverage.qualifiedCounters == p.qualifiedCount,
              p.factCoverage.sourceBoundObservations == p.sourceObservations.count
        else { throw PresentationHold.invalidSource }
        if let mappings = p.sourceClassification {
            guard Set(mappings.keys).isSubset(of: Set(p.projects.map(\.key))), mappings.allSatisfy({ key, item in p.projects.contains { $0.key == key && $0.projectId == item.projectId } }) else { throw PresentationHold.invalidSource }
        }
        for row in p.projects {
            guard matches(row.key, "^[a-z0-9][a-z0-9_-]{0,127}$"), matches(row.projectId, "^[A-Za-z0-9_.-]{1,128}$"),
                  row.officialAcceptance == "HOLD", !row.closed, ["HOLD", "VERIFIED"].contains(row.finish)
            else { throw PresentationHold.invalidSource }
            if row.status == "PASS_CORE_READ_ONLY" {
                guard let done = row.done, let total = row.total, let percent = row.percent,
                      total > 0, total <= 1_000_000_000, done >= 0, done <= total, percent.isFinite,
                      abs(percent - (Double(done) * 10000 / Double(total)).rounded() / 100) < 0.000001,
                      !(done < total && row.finish == "VERIFIED"),
                      row.activeItem?.isEmpty == false, row.activePackage?.isEmpty == false, row.nextAction?.isEmpty == false,
                      p.sourceObservations[row.key] != nil
                else { throw PresentationHold.invalidCounter }
            } else {
                guard row.status == "HOLD", row.done == nil, row.total == nil, row.percent == nil, row.finish == "HOLD"
                else { throw PresentationHold.invalidCounter }
            }
        }
        return p
    }
}
