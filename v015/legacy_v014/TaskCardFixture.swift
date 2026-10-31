// Standalone review fixture. Mac compile and visual acceptance: NOT_TESTED.
// V0.6 Ulak layout is not replaced or edited by this fixture.
import SwiftUI

enum SnapshotState: String { case hold = "HOLD", verified = "Doğrulandı", waiting = "Bekliyor" }
enum SnapshotError: Error { case invalidBasisPoints, missingSource }

struct TaskSnapshot: Identifiable {
    let id: String
    let title: String
    let verifiedBasisPoints: Int
    let state: SnapshotState
    let sourceSHA: String
    let lastVerifiedEvent: String

    init(id: String, title: String, verifiedBasisPoints: Int, state: SnapshotState,
         sourceSHA: String, lastVerifiedEvent: String) throws {
        guard (0...10000).contains(verifiedBasisPoints) else { throw SnapshotError.invalidBasisPoints }
        guard sourceSHA.count == 64, sourceSHA.allSatisfy({ "0123456789abcdef".contains($0) })
            else { throw SnapshotError.missingSource }
        self.id = id; self.title = title; self.verifiedBasisPoints = verifiedBasisPoints
        self.state = state; self.sourceSHA = sourceSHA; self.lastVerifiedEvent = lastVerifiedEvent
    }
}

struct TaskCardView: View {
    let snapshot: TaskSnapshot
    var body: some View {
        VStack(alignment: .leading) {
            Text(snapshot.title)
            Text(String(format: "%.2f%%", Double(snapshot.verifiedBasisPoints) / 100.0))
            Text(snapshot.state.rawValue)
            Text(snapshot.lastVerifiedEvent)
            Text("Kaynak: \(snapshot.sourceSHA)").font(.caption)
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(snapshot.title), \(snapshot.state.rawValue), yüzde \(Double(snapshot.verifiedBasisPoints) / 100.0), son doğrulanmış olay \(snapshot.lastVerifiedEvent), kaynak \(snapshot.sourceSHA)")
    }
}
