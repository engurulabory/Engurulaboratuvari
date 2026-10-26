# ENGÜRÜ Ar-Ge — BLOK 01 Birleşik Giriş ve Çıkış Denetimi

STATE: BLOCK01_GITHUB_PREPARATION / BLOCK_FINISH_HOLD
SOURCE: Issue #205, V4.6 six-block plan, V4.11 four counters, V4.12 entry/exit simulation
SCOPE: A01–A09 = nine **Ar-Ge architecture** tasks. Mac Engineer V07 A-ID'leri farklı kayıttır.

## Toplu iş matrisi — aynı bloğun dokuz kontrolü

| ID | Blok kapsamındaki hazırlık teması | Kanıt sınırı | Resmî |
|---|---|---|---|
| A01 | 18 vaka, altı alan, kaynak ve senaryo envanteri | V4.5 yapısal hazırlık, özgün müşteri kanıtı açık | HOLD |
| A02 | 234 benzersiz K01–K13 hücre ve kaynak izlenebilirliği | V4.5 yapısal hazırlık, bağımsız E5 açık | HOLD |
| A03 | K01–K13/E5 canonical kabul sözleşmesi, owner/issuer, reviewer, yetki | PR #207 özel CI PASS, owner imzalı grant ve kaynak SHA açık | HOLD |
| A04 | Upstream kanıt denetimi: 18 vakanın sürüm/tarih/lisans/CVE/SBOM durumu | Erişilebilir upstream kanıt ve Kâşifi gerçek canonical kimlik doğrulaması açık | HOLD |
| A05 | Müşteri dağıtım doğrulama: 18 kurulu sürüm ve iddia sınıfı | 18 gerçek deployment pin ve müşteri teyidi açık; UNKNOWN ayrı | HOLD |
| A06 | E5 bağımsız kabul: 18 doğrulama kararı veya yetkili kapsam kararı | 18 vakanın gerçek bağımsız E5 doğrulaması açık | HOLD |
| A07 | G01 dış etki, G02 ilişkisel yetki, G03 zaman doğruluğu mimari garantileri | saldırı girdisi + beklenen orakel + gereksinim/test ayrımı; gerçek saha testleri açık | HOLD |
| A08 | 18 vaka K12: 5 yıllık TCO, açık varsayımlar ve ±20% duyarlılık | kaynaklı gerçek müşteri/ENGÜRÜ maliyet ölçümü ve bağımsız review açık | HOLD |
| A09 | Birleşik Mimarlık Ar-Ge kanıt dosyası ve AR→GE devri | tam 9 kontrol kabulü ve reviewer açık | HOLD |

Temalar V4.2 KSF aday eşleştirmesi ve #205 Ar-Ge kapsamından hazırlanmıştır. Ayrıntılı task-specific canonical tanımlar OWNER doğrulamasına bağlıdır. İş ID'leri korunur; kesinleşmeyen alt anlamlar taslak niteliğindedir.

## Toplu giriş simülasyonu — %20 icra eksikliği planlama payı

A01–A09 tek iş olarak değerlendirilir. Dokuz görevin %20'si yaklaşık iki görev eder. Her iki-görev düşüm senaryosunda blok kabulü HOLD üretmelidir:
(1) A01+A02 kaynak envanteri; (2) A03+A04 yetki ve provenance; (3) A05+A06 gerçek E5/G01–G03; (4) A07+A08 fark/ROI; (5) A09 + rastgele diğer kontrol.
Kritik yetki kaybı ayrıca **tek kusur** ile blok HOLD üretir. Bu tasarım sınaması ampirik ChatGPT hata oranı değildir.

## Giriş ve çıkış kanıtı
ENTRY: dokuz iş kimliği / kapsam / bağımlılık grafiği / HOLD ayrımı / karşıt plan.
EXECUTION: GitHub-first kaynakları toplu hazırlama; bağlı alt PR #207 tekil yetki yardımcı kanıtıdır.
EXIT: dokuz işin gerçek kaynak pinleri, kanıt kaydı, bağımsız review, %20 eksik enjeksiyonu, görevler arası bağımlılık ve canonical kabul sınırları yeniden test edilir.
BLOCK FINISH: ancak dokuz gerçek yetkili PASS ile. Bu dokümanın hazırlanması blok resmî sayacını artırmaz.

## Dört ayrı sayaç
Teorik kapsam 100/100 (öz değerlendirme); GitHub hazırlık 50/100; OSi saha 0/100; resmî 0/40.
Kâşifi canonical kaynak / A03 grant / 18 E5 / gerçek G01–G03 ve K12 ayrı HOLD.
NEXT: Birleşik giriş testini CI'de pinle; blok eksiklerini yetkili belgeye bağla; çıkış simülasyonunu aynı dokuz iş üzerinden tamamla.

## V4.2 kanonik görev kimliği uzlaştırması
A04 upstream; A05 müşteri deployment; A06 bağımsız E5; A07 G01–G03; A08 beş yıllık K12 TCO. V423 önceki konu satırlarında A06/A07 görev kayması düzeltildi; özgün A01–A09 sayacı ve resmî 0/9 korunur. G01–G03 tasarım testleri gerçek saha kabulü yerine geçmez. Bağlayıcı görev sahibi ve reviewer yetkileri canonical source/DoneCheck üzerinden doğrulanır.
