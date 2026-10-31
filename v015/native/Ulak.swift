import SwiftUI
import AppKit

@MainActor final class Bridge: ObservableObject {
    @Published var input = ""
    @Published var status = "IDLE"
    @Published var percent = 0.0
    @Published var remaining = 100.0
    @Published var donecheck = "HOLD"
    @Published var message = "Bir görev yazın. Desteklenen ilk pilot: unique_jobs sıra koruma onarımı."
    @Published var transcript: [String] = []
    @Published var busy = false
    @Published var queue = "Kuyruk boş"
    @Published var evidence = ""
    @Published var source = ""
    private var activity: NSObjectProtocol?
    private var config: [String:String] = [:]

    init() {
        if let r = Bundle.main.resourceURL,
           let data = try? Data(contentsOf:r.appendingPathComponent("runtime.json")),
           let v = try? JSONSerialization.jsonObject(with:data) as? [String:String] { config = v }
        request("snapshot")
    }

    func request(_ action: String) {
        let primary = action != "pause" && action != "resume"
        if busy && primary { return }
        guard let python = config["python"], let profile = config["profile"],
              let root = Bundle.main.resourceURL?.appendingPathComponent("Product") else {
            status = "HOLD"; message = "Uygulama yapılandırması doğrulanmalı."; return
        }
        var payload: [String:Any] = ["action":action,"profile":profile]
        if action == "run" {
            let text = input.trimmingCharacters(in:.whitespacesAndNewlines)
            guard !text.isEmpty else { return }
            payload["text"] = text; payload["command_id"] = UUID().uuidString
            transcript.append("Siz · " + text); input = ""
        }
        guard let bytes = try? JSONSerialization.data(withJSONObject:payload) else { return }
        if primary { busy = true }
        message = action == "run" ? "İstek çekirdeğe iletiliyor; sonuç makbuzla bildirilecek." : "Kaynak durum okunuyor."
        if action == "run" {
            activity = ProcessInfo.processInfo.beginActivity(options:[.idleSystemSleepDisabled,.userInitiated],reason:"ENGÜRÜ yetkili aktif görevi")
        }
        DispatchQueue.global(qos:.userInitiated).async {
            let process = Process(); let incoming = Pipe(); let outgoing = Pipe(); let errors = Pipe()
            process.executableURL = URL(fileURLWithPath:python)
            process.arguments = ["-I","-B",root.appendingPathComponent("cli.py").path]
            process.standardInput = incoming; process.standardOutput = outgoing; process.standardError = errors
            do {
                try process.run()
                incoming.fileHandleForWriting.write(bytes); try incoming.fileHandleForWriting.close()
                let data = outgoing.fileHandleForReading.readDataToEndOfFile()
                let err = errors.fileHandleForReading.readDataToEndOfFile()
                process.waitUntilExit()
                let result = (try? JSONSerialization.jsonObject(with:data)) as? [String:Any]
                DispatchQueue.main.async { self.receive(result, fallback:String(data:err,encoding:.utf8) ?? "Makbuz okunamadı.", primary:primary) }
            } catch {
                DispatchQueue.main.async { self.receive(nil,fallback:error.localizedDescription,primary:primary) }
            }
        }
    }

    private func receive(_ result: [String:Any]?, fallback: String, primary: Bool) {
        defer {
            if primary {
                busy = false
                if let token = activity { ProcessInfo.processInfo.endActivity(token); activity = nil }
            }
        }
        guard let result = result, result["ok"] as? Bool == true,
              let p = result["projection"] as? [String:Any] else {
            status = "HOLD"; donecheck = "HOLD"
            message = result?["reason"] as? String ?? fallback
            transcript.append("Ulak · " + message); return
        }
        status = p["state"] as? String ?? "HOLD"
        if let value = p["completion_percent"] as? Double, (0...100).contains(value) { percent = value } else { percent = 0 }
        remaining = p["remaining_percent"] as? Double ?? 100
        donecheck = p["donecheck"] as? String ?? "HOLD"
        evidence = p["evidence"] as? String ?? ""
        source = p["source_sha256"] as? String ?? ""
        let items = p["queue"] as? [[String:Any]] ?? []
        queue = items.map { "\($0["command"] ?? "?") · \($0["state"] ?? "HOLD")" }.joined(separator:"\n")
        message = p["message"] as? String ?? "Son olay: \(p["last_verified_event"] ?? "Yok") · Ürün kabulü HOLD"
        transcript.append("Ulak · \(status) · \(message)")
    }
}

