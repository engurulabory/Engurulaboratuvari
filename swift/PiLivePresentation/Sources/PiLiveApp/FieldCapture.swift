import AppKit
import Foundation
import CryptoKit
import PiLivePresentation

struct FieldCapture {
    static func stamp() -> String {
        let f = ISO8601DateFormatter(); f.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return f.string(from: Date())
    }
    @MainActor static func event(task: String, journeyId: String, packet: Data, portfolio: Portfolio,
                                row: ProjectRow, renderedAt: String, selectedDigest: String) throws -> [String: Any] {
        let evidence = try portfolio.projectEvidence(projectId: row.projectId, selectedDigest: selectedDigest)
        guard let directory = Bundle.main.object(forInfoDictionaryKey: "SessionDirectory") as? String,
              let window = NSApp.windows.first(where: { $0.isVisible && !$0.isMiniaturized && $0.title.contains("PiLive") }),
              let view = window.attachedSheet?.contentView ?? window.contentView,
              let image = view.bitmapImageRepForCachingDisplay(in: view.bounds) else { throw PresentationHold.invalidSource }
        let start = ProcessInfo.processInfo.systemUptime
        view.displayIfNeeded(); view.cacheDisplay(in: view.bounds, to: image)
        guard let png = image.representation(using: .png, properties: [:]), png.count > 100 else { throw PresentationHold.invalidSource }
        let filename = "FIELD_" + task + "_" + UUID().uuidString + ".png"
        try png.write(to: URL(fileURLWithPath: directory).appendingPathComponent(filename), options: .withoutOverwriting)
        return ["taskId": task, "journeyId": journeyId, "eventAt": stamp(), "uiRenderedAt": renderedAt,
            "sourceReadAt": portfolio.sourceReadAt, "adapterBuiltAt": portfolio.adapterBuiltAt,
            "sourceRevision": portfolio.sourceRevision, "projectionDigest": portfolio.projectionDigest,
            "projectId": row.projectId, "projectKey": row.key,
            "done": row.done.map { $0 as Any } ?? NSNull(), "total": row.total.map { $0 as Any } ?? NSNull(),
            "percent": row.percent.map { $0 as Any } ?? NSNull(), "activeItem": row.activeItem ?? "N/A",
            "finish": row.finish, "officialAcceptance": row.officialAcceptance,
            "projectSourcePins": evidence.pins, "readerPacketBase64": packet.base64EncodedString(),
            "userConfirmation": "EXPLICIT_TASK_BUTTON", "windowVisible": true,
            "screenshot": filename, "screenshotSha256": SHA256.hash(data: png).map { String(format: "%02x", $0) }.joined(),
            "captureSurface": window.attachedSheet == nil ? "OWN_WINDOW_CONTENT" : "OWN_SHEET_CONTENT",
            "captureDurationMs": (ProcessInfo.processInfo.systemUptime - start) * 1000,
            "productAcceptance": "HOLD", "verifiedFinish": "HOLD"]
    }
}
