import Foundation

public struct ProjectEvidence {
    public let row: ProjectRow
    public let sourceRevision: String
    public let projectionDigest: String
    public let sourceReadAt: String
    public let adapterBuiltAt: String
    public let pins: [String: String]
}

extension Portfolio {
    /// Project selection is a canonical ID, never a cached row or list index.
    public func projectEvidence(projectId: String, selectedDigest: String) throws -> ProjectEvidence {
        guard selectedDigest == projectionDigest,
              let row = projects.first(where: { $0.projectId == projectId }),
              let source = sourceClassification?[row.key], source.projectId == projectId,
              let state = source.state, let worklist = source.worklist, state != worklist,
              [state, worklist].allSatisfy({ $0.hasPrefix("governance/") && !$0.split(separator: "/").contains("..") }),
              let statePin = sourcePins[state], let worklistPin = sourcePins[worklist]
        else { throw PresentationHold.invalidSource }
        return ProjectEvidence(row: row, sourceRevision: sourceRevision, projectionDigest: projectionDigest,
            sourceReadAt: sourceReadAt, adapterBuiltAt: adapterBuiltAt, pins: [state: statePin, worklist: worklistPin])
    }
}

/// Freezes source identity for a bounded real-user journey, not source contents.
public struct FieldSourceLock {
    public let revision: String
    public let digest: String
    public init(_ portfolio: Portfolio) { revision = portfolio.sourceRevision; digest = portfolio.projectionDigest }
    public func requireSameSource(_ portfolio: Portfolio) throws {
        guard revision == portfolio.sourceRevision, digest == portfolio.projectionDigest else { throw PresentationHold.invalidSource }
    }
}
