#if canImport(SwiftUI)
import SwiftUI

/// State bridge for future accepted views; no final layout, animation or native launch here.
@MainActor public final class SwiftUIState: ObservableObject {
    @Published public private(set) var screen: ScreenState
    @Published public private(set) var selected: Screen = .overview
    @Published public private(set) var evidenceIsOpen = false
    @Published public private(set) var focusTarget = "overview.heading"
    public let store: PresentationStore
    public init(store: PresentationStore) { self.store = store; self.screen = store.state }
    public func synchronize() {
        screen = store.state; selected = store.selectedScreen
        evidenceIsOpen = store.evidenceIsOpen; focusTarget = store.focusTarget
    }
    public func navigate(_ screen: Screen) { store.navigate(screen); synchronize() }
    public func openEvidence(from control: String = "evidence.button") { store.openEvidence(from: control); synchronize() }
    public func escape() { store.escape(); synchronize() }
    // Accepted views bind focusTarget with AccessibilityFocusState/FocusState,
    // announce screen.accessibilityAnnouncement and honor accessibilityReduceMotion.
    // These state intents alone do not prove native focus trapping or VoiceOver behavior.
}
#endif
