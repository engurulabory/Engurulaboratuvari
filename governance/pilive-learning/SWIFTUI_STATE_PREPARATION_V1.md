# PiLive — kaynak doğrulamalı SwiftUI durum katmanı V1

## Yetkili giriş ve kapsam

UX PR #245 @ `c780002c66ad916d2c3c0a587085a32e2f0b68a8` kaynakları:
`governance/plive/SESSIZ_ORMAN_COCKPIT_UX_CONTRACT_V1.md` (Git blob `ca9e74b9b871ed3f3d628e7c85f2e708cbe4f955`) ve `SESSIZ_ORMAN_ZULFIKAR_V13_SCORECARD_V2.json` (Git blob `2b49e9adf762a601957b50a4176aa1d350721df4`). 11 boyut / 110 şart / her boyut hedef 100 korunur. Bu hazırlık kalite puanlarını veya nihai kabulü yükselten otomatik hüküm üretmez. G1.D03-V yönetimde; G1.D04, gerçek görsel SwiftUI ve Mac kurulumu HOLD.

## Tamamlanan mühendislik işleri

- VM01: mevcut Python portföyünden kayıpsız `screen-wire/v1`. Yeni Core veya sayaç yok. Python canonical content byte'ları aynen taşınır; Swift farklı float/Unicode JSON serileştirmesiyle yeni digest üretmez.
- VM02: Swift Foundation/CryptoKit decoder; caller'ın verified reader'dan aldığı revision, pins, projection digest ve **tam wire SHA** karşılaştırılır. Timestamp digest dışında olduğundan tam wire SHA tazelik metadata'sını da bağlar. TrustIdentity'yi gelen wire'dan türetmek üretimde yasaktır; test oracle'ı yalnız test fixture'ında kullanılır. SHA kendi başına kaynak otoritesi değildir. Gerçek reader→wire→SwiftUI ingestion kendi native kapısında açık.
- VM03: MainActor tek immutable ScreenState yayını; request generation eski completion'ı reddeder. Kaynak hatasında mevcut model HOLD/N/A; offline cache yalnız açık son bilinen kayıt/yaş ile görünür. Tick stale geçişini yeniden değerlendirir. Kaynak rollback yalnız yeni request ve bağımsız doğrulanmış trust identity ile kabul edilir.
- VM04: Genel Durum gerçek proje ve qualified sayaç kapsamını taşır; genel yüzde veya küresel öncelik icat etmez. Şimdi GLOBAL_PRIORITY_NOT_PROVEN; P02 proje içi kartı ayrı. Projeler beş sabit başlık/N/A + kaynak eşlemesi bekleyen tüm satırlar; productionArea/facet mevcut portföyde yok. Heuristik sınıflama ve ikinci sayaç yok. Kanıt state'inde revision/digest/48 pin ve gözlem/model zamanları korunur; gerçek uiRenderedAt null kalır.
- VM05: ObservableObject/@Published SwiftUI köprüsü, sayfa/head focus intent, kanıt tek açma eylemi, Escape/odak dönüş intent'i, açık durum metni ve erişilebilir satır adları. Gerçek focus trap, AccessibilityFocusState/VoiceOver duyurusu, Dynamic Type, AA ve Reduce Motion uygulaması nihai view/native testinde açık.
- VM06: üç karşıt tur: (1) kimlik/pin/digest/sayaç, (2) hata/klavye/erişilebilir ad/boş arama, (3) source drift/obsolete request/offline cache/stale/trusted readback. Swift macOS CI 12 test ×3; Python mevcut221+3 wire testi =224 ×3 hedefli gerçek çalıştırma. Sonuç CI'den ayrı doğrulanır; plan kendi başına PASS değildir.

## Saha ve bağımsızlık sınırı

Native veri fixture'ı 26 Ekim makbuzu SHA `0b5aae55274fd0d8f5bf06c4aff4b7ed44595436655530a587b2703743f04fd5` üzerinden gizlilik incelemesiyle türetildi. 15 kimlik, 14 qualified, Visual Cockpit N/A, P02 0/12 ve Core 44/44 finish HOLD korunur. Wire SHA `99c73ac55309cc961aae90de7a6aefeb07dae59b8bcd739288fdf6749bcfa052`. Statik fixture canlı telemetri değildir.

GitHub macos-15 compile/test gerçek Swift/SwiftUI state kodunu sınar; kullanıcının OSi cihazı veya gerçek pencere testi değildir. Yerel Work ortamında Swift yok. Önceki kas CI explicit test listesi yeni reviewed-native testini içermiyordu; bu fark kapatıldı ve hem native review hem wire testleri eklendi. Önceki 5/5 CI hükmü kendi kapsamındadır; yeni test kapsaması bu HEAD ile doğrulanır.

## Özgün kabul ID'leri

U01 revision/pin/wire bağı hazırlığı; tarihsel build/signing açık. U02 tek Core→transport→state; native reader/view parity açık. U03 qualified ve HOLD/N/A ayrımı; gerçek ekran açık. U04 kaynaklı proje odağı; global canonical priority ve gerçek conflict/cycle yüzeyi açık. U05 beş başlık/unclassified korunumu; source facet eşliği açık. U06 dört view state hazırlığı; final layout açık. U07 G1.D04 açık. U08 text labels/focus intent testleri; native VoiceOver/AA/Dynamic Type/Reduce Motion açık. U09 model zamanları ve cache yaşı; native render zamanı açık. U10 digest/kimlik/kesinti/recovery state testleri; native yaşam döngüsü açık. U11 performans/Finder/crash saha testleri açık. U12 exact code/fixture/CI; bağımsız GUI ve owner kabulü açık.

11 boyut (AESTHETIC, ACCESS, ACCESSIBILITY, GOVERNANCE, TECHNICAL, E2E, GENERAL, PROCESS_SIMPLE, SURFACE_SIMPLE, USABILITY, SERVICE) kendi 10 şartını korur. Bu tur GOVERNANCE/TECHNICAL/PROCESS_SIMPLE ve ACCESS/ACCESSIBILITY/USABILITY alt hazırlıklarına test kanıtı sağlar. SERVICE ve diğer boyutların nihai 100/100 hükmü HOLD; yeni estetik skor verilmez.

Core/canonical writer/kas/kurulu app/main korunur. OSi bütünsel mimari PR #244 backlog HOLD. P02 0/12 + 0/4 DoneCheck ve ayrı saha/G3/Human Threshold/Verified Finish açık. Yeni Terminal hareketi gerekmez.
