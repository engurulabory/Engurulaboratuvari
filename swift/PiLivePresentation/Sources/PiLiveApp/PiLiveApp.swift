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
    private var lastRenderedSourceReadAt: String?
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
        guard !isLoading, let packet, let snapshot = model.screen.portfolio,
              lastRenderedSourceReadAt != snapshot.sourceReadAt,
              NSApp.windows.contains(where: { $0.isVisible && !$0.isMiniaturized && $0.title.contains("PiLive") }),
              let directory = Bundle.main.object(forInfoDictionaryKey: "SessionDirectory") as? String else { return }
        let format = ISO8601DateFormatter(); format.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let rendered = format.string(from: Date()); uiRenderedAt = rendered; lastRenderedSourceReadAt = snapshot.sourceReadAt
        if recorded { return }
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
    func fieldEvent(task: String, journeyId: String, projectId: String, lock: FieldSourceLock) throws -> [String: Any] {
        guard !isLoading, model.screen.availability == .fresh, let p = model.screen.portfolio,
              let row = p.projects.first(where: { $0.projectId == projectId }), let packet,
              lastRenderedSourceReadAt == p.sourceReadAt, let rendered = uiRenderedAt else { throw PresentationHold.invalidSource }
        try lock.requireSameSource(p)
        return try FieldCapture.event(task: task, journeyId: journeyId, packet: packet, portfolio: p,
            row: row, renderedAt: rendered, selectedDigest: lock.digest)
    }

}

