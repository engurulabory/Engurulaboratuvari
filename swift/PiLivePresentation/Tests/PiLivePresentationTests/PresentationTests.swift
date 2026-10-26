import XCTest
import CryptoKit
@testable import PiLivePresentation

final class PresentationTests: XCTestCase {
    func bytes() throws -> Data { try Data(contentsOf: Bundle.module.url(forResource: "native-wire", withExtension: "json", subdirectory: "Fixtures")!) }
    func now() -> Date { Portfolio.date("2026-10-26T06:04:00Z")! }
    // Test-only trust oracle; production obtains identity outside the incoming wire.
    func trust(_ data: Data) throws -> SourceIdentity {
        let o = try JSONSerialization.jsonObject(with: data) as! [String: Any]
        let p = o["snapshot"] as! [String: Any]
        return SourceIdentity(revision: p["sourceRevision"] as! String, pins: p["sourcePins"] as! [String: String], digest: p["projectionDigest"] as! String, wireSha256: SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined())
    }
    func changed(_ edit: (inout [String: Any]) -> Void, resign: Bool = false) throws -> Data {
        var o = try JSONSerialization.jsonObject(with: bytes()) as! [String: Any]
        var p = o["snapshot"] as! [String: Any]; edit(&p)
        if resign {
            let fields = ["sourceRevision", "sourcePins", "projects", "canonicalWrite", "productionGrant", "verifiedFinish", "technicalPassIsOfficial"]
            let raw = try JSONSerialization.data(withJSONObject: p.filter { fields.contains($0.key) }, options: [.sortedKeys, .withoutEscapingSlashes])
            p["projectionDigest"] = SHA256.hash(data: raw).map { String(format: "%02x", $0) }.joined()
            o["canonicalProjection"] = String(data: raw, encoding: .utf8)!
        }
        o["snapshot"] = p
        return try JSONSerialization.data(withJSONObject: o, options: [.sortedKeys, .withoutEscapingSlashes])
    }
    func testNativeFifteenAndFourteenQualified() throws {
        let data = try bytes(); let p = try Portfolio.decode(data, trust: trust(data), now: now())
        XCTAssertEqual(p.projects.count, 15); XCTAssertEqual(p.qualifiedCount, 14); XCTAssertEqual(p.sourcePins.count, 48)
        let row = p.projects.first { $0.key == "plive-p02-user-screen" }!
        XCTAssertEqual(row.done, 0); XCTAssertEqual(row.total, 12); XCTAssertEqual(row.activeItem, "P02.S01.01")
    }
    func testVisualHoldAndTechnicalFinishSeparation() throws {
        let data = try bytes(); let p = try Portfolio.decode(data, trust: trust(data), now: now())
        XCTAssertNil(p.projects.first { $0.key == "visual-cockpit-premium-v1" }!.percent)
        let core = p.projects.first { $0.key == "progress-core" }!
        XCTAssertEqual(core.percent, 100); XCTAssertEqual(core.finish, "HOLD")
        XCTAssertTrue(p.projects.allSatisfy { !$0.closed && $0.officialAcceptance == "HOLD" })
    }
    func testTamperedTimestampFailsTrustedHash() throws {
        let edited = try changed { $0["sourceReadAt"] = "2026-10-26T06:03:59Z" }
        XCTAssertThrowsError(try Portfolio.decode(edited, trust: trust(bytes()), now: now()))
    }
    func testRevisionAndPinDriftFail() throws {
        let expected = try trust(bytes())
        let edits = [try changed { $0["sourceRevision"] = String(repeating: "0", count: 40) }, try changed { $0["sourcePins"] = ["unknown": String(repeating: "a", count: 64)] }]
        for data in edits { XCTAssertThrowsError(try Portfolio.decode(data, trust: expected, now: now())) }
    }
    func testDuplicateIdentityCounterBooleanAndPercentRejected() throws {
        for kind in ["identity", "counter", "boolean", "percentage"] {
            let data = try changed({ p in
                var rows = p["projects"] as! [[String: Any]]
                if kind == "identity" { rows[1]["projectId"] = rows[0]["projectId"] }
                else if kind == "counter" { rows[0]["done"] = -1 }
                else if kind == "boolean" { rows[0]["done"] = true }
                else { rows[0]["percent"] = 92 }
                p["projects"] = rows
            }, resign: true)
            XCTAssertThrowsError(try Portfolio.decode(data, trust: trust(data), now: now()), kind)
        }
    }
    func testMalformedAndFutureTimeHold() throws {
        XCTAssertThrowsError(try Portfolio.decode(Data("{".utf8), trust: trust(bytes()), now: now()))
        let data = try changed { $0["adapterBuiltAt"] = "2027-01-01T00:00:00Z" }
        XCTAssertThrowsError(try Portfolio.decode(data, trust: trust(data), now: now()))
    }
    func testFourScreensNoInventedPriorityAndUnclassifiedSearch() async throws {
        let data = try bytes(); let expected = try trust(data); let time = now()
        try await MainActor.run {
            let store = PresentationStore(); try store.accept(data, trust: expected, request: store.beginRefresh(), now: time)
            XCTAssertEqual(store.state.globalActiveSelection, "HOLD · GLOBAL_PRIORITY_NOT_PROVEN")
            XCTAssertEqual(store.state.projectGroups().count, 6); XCTAssertEqual(store.state.projectGroups().last!.rows.count, 15)
            XCTAssertTrue(store.state.projectGroups().prefix(5).allSatisfy { $0.countText == "N/A" })
            XCTAssertEqual(store.state.projectGroups(search: "no-such-project").last!.rows.count, 0)
            XCTAssertEqual(store.state.projectGroups(search: "P02_USER").last!.rows.count, 1)
        }
    }
    func testEvidenceEscapeFocusAndNavigationGuard() async {
        await MainActor.run {
            let s = PresentationStore(); s.navigate(.projects); s.openEvidence(from: "project.evidence")
            XCTAssertTrue(s.evidenceIsOpen); XCTAssertEqual(s.focusTarget, "evidence.heading")
            s.navigate(.now); XCTAssertEqual(s.selectedScreen, .projects)
            s.escape(); XCTAssertFalse(s.evidenceIsOpen); XCTAssertEqual(s.focusTarget, "project.evidence")
            s.navigate(.now); XCTAssertEqual(s.focusTarget, "now.heading")
        }
    }
    func testTextAccessibilityAndRenderedTime() throws {
        let data = try bytes(); let p = try Portfolio.decode(data, trust: trust(data), now: now())
        XCTAssertNil(p.uiRenderedAt)
        XCTAssertTrue(p.projects.allSatisfy { $0.accessibilityLabel.contains("resmî kabul HOLD") })
        XCTAssertTrue(p.projects.first { $0.status == "HOLD" }!.accessibilityLabel.contains("N/A"))
    }
    func testFreshStaleOfflineCacheAndEmptyOffline() async throws {
        let data = try bytes(); let expected = try trust(data); let time = now()
        try await MainActor.run {
            let s = PresentationStore(); let request = s.beginRefresh()
            try s.accept(data, trust: expected, request: request, now: time); XCTAssertEqual(s.state.availability, .fresh)
            s.tick(now: time.addingTimeInterval(120)); XCTAssertEqual(s.state.availability, .stale)
            s.disconnected(request: request, now: time.addingTimeInterval(121))
            XCTAssertEqual(s.state.availability, .offline); XCTAssertTrue(s.state.isCache)
            let empty = PresentationStore(); empty.disconnected(request: empty.beginRefresh(), now: time)
            XCTAssertNil(empty.state.portfolio); XCTAssertEqual(empty.state.availability, .offline)
        }
    }
    func testObsoleteRequestDriftAndTrustedReadback() async throws {
        let data = try bytes(); let expected = try trust(data); let time = now()
        try await MainActor.run {
            let s = PresentationStore(); let old = s.beginRefresh(); let current = s.beginRefresh()
            try s.accept(data, trust: expected, request: current, now: time)
            XCTAssertThrowsError(try s.accept(data, trust: expected, request: old, now: time)); XCTAssertEqual(s.state.projectCount, 15)
            XCTAssertThrowsError(try s.accept(Data("broken".utf8), trust: expected, request: current, now: time))
            XCTAssertNil(s.state.portfolio); XCTAssertEqual(s.state.availability, .hold)
            try s.accept(data, trust: expected, request: s.beginRefresh(), now: time); XCTAssertEqual(s.state.projectCount, 15)
        }
    }
    func testSwiftUIObservableBridge() async {
        await MainActor.run {
            let bridge = SwiftUIState(store: PresentationStore())
            bridge.navigate(.projects); XCTAssertEqual(bridge.selected, .projects)
            bridge.openEvidence(); XCTAssertTrue(bridge.evidenceIsOpen)
            bridge.escape(); XCTAssertFalse(bridge.evidenceIsOpen)
        }
    }
}
