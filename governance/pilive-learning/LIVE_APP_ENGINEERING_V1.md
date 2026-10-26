# PiLive — gerçek kaynaklı read-only SwiftUI ekran adayı

Korunan baseline PR241 bcec47379e936ee53683f47cfb89c03bca57967b; native 218, 15 kimlik, 14 qualified, 48 kaynak/8 Core pini. Mevcut Core ve VM01–VM06 yeniden kurulmadı. UI01 packaged-reader SHA denetimi; UI02 collector→wire→SourceIdentity→MainActor state→gerçek view; UI03 sourceClassification aktarımı; UI04 dört görünüm; UI05 ayrı native candidate build/signing/frame devri uygulanır. Test/CI ve saha hükümleri ayrı değerlendirilir.

Reader her çağrıda kaynak manifestini doğrular; -I -B -S, nofollow/bounded okuma ve mevcut Core pin çerçevesini kullanır. Cmd-R ve 30 saniyelik yenileme gerçek kaynak okur. Kaynak kopmasında HOLD ve N/A; son kayıt güncel diye sunulmaz. Sayısal JSON yeniden serileştirmesinin byte kimliğini bozmaması için frame makbuzu original reader packet byte'larını base64 taşır. Public GitHub'a gerçek Mac ham makbuzu aktarılmaz.

Registry productionArea/facet metadata'sı varsa taşınır; yoksa beş başlık N/A ve görünür unclassified. Key/projectId ayrı; ticari facet ikinci sayaç üretmez. Küresel odak kanıtı yoksa Şimdi HOLD; P02 proje içi odaktır.

Görsel, mevcut UX sözleşmesinin işlevsel aday uygulamasıdır; G1.D04 owner final estetik kabulü HOLD. Cmd-1/2/3, Cmd-R, Escape, sheet ve metinsel durum adları mevcut; gerçek VoiceOver/focus/AA/Dynamic Type/Reduce Motion saha kabulü açık. OSi bütünsel mimarisi ve ana Cockpit modalı backlog HOLD.

Native --build-and-open yalnız benzersiz AudiV13 session'ında kaynakları korur, gerçek Mac Swift test/build komutlarını/toolchain'i kaydeder, ayrı app'i ad-hoc imzalar ve strict verify yapar. /Applications kurulumu veya mevcut app değişimi yok. Rollback aday pencereyi kapatıp mevcut app'i kullanmaktır; kaynak/makbuzlar korunur. Yeni servis/API/anahtar/canonical writer yok.

Görünür NSWindow ve kaynak doğrulanmış modelden sonra UI frame event'i kaynak/model/render zamanlarını ve proje/digest bağını kaydeder. Handoff bunu tekrar doğrular; AudiV13 original + SHA eş Desktop kopya üretir. PASS_SOURCE_TO_VISIBLE_FRAME_ONLY bağımsız kullanıcı kabulü değildir. App'in kendi görünür frame gözlemi, insan görev/ekran onayından ayrı tutulur.

U01 source/recipe/toolchain/signing/binary zinciri native makbuzda; U02–U06/U09/U10 view bağlantısı native parity bekler. U07 G1.D04, U08 gerçek erişilebilirlik, U11 100 proje/30 açılış/100 yenileme, U12 bağımsız GUI ve ayrı resmî P02 12/12+4/4+7/7+G3+HT+Verified Finish HOLD.

Zülfikar PR246 4780d96ccb16ca4a922846ab48918262c7845f47; engine SHA aae470e41a59de981c0c34b81a25ed094f52db6eed8dc0d101124984dd903230. DÖM LOCAL_DISPOSABLE_PROOF kapsamı korunur; üretim yetkisi doğurmaz. Mevcut Work döngüsü kaynak/kimlik, hata/erişilebilirlik ve drift/geri dönüş turlarını yürütür. Sekiz kapı LIVE_APP_GATE_HANDOFF_V1.json içinde; özgün şartlar tam kapanmadan 100 veya aşama PASS verilmez.