@main struct PiLiveApp: App {
    var body: some Scene {
        WindowGroup("ENGÜRÜ PiLive™ · Saha V2") { CockpitRoot() }
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
    @State private var selectedDigest: String?
    @State private var projectOpenerId: String?
    @State private var scopedEvidence = false
    @State private var fieldId: String?
    @State private var fieldLock: FieldSourceLock?
    @State private var fieldStep = 0
    @State private var fieldEvents: [[String: Any]] = []
    @State private var fieldMessage = ""
    @State private var fieldStarted: Date?
    @State private var evidenceClosedWithEscape = false
    @State private var restoredFocusTarget: String?
    @State private var fieldCompleted = false
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
                    Button("Saha görevi") { startField() }.frame(minHeight: 44).disabled(live.isLoading || model.screen.portfolio == nil || fieldId != nil)
                    if live.isLoading { ProgressView().accessibilityLabel("Kaynak okunuyor") }
                    Button { live.refresh() } label: { Label("Yenile", systemImage: "arrow.clockwise") }.frame(minWidth: 70, minHeight: 44)
                    Button { model.openEvidence() } label: { Label("Kanıt", systemImage: "checkmark.seal") }.frame(minWidth: 70, minHeight: 44).focused($focus, equals: "evidence.button")
                }
                Text("\(live.readerMessage) · \(model.screen.availability.rawValue) · Kaynak yaşı: \(age)").font(.callout).foregroundStyle(jade).accessibilityLabel("Kaynak durumu: \(model.screen.availability.rawValue), yaş \(age)")
                if fieldId != nil { fieldPanel }
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
        .onChange(of: focus) { target in
            if evidenceClosedWithEscape, target == "project." + (projectOpenerId ?? "UNKNOWN") { restoredFocusTarget = target }
        }
        .sheet(isPresented: Binding(get: { model.evidenceIsOpen }, set: { if !$0 { model.escape() } })) {
            evidence.padding(28).frame(minWidth: 660, minHeight: 480).onExitCommand { model.escape() }
        }
        .sheet(item: $selectedProject, onDismiss: { scopedEvidence = false; focus = "project." + (projectOpenerId ?? "UNKNOWN") }) { row in
            Group { if scopedEvidence { evidence } else { projectDetail(row) } }
                .padding(28).frame(minWidth: 760, minHeight: 620)
                .onExitCommand { closeScopedEvidence(escape: true) }
        }
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
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 120))], spacing: 10) {
                ForEach(Array(model.screen.projectGroups(search: search).prefix(5)), id: \.name) { group in
                    VStack(alignment: .leading) { Text(group.name).font(.headline); Text(group.countText).font(.callout) }
                        .frame(maxWidth: .infinity, minHeight: 52, alignment: .leading).padding(12).background(surface, in: RoundedRectangle(cornerRadius: 10))
                }
            }
            ForEach(model.screen.projectGroups(search: search).filter { !$0.rows.isEmpty || $0.name == "Kaynak eşlemesi bekleniyor" }, id: \.name) { group in
                card("\(group.name) · \(group.countText)") {
                    ForEach(group.rows) { row in
                        Button { projectOpenerId = row.projectId; selectedDigest = model.screen.projectionDigest; scopedEvidence = false; selectedProject = row } label: {
                            HStack { Text(row.key).lineLimit(nil); Spacer(); Text(row.counterText) }.frame(minHeight: 44).contentShape(Rectangle())
                        }.buttonStyle(.plain).accessibilityLabel(row.accessibilityLabel).focused($focus, equals: "project." + row.projectId)
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
    private func projectDetail(_ original: ProjectRow) -> some View {
        VStack(alignment: .leading, spacing: 18) {
            if let p = model.screen.portfolio, p.projectionDigest == selectedDigest,
               let row = p.projects.first(where: { $0.projectId == original.projectId }) {
                Text(row.key).font(.title).accessibilityAddTraits(.isHeader)
                Text(row.projectId).textSelection(.enabled); projectSummary(row)
                if !fieldMessage.isEmpty { Text(fieldMessage).foregroundStyle(.yellow) }
                Text("Sonraki hareket: \(row.nextAction ?? "N/A")")
                if fieldId != nil && fieldStep == 1 && row.projectId == "ENGURU_PROGRESS_CORE" {
                    Button("Proje görevini doğrula") { captureField(task: "FJ.PROJECTS", projectId: row.projectId) }.frame(minHeight: 44).disabled(live.isLoading)
                }
                Button("Bu projenin kanıtı") { scopedEvidence = true }.frame(minHeight: 44)
                    .accessibilityLabel("\(row.key) projesinin kaynak kanıtını aç")
            } else { Text("HOLD · Kaynak değişti. Ayrıntıyı kapatıp projeyi yeniden seç.") }
            Button("Kapat") { closeScopedEvidence(escape: false) }.keyboardShortcut(.cancelAction)
        }
    }
    private func closeScopedEvidence(escape: Bool) {
        if scopedEvidence && escape && fieldStep == 3 { evidenceClosedWithEscape = true }
        selectedProject = nil; scopedEvidence = false
    }
    private var evidence: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                HStack { Text("Kanıt Çekmecesi").font(.title).accessibilityAddTraits(.isHeader); Spacer(); Button("Kapat") { if scopedEvidence { closeScopedEvidence(escape: false) } else { model.escape() } } }
                if scopedEvidence, let selectedProject {
                    if let context = try? model.screen.portfolio?.projectEvidence(projectId: selectedProject.projectId, selectedDigest: selectedDigest ?? "") {
                        Text("Proje: \(context.row.projectId)").font(.headline).textSelection(.enabled)
                        if !fieldMessage.isEmpty { Text(fieldMessage).foregroundStyle(.yellow) }
                        projectSummary(context.row)
                        ForEach(context.pins.keys.sorted(), id: \.self) { path in Text("\(path)\n\(context.pins[path] ?? "")").font(.callout.monospaced()).textSelection(.enabled) }
                        Text(live.verificationNotes[context.row.key] ?? "N/A")
                        if fieldId != nil && fieldStep == 2 && context.row.projectId == "ENGURU_PROGRESS_CORE" {
                            Button("Kanıt görevini doğrula") { captureField(task: "FJ.EVIDENCE", projectId: context.row.projectId) }.frame(minHeight: 44).disabled(live.isLoading)
                        }
                        if fieldStep == 3 { Text("Şimdi Escape tuşuyla kapat; sonra ana ekranda kaydı tamamla.") }
                    } else { Text("HOLD · Proje/kaynak eşliği değişti; kanıt yeniden seçilmeli.") }
                }
                Text("Kaynak revision: \(model.screen.sourceRevision ?? "Bilinmiyor")")
                Text("Projection digest: \(model.screen.projectionDigest ?? "Bilinmiyor")")
                Text("Kaynak okuma: \(model.screen.portfolio?.sourceReadAt ?? "Bilinmiyor")")
                Text("Model oluşturma: \(model.screen.portfolio?.adapterBuiltAt ?? "Bilinmiyor")")
                Text("Görünür frame: \(live.uiRenderedAt ?? "Bilinmiyor")")
                Text("Kaynak yaşı: \(age) · \(model.screen.availability.rawValue)")
                Text("Bu ekran gözlemi kullanıcı estetik veya resmî P02 kabulü üretmez.")
                Text("Tarihsel V3.1 imza doğrulaması: HOLD · build kökeni ayrı kapıda")
                if !scopedEvidence { Text("Visual Cockpit kaynak olgusu: \(live.verificationNotes["visual-cockpit-premium-v1"] ?? "N/A")") }
                if !scopedEvidence { ForEach((model.screen.portfolio?.sourcePins ?? [:]).keys.sorted(), id: \.self) { key in Text("\(key)\n\(model.screen.portfolio?.sourcePins[key] ?? "")").font(.caption.monospaced()).textSelection(.enabled) } }
            }
        }
    }
    private var fieldPanel: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Üç ekran saha görevi · \(fieldStep)/3").font(.headline)
            Text(fieldStep == 0 ? "Şimdi: P02 0/12, aktif P02.S01.01 ve küresel HOLD durumunu oku." : fieldStep == 1 ? "Projeler: progress-core ara, seç, 44/44 ve finiş HOLD durumunu doğrula." : fieldStep == 2 ? "Seçili projenin Bu projenin kanıtı düğmesine bas; ENGURU_PROGRESS_CORE ve kendi State/Worklist SHA'larını doğrula." : "Escape ile kanıtı kapat. Odak proje satırına döndüyse kaydı tamamla.")
            if !fieldMessage.isEmpty { Text(fieldMessage).foregroundStyle(.yellow) }
            if fieldStep == 0 { Button("Şimdi görevini doğrula") { captureField(task: "FJ.NOW", projectId: "ENGURU_PLIVE_P02_USER_SCREEN") }.disabled(live.isLoading) }
            Button("Saha görevini yeniden başlat") { restartField() }.disabled(fieldCompleted)
            if fieldStep == 3 { Button("Odak döndü · Kaydı tamamla") { finishField() }.disabled(!evidenceClosedWithEscape || fieldCompleted) }
        }.padding(12).background(surface, in: RoundedRectangle(cornerRadius: 10))
    }
    private func restartField() {
        if let id = fieldId, let dir = Bundle.main.object(forInfoDictionaryKey: "SessionDirectory") as? String {
            let partial: [String: Any] = ["journeyId": id, "events": fieldEvents, "state": "HOLD_INTERRUPTED_RESTART", "verifiedFinish": "HOLD"]
            if let raw = try? JSONSerialization.data(withJSONObject: partial, options: [.sortedKeys]) {
                try? raw.write(to: URL(fileURLWithPath: dir).appendingPathComponent("FIELD_PARTIAL_" + UUID().uuidString + ".json"), options: .withoutOverwriting)
            }
        }
        fieldId = nil; evidenceClosedWithEscape = false; restoredFocusTarget = nil; startField()
    }
    private func startField() {
        guard let p = model.screen.portfolio, model.screen.availability == .fresh else { return }
        fieldId = "PILIVE.FIELD.3SCREEN." + UUID().uuidString; fieldLock = FieldSourceLock(p)
        fieldStarted = Date(); fieldEvents = []; fieldStep = 0; fieldMessage = ""; model.navigate(.now)
    }
    private func captureField(task: String, projectId: String) {
        guard let id = fieldId, let lock = fieldLock else { return }
        do {
            let event = try live.fieldEvent(task: task, journeyId: id, projectId: projectId, lock: lock)
            fieldEvents.append(event); fieldStep += 1; fieldMessage = ""
            if fieldStep == 1 { model.navigate(.projects) }
        } catch { fieldMessage = "HOLD · Kaynak/ekran eşliği veya tazelik bekleniyor; yenileme bitince tekrar dene." }
    }
    private func finishField() {
        guard !fieldCompleted, let id = fieldId, fieldEvents.count == 3, evidenceClosedWithEscape,
              let dir = Bundle.main.object(forInfoDictionaryKey: "SessionDirectory") as? String,
              let start = fieldStarted else { return }
        let value: [String: Any] = ["schema": "enguru.pilive.field-journey/v1", "journeyId": id,
            "events": fieldEvents, "elapsedSeconds": Date().timeIntervalSince(start),
            "escapeObserved": true, "focusReturn": "USER_CONFIRMED_PROJECT_ROW",
            "focusBindingTarget": restoredFocusTarget ?? focus ?? "UNKNOWN", "state": "CAPTURE_REQUIRES_INDEPENDENT_REVIEW",
            "productAcceptance": "HOLD", "verifiedFinish": "HOLD"]
        do {
            try JSONSerialization.data(withJSONObject: value, options: [.sortedKeys, .prettyPrinted])
                .write(to: URL(fileURLWithPath: dir).appendingPathComponent("FIELD_JOURNEY.json"), options: .withoutOverwriting)
            fieldCompleted = true
            fieldMessage = "Görev kaydı korundu. Terminal çıktısındaki saha ZIP'ini Work'e yükle."
        } catch { fieldMessage = "HOLD · Saha kaydı yazılamadı." }
    }

}
