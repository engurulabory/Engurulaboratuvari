import SwiftUI
import AppKit
import CryptoKit
import PiLivePresentation

private enum ReaderFailure: Error { case unavailable, failed }
private struct ReaderPacket: Decodable {
    struct Identity: Decodable { let revision: String; let pins: [String: String]; let digest: String; let wireSha256: String }
    let wire: String
    let identity: Identity
    struct Observation: Decodable {
        struct Fact: Decodable {
            struct Summary: Decodable { let declaredPass: Int? }
            struct Verify: Decodable { let evidencedPass: Int?; let unverifiedPass: Int? }
            let summary: Summary?; let verify: Verify?
        }
        let coreFacts: [String: Fact]?
    }
    let observation: Observation
}
private func readPacket() throws -> Data {
    guard let resources = Bundle.main.resourceURL,
          let python = Bundle.main.object(forInfoDictionaryKey: "PythonExecutable") as? String,
          let pin = Bundle.main.object(forInfoDictionaryKey: "ReaderManifestSHA256") as? String,
          python.hasPrefix("/"), pin.count == 64 else { throw ReaderFailure.unavailable }
    let process = Process(); process.executableURL = URL(fileURLWithPath: python)
    process.arguments = ["-I", "-B", "-S", resources.appendingPathComponent("reader/launch_reader.py").path, pin]
    process.standardError = FileHandle.nullDevice
    let pipe = Pipe(); process.standardOutput = pipe
    try process.run()
    let deadline = DispatchWorkItem { if process.isRunning { process.terminate() } }
    DispatchQueue.global().asyncAfter(deadline: .now() + 110, execute: deadline)
    let data = pipe.fileHandleForReading.readDataToEndOfFile()
    process.waitUntilExit(); deadline.cancel()
    guard data.count <= 4 * 1024 * 1024 else { throw ReaderFailure.failed }
    return data
}

@MainActor private final class LiveController: ObservableObject {
    let model = SwiftUIState(store: PresentationStore(staleAfter: 60))
    @Published var isLoading = false
    @Published var readerMessage = "Kaynak okunuyor"
    @Published var verificationNotes: [String: String] = [:]
    private var packet: Data?
    private var recorded = false
    @Published private(set) var uiRenderedAt: String?
    func refresh() {
        guard !isLoading else { return }
        isLoading = true
        let request = model.store.beginRefresh()
        Task {
            var attempted: Data?
            do {
                let bytes = try await Task.detached(priority: .userInitiated) { try readPacket() }.value
                attempted = bytes
                let p = try JSONDecoder().decode(ReaderPacket.self, from: bytes)
                guard let wire = Data(base64Encoded: p.wire) else { throw ReaderFailure.failed }
                let identity = SourceIdentity(revision: p.identity.revision, pins: p.identity.pins, digest: p.identity.digest, wireSha256: p.identity.wireSha256)
                try model.store.accept(wire, trust: identity, request: request, now: Date())
                verificationNotes = (p.observation.coreFacts ?? [:]).mapValues { f in
                    "Beyan: \(f.summary?.declaredPass.map(String.init) ?? "N/A") · Kanıtlı: \(f.verify?.evidencedPass.map(String.init) ?? "N/A") · Doğrulanmamış: \(f.verify?.unverifiedPass.map(String.init) ?? "N/A")"
                }
                packet = bytes; readerMessage = "Kaynak doğrulandı"
            } catch {
                if let attempted, let directory = Bundle.main.object(forInfoDictionaryKey: "SessionDirectory") as? String {
                    try? attempted.write(to: URL(fileURLWithPath: directory).appendingPathComponent("READER_FAILURE.json"), options: .withoutOverwriting)
                }
                // A failed source refresh must not present last-good counters as current.
                // The store clears current data; offline cache requires explicit classification.
                try? model.store.accept(Data(), trust: SourceIdentity(revision: "", pins: [:], digest: "", wireSha256: ""), request: request, now: Date())
                readerMessage = "HOLD · Kaynak veya reader doğrulaması bekleniyor"
            }
            isLoading = false; model.synchronize()
        }
    }
    func tick() { model.store.tick(now: Date()); model.synchronize() }
    func recordVisibleFrame() {
        guard !recorded, !isLoading, let packet, let snapshot = model.screen.portfolio,
              NSApp.windows.contains(where: { $0.isVisible }),
              let directory = Bundle.main.object(forInfoDictionaryKey: "SessionDirectory") as? String else { return }
        let format = ISO8601DateFormatter(); format.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let rendered = format.string(from: Date()); uiRenderedAt = rendered
        let receipt: [String: Any] = ["schema": "enguru.pilive.visible-frame/v1", "uiRenderedAt": rendered,
            "sourceReadAt": snapshot.sourceReadAt, "adapterBuiltAt": snapshot.adapterBuiltAt,
            "sourceRevision": snapshot.sourceRevision, "projectionDigest": snapshot.projectionDigest,
            "projectIds": snapshot.projects.map(\.projectId), "qualifiedCounters": snapshot.qualifiedCount,
            "windowVisible": true, "processId": ProcessInfo.processInfo.processIdentifier,
            "readerPacketBase64": packet.base64EncodedString(), "humanAcceptance": "NOT_ASSESSED", "productAcceptance": "HOLD", "verifiedFinish": "HOLD"]
        do {
            let raw = try JSONSerialization.data(withJSONObject: receipt, options: [.sortedKeys, .prettyPrinted])
            try raw.write(to: URL(fileURLWithPath: directory).appendingPathComponent("VISIBLE_FRAME.json"), options: .withoutOverwriting)
            recorded = true
        } catch { readerMessage = "HOLD · Görünür ekran makbuzu yazılamadı" }
    }
}