@MainActor struct UlakView: View {
    @StateObject private var bridge = Bridge()
    @State private var showQueue = false
    @State private var showEvidence = false
    @State private var showReference = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    private let green = Color(red:0.08,green:0.88,blue:0.55)
    var body: some View {
        VStack(spacing:20) {
            HStack {
                Image(systemName:"leaf.circle").font(.system(size:34)).foregroundStyle(green)
                VStack(alignment:.leading) {
                    Text("ENGÜRÜ").font(.title2.weight(.semibold))
                    Text("Üçlü Yerel Zekâ™ · Ulak V015").font(.caption).foregroundStyle(.secondary)
                }
                Spacer()
                Button("V0.6 referansı") { showReference = true }
                Text("Yerel Qwen3 14B").font(.caption)
            }
            HStack(spacing:28) {
                ZStack {
                    Circle().stroke(green.opacity(0.15),lineWidth:9)
                    Circle().trim(from:0,to:bridge.percent/100).stroke(green,style:StrokeStyle(lineWidth:9,lineCap:.round)).rotationEffect(.degrees(-90))
                    Text(bridge.percent,format:.number.precision(.fractionLength(0...2))).font(.largeTitle.bold()) + Text("%")
                }.frame(width:100,height:100).accessibilityLabel("Kanıtlı ilerleme yüzde \(bridge.percent)")
                VStack(alignment:.leading,spacing:10) {
                    Text("Aktif görevin kanıtlı sonucu").font(.headline)
                    Text("\(bridge.status) · Kalan yüzde \(bridge.remaining,specifier:"%.2f")")
                    Text("DoneCheck™ · \(bridge.donecheck)").foregroundStyle(green)
                    Text("Ürün / Mac saha kabulü: HOLD").font(.caption).foregroundStyle(.secondary)
                }
                Spacer()
            }.padding(22).background(green.opacity(0.06),in:RoundedRectangle(cornerRadius:20))
            HStack {
                Label("Yönetici · plan önerir",systemImage:"point.3.connected.trianglepath.dotted")
                Spacer()
                Label("İcracı · araç önerir",systemImage:"gearshape")
            }.font(.subheadline).foregroundStyle(.secondary)
            ScrollView {
                VStack(alignment:.leading,spacing:14) {
                    Text(bridge.message).foregroundStyle(.secondary)
                    ForEach(Array(bridge.transcript.enumerated()),id:\.offset) { _, line in
                        Text(line).textSelection(.enabled).frame(maxWidth:.infinity,alignment:.leading)
                            .padding(14).background(.white.opacity(0.04),in:RoundedRectangle(cornerRadius:12))
                    }
                }.frame(maxWidth:.infinity,alignment:.leading)
            }
            HStack {
                Button("Kuyruk") { showQueue = true }
                Button("Kanıtları Gör") { showEvidence = true }
                Spacer()
                Button("Duraklat") { bridge.request("pause") }
                Button("Devam Et") { bridge.request("resume") }
                Button("Güvenli Durdur / Uzlaştır") { bridge.request("recover") }.disabled(bridge.busy)
            }.font(.caption)
            HStack {
                TextField("Bir görev yazın…",text:$bridge.input).textFieldStyle(.roundedBorder)
                    .onSubmit { bridge.request("run") }.disabled(bridge.busy)
                    .accessibilityLabel("Ulak görev emri")
                Button { bridge.request("run") } label: { Image(systemName:"arrow.up.circle.fill").font(.title) }
                    .buttonStyle(.plain).foregroundStyle(green).disabled(bridge.busy)
                    .accessibilityLabel("Görevi çekirdeğe ilet")
            }
            HStack { Text("İki zekâ · Bir ortak çekirdek · Bir Ulak"); Spacer(); Button("Durumu yenile") { bridge.request("snapshot") }.disabled(bridge.busy) }
                .font(.caption2).foregroundStyle(.secondary)
        }
        .padding(28).frame(minWidth:760,minHeight:680)
        .background(Color(red:0.015,green:0.055,blue:0.045))
        .preferredColorScheme(.dark)
        .animation(reduceMotion ? nil : .easeOut(duration:0.18),value:bridge.percent)
        .sheet(isPresented:$showQueue) { sheet("Kuyruk",bridge.queue.isEmpty ? "Kuyruk boş" : bridge.queue) }
        .sheet(isPresented:$showEvidence) { sheet("Kanıt ve DoneCheck™",bridge.donecheck + "\n" + bridge.source + "\n" + bridge.evidence) }
        .sheet(isPresented:$showReference) {
            VStack {
                Text("V0.6 kabul edilen görsel karakter · Tasarım referansı, canlı durum değildir")
                if let url=Bundle.main.resourceURL?.appendingPathComponent("Product/design/V06_OWNER_DESKTOP.png"),let image=NSImage(contentsOf:url) {
                    Image(nsImage:image).resizable().scaledToFit()
                }
                Button("Kapat") { showReference=false }
            }.padding().frame(width:900,height:700)
        }
    }
    private func sheet(_ title:String,_ text:String) -> some View {
        VStack(alignment:.leading,spacing:20) {
            Text(title).font(.title2)
            ScrollView { Text(text).textSelection(.enabled).frame(maxWidth:.infinity,alignment:.leading) }
            Button("Kapat") { showQueue=false; showEvidence=false }
        }.padding(28).frame(width:600,height:350)
    }
}

@main @MainActor struct UlakApp: App {
    var body: some Scene { WindowGroup("ENGÜRÜ Ulak V015") { UlakView() } }
}
