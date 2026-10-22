# ENGÜRÜ Yönetim → İCRA V17 | Dar hedef

**Başlangıç:** 18/100 kanıtlı kontrol. **Hedef:** 22/100, yalnız kanıtlanan +4 kontrol. **Resmî kabul:** H1–H3 0/12, F01–F06 0/6, Verified Finish HOLD; yalnız yetkili kayıt bu sayaçları ilerletir.

**Ana iş F01:** Mevcut 12 kriter ve V13 tek karar dosyasından yetkili owner/reviewer kaynağını kesin tespit et; yetki varsa gerçek karar + DoneCheck/Mac binding kanıtına bağla. Yetki eşiğinde tek açık karar ve kesin sahibi ile `HOLD_AUTHORITY`.

**Bağımsız destek F05:** V16 mevcut izole patch ve gerçek Mac build kanıtını koru; yeni onarım motoru yerine şu dört kaynak-mutabakat kontrolünü kanıtla:

- `B01-07`: Yerel ürün HEAD ↔ `origin/main` kapsam farkının kaynak analizi.
- `B07-01`: PR #14 stage blob'unun yerel Git'te bulunabilirlik nedeninin kesin teşhisi.
- `B07-02`: Yerel HEAD, `origin/main` ve PR #14 ancestry karşılaştırması.
- `B07-03`: Korunmuş dirty-path farkları için somut owner review/uygulama planı.

**Koruma:** Orijinal HEAD, çalışma alanı, mevcut uygulama, kilitli v0.6 kabulü ve AudiV13 korunur. Canonical promotion, signing, install, remote write ve resmî acceptance ayrı Human Threshold™ kapılarındadır.

**İCRA yanıtı en çok 6 satır:**

`STATE=İLERLE/GÜVENLİ_DUR`
`SAYAC=18/100 → N/100 (+kanıtlı)`
`YENI_PASS=B01-07,B07-01,... / YOK`
`F01=PASS/HOLD + tek kesin gerekçe`
`F05=PASS/HOLD + tek kesin gerekçe`
`RESMI=H1/H2/H3 0/12; F01-F06 0/6; RAPOR_SHA256=...; SONRAKI=...`

**Yönetim hükmü:** Yüzde hedefi iş üretim baskısı değil, kapanacak somut kontrol hedefidir. Kaynak veya yetki kanıtı açık kaldığında mevcut gerçek sayı korunur. Tek rapor AudiV13, tam ayrıntı JSON içinde.