@main struct PiLiveApp: App {
    var body: some Scene {
        WindowGroup("ENGÜRÜ PiLive™") { CockpitRoot() }
            .defaultSize(width: 1200, height: 800)
            .commands {
                CommandGroup(after: .newItem) {
                    Button("Kaynağı yenile") { NotificationCenter.default.post(name: .init("PiLiveRefresh"), object: nil) }.keyboardShortcut("r", modifiers: .command)
                }
            }
    }
}
private struct CockpitRoot: View {
    @StateObject private var live = LiveController()
    var body: some View { Cockpit(live: live, model: live.model) }
}
private struct Cockpit: View {
    @ObservedObject var live: LiveController
    @ObservedObject var model: SwiftUIState
    @State private var search = ""
    @State private var selectedProject: ProjectRow?
    @FocusState private var focus: String?
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    private let tick = Timer.publish(every: 1, on: .main, in: .common).autoconnect()
    private let refresh = Timer.publish(every: 30, on: .main, in: .common).autoconnect()
    private let canvas = Color(red: 0.043, green: 0.082, blue: 0.075)
    private let surface = Color(red: 0.078, green: 0.141, blue: 0.122)
    private let jade = Color(red: 0.569, green: 0.831, blue: 0.678)
    private var title: String { switch model.selected { case .overview: return "Genel Durum"; case .now: return "Şimdi"; case .projects: return "Projeler" } }
    var body: some View {
        HStack(spacing: 0) {
            VStack(alignment: .leading, spacing: 20) {
                Label("PiLive™", systemImage: "leaf").font(.title2).foregroundStyle(jade)
                Text("Sessiz Orman Cockpit™").font(.caption).foregroundStyle(.secondary)
                ForEach(Screen.allCases, id: \.rawValue) { screen in
                    Button { model.navigate(screen) } label: {
                        Label(label(screen), systemImage: icon(screen)).frame(maxWidth: .infinity, alignment: .leading).frame(minHeight: 44)
                    }.buttonStyle(.bordered).keyboardShortcut(shortcut(screen), modifiers: .command)
                }
                Spacer()
                Text("Salt-okunur ekran adayı\nResmî kabul: HOLD").font(.caption)
                Text("G1.D04 · Görsel kabul bekliyor").font(.caption2).foregroundStyle(.secondary)
            }.padding(22).frame(width: 210).background(surface)
            VStack(alignment: .leading, spacing: 20) {
                HStack {
                    VStack(alignment: .leading) {
                        Text(title).font(.largeTitle).accessibilityAddTraits(.isHeader).focusable().focused($focus, equals: model.selected.rawValue + ".heading")
                        Text(model.screen.accessibilityAnnouncement).font(.callout)
                    }
                    Spacer()
                    if live.isLoading { ProgressView().accessibilityLabel("Kaynak okunuyor") }
                    Button { live.refresh() } label: { Label("Yenile", systemImage: "arrow.clockwise") }.frame(minWidth: 70, minHeight: 44)
                    Button { model.openEvidence() } label: { Label("Kanıt", systemImage: "checkmark.seal") }.frame(minWidth: 70, minHeight: 44).focused($focus, equals: "evidence.button")
                }
                Text("\(live.readerMessage) · \(model.screen.availability.rawValue) · Kaynak yaşı: \(age)").font(.callout).foregroundStyle(jade).accessibilityLabel("Kaynak durumu: \(model.screen.availability.rawValue), yaş \(age)")
                ScrollView {
                    VStack(alignment: .leading, spacing: 20) {
                        switch model.selected {
                        case .overview: overview
                        case .now: nowView
                        case .projects: projectList
                        }
                    }.frame(maxWidth: .infinity, alignment: .leading).padding(.bottom, 24)
                }
            }.padding(28)
        }
        .frame(minWidth: 980, minHeight: 640).background(canvas).foregroundStyle(Color(red: 0.933, green: 0.957, blue: 0.933)).preferredColorScheme(.dark)
        .task { live.refresh() }
        .onReceive(tick) { _ in live.tick(); live.recordVisibleFrame() }
        .onReceive(refresh) { _ in live.refresh() }
        .onReceive(NotificationCenter.default.publisher(for: .init("PiLiveRefresh"))) { _ in live.refresh() }
        .onChange(of: model.focusTarget) { focus = $0 }
        .sheet(isPresented: Binding(get: { model.evidenceIsOpen }, set: { if !$0 { model.escape() } })) {
            evidence.padding(28).frame(minWidth: 660, minHeight: 480).onExitCommand { model.escape() }
        }
        .sheet(item: $selectedProject) { row in projectDetail(row).padding(28).frame(minWidth: 600, minHeight: 360) }
    }
    private var age: String { model.screen.sourceAgeSeconds.map { "\(Int($0)) sn" } ?? "Bilinmiyor" }
    private func label(_ s: Screen) -> String { switch s { case .overview: return "Genel Durum"; case .now: return "Şimdi"; case .projects: return "Projeler" } }
    private func icon(_ s: Screen) -> String { switch s { case .overview: return "square.grid.2x2"; case .now: return "scope"; case .projects: return "folder" } }
    private func shortcut(_ s: Screen) -> KeyEquivalent { switch s { case .overview: return "1"; case .now: return "2"; case .projects: return "3" } }
    private func card<Content: View>(_ title: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 12) { Text(title).font(.headline).accessibilityAddTraits(.isHeader); content() }.padding(22).frame(maxWidth: .infinity, alignment: .leading).background(surface, in: RoundedRectangle(cornerRadius: 16))
    }
    private var overview: some View {
        VStack(spacing: 20) {
            HStack {
                card("Kaynakta gözlenen projeler") { Text(model.screen.projectCount.map { String($0) } ?? "N/A").font(.system(size: 36, weight: .semibold)) }
                card("Doğrulanmış teknik sayaç") { Text(model.screen.qualifiedCount.map { "\($0)/\(model.screen.projectCount ?? 0)" } ?? "N/A").font(.system(size: 36, weight: .semibold)) }
            }
            if let p02 = model.screen.p02 { card("PiLive P02 · Proje içi odak") { projectSummary(p02) } }
            ForEach(model.screen.portfolio?.projects.filter { ["progress-core", "visual-cockpit-premium-v1"].contains($0.key) } ?? []) { row in card(row.key) { projectSummary(row) } }
            if model.screen.portfolio == nil { card("Kaynak bekleniyor") { Text("HOLD · Doğrulanmış veri geldiğinde projeler burada görünür.") } }
        }
    }
    private var nowView: some View {
        VStack(spacing: 20) {
            card("Küresel aktif iş") { Text(model.screen.globalActiveSelection); Text("Yetkili canonical küresel odak kaynağı bekleniyor.").font(.callout) }
            if let p02 = model.screen.p02 { card("P02 · Proje içindeki sıradaki hareket") { projectSummary(p02); Text(p02.nextAction ?? "N/A") } }
        }
    }
    private var projectList: some View {
        VStack(alignment: .leading, spacing: 18) {
            TextField("Proje ara", text: $search).textFieldStyle(.roundedBorder).accessibilityLabel("Canonical proje adı veya kimliğiyle ara")
            ForEach(model.screen.projectGroups(search: search), id: \.name) { group in
                card("\(group.name) · \(group.countText)") {
                    ForEach(group.rows) { row in
                        Button { selectedProject = row } label: {
                            HStack { Text(row.key).lineLimit(nil); Spacer(); Text(row.counterText) }.frame(minHeight: 44).contentShape(Rectangle())
                        }.buttonStyle(.plain).accessibilityLabel(row.accessibilityLabel)
                    }
                }
            }
            if !search.isEmpty && model.screen.projectGroups(search: search).allSatisfy({ $0.rows.isEmpty }) { Text("Aramayla eşleşen proje bulunamadı.") }
        }
    }
    private func projectSummary(_ row: ProjectRow) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(row.counterText).font(.title2.monospacedDigit())
            Text("Aktif iş: \(row.activeItem ?? "N/A") · Aşama: \(row.activePackage ?? "N/A")")
            Text("Teknik finiş: \(row.finish) · Resmî kabul: \(row.officialAcceptance)")
            if row.status == "HOLD" { Text("HOLD · \(row.reason)").foregroundStyle(.yellow) }
        }.accessibilityElement(children: .combine)
    }
    private func projectDetail(_ row: ProjectRow) -> some View {
        VStack(alignment: .leading, spacing: 18) {
            Text(row.key).font(.title).accessibilityAddTraits(.isHeader)
            Text(row.projectId).textSelection(.enabled); projectSummary(row)
            Text("Sonraki hareket: \(row.nextAction ?? "N/A")")
            Button("Kapat") { selectedProject = nil }.keyboardShortcut(.cancelAction)
        }
    }
    private var evidence: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HStack { Text("Kanıt Çekmecesi").font(.title).accessibilityAddTraits(.isHeader); Spacer(); Button("Kapat") { model.escape() }.keyboardShortcut(.cancelAction) }
                Text("Kaynak revision: \(model.screen.sourceRevision ?? "Bilinmiyor")")
                Text("Projection digest: \(model.screen.projectionDigest ?? "Bilinmiyor")")
                Text("Kaynak okuma: \(model.screen.portfolio?.sourceReadAt ?? "Bilinmiyor")")
                Text("Model oluşturma: \(model.screen.portfolio?.adapterBuiltAt ?? "Bilinmiyor")")
                Text("Görünür frame: \(live.uiRenderedAt ?? "Bilinmiyor")")
                Text("Kaynak yaşı: \(age) · \(model.screen.availability.rawValue)")
                Text("Bu ekran gözlemi kullanıcı estetik veya resmî P02 kabulü üretmez.")
                Text("Tarihsel V3.1 imza doğrulaması: HOLD · build kökeni ayrı kapıda")
                Text("Visual Cockpit kaynak olgusu: \(live.verificationNotes["visual-cockpit-premium-v1"] ?? "N/A")")
                ForEach((model.screen.portfolio?.sourcePins ?? [:]).keys.sorted(), id: \.self) { key in Text("\(key)\n\(model.screen.portfolio?.sourcePins[key] ?? "")").font(.caption.monospaced()).textSelection(.enabled) }
            }
        }
    }
}
