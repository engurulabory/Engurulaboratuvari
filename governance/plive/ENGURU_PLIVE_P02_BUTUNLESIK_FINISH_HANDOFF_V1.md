# ENGÜRÜ PLive P02 — Bütünleşik Finiş Hazırlığı V1

**Niyet:** Korunan PLive V3.1 Mac işleyişini canonical dört paket ve 12 P02 işi ile bağlamak; tamamlanmış teknik kanıtı yeniden kullanmak; gerçek yetkili finişe kadar yalnız gereken farkı ilerletmek.

**ENGÜRÜ Süzgeci™ v2.4:** Hakikati gör → Değeri koru → Eksikleri ve ihtiyaçları tespit et → Gerekli farkı üret → Eksikleri tamamla, ihtiyaçları karşıla → Kanıtla → Bir sonraki ihtiyaçları belirle → İlerlet. Dokuzuncu aşama, yeni core, ikinci sayaç veya ayrı G3 kapısı yok.

**Pozitif dil:** Mevcut değeri koru. Gerekli farkı üret. Yalın onay. Yetkili ve akıcı işleyiş. Sağlam karar. Tamamlanmış kanıt. Doğrulanmış sonuç. Güvenlik engellerinde teknik HOLD terimi aynen korunur.

## Kaynak hakikati ve sınırlar

- Son OSi native saha sonucu: P01 2/2 VERIFIED, final binding LOCKED; P02 0/12 HOLD, progress integrity PASS, drift NONE.
- Kullanıcı gözlemi: V3.1 yerel Mac'te derlendi; kullanıcı Applications altındaki uygulama 7/7 SHA eş kaynakla kuruldu; beş üretim alanı, ⌘R yenileme, Finder'dan tekrar açılış manuel kabul edildi. Bunlar **teknik saha kanıt adayıdır; resmî P02 countedPass değildir.**
- Beş başlık mevcut; yedi gerçek proje henüz canonical primaryArea ile sınıflandırılmıyor. Beş kayıt bağlantı bekliyor, sekiz planlanan sayaç dışında. P02 mühendislik işlerini beş üretim alanına sahte ürün gibi ekleme.
- G3 simülasyonları gerçek kurumsal issuer, güven kökü, Ed25519 yetkisi, bağımsız onay, sahici grant veya yetkili writer sahipliği değildir.
- Önceki DoneCheck 0/4 ve yedi saha önkoşulu 1/7 gözlemi tarihseldir; güncel saha iddiası için ayrı readback gerekir.
- GitHub tasarım adayı OSi local canonical kayıtlarının yerine geçmez. Ana kaynak, Mac'teki var olan Work Contract, State, Worklist ve Progress Core'dur.

## Tek resmî finiş eşiği

12/12 gerçek yetkili item PASS + 4/4 mevcut DoneCheck + 7/7 mevcut saha önkoşulu + gerçek Human Threshold ACCEPTED + native Progress Core Verified Finish → BİTTİ → DUR.

### Aynı mevcut dört paket

| Paket | Mevcut üç iş | Tamamlanacak gerçek teslim / kabul |
|---|---|---|
| S01 Kaynak ve sayaç | P02.S01.01–03 | Exact-source P01 korunumu, gerçek G3 issuer/grant/writer ile ilk bounded item, Work Contract/Worklist/State, registry ve S01 DoneCheck |
| S02 Aktif iş | P02.S02.01–03 | Gerçek tek aktif OSi iş, A→B→A seçimi, ad/aşama/ilerleme uyuşması ve paket DoneCheck |
| S03 Ekran | P02.S03.01–03 | Canonical beşli kategori tek sahip, gerçek canlı yenileme, scroll/drag/overlap/erişilebilirlik, insan saha kabulü ve paket DoneCheck |
| S04 Güvenlik/finiş | P02.S04.01–03 | G04 gerçek OS restart/durable journal, bağımsız güvenlik kanıtı, dört DoneCheck, yedi kapı, insan kabulü, native Verified Finish |

## Birleşik ve bütünleşik güvenli OSi işleyişi

Tek Python aracı: tools/plive_p02_integrated_finish_handoff_v1.py

**--self-test:** Sadece sentetik fixture ve sözleşme matematiği. Gerçek OSi'ye erişmez, 12 item kimliği, beş alan, çift sayım, geçmiş resmî kabul, G3/sahte yetki ve finiş eksikliği karşıt testlerinden geçer.

**--observe:** Ön simülasyon PASS sonrasında OSi mevcut HEAD, yedi gerçek kaynak SHA-256 ve tracked çalışma durumunu önce/sonra okur; P01/P02 existing native verify, gerçek V3.1 bundle kimliği, dört paket ve 12 item eşlemesi. Yalnız AudiV13 içine orijinal JSON makbuz ve Masaüstü'ne doğrulanmış kopya üretir. Kurulu uygulamayı çalıştırmaz, yeni grant/issuer oluşturmaz, canonical kayıtlara yazmaz.

**Kaynak kayması:** HEAD veya SHA değişirse güvenli HOLD, kaynak yeniden nitelendirilir. PASS_READONLY_RECONCILIATION, sadece okuma ve uzlaştırma PASS'idir; resmî P02 kabulüne kredi vermez.

**Sıradaki tek bağımlılık:** G3 için gerçek mevcut bağımsız onaylı trust root / issuer kimliği, anahtar sahipliği ve iptal sorumluluğu, bounded P02.S01.01 grant ve yetkili dayanıklı writer. Bu onay gerçek mevcut sahiplerin otoritesinden gelmelidir. Sohbet, fixture imzası veya kullanıcı niyeti yeni grant sayılmaz.

**Sonraki akış:** G3 kanıtlanınca ayrı resmî yetkili iş geçişi + native readback → S01 DoneCheck → S02 → S03 → S04; önceden onaylı geçerli kapsamda gereksiz insan komutu isteme; yeni kapsam veya nihai Human Threshold için ayrı yetkili karar.

**DUR:** GitHub CI model PASS ile OSi saha PASS'i karıştırma. P01/P06, tek Progress Core, user Applications V3.1, AudiV13 ve mevcut OSi repo HEAD korunur.
