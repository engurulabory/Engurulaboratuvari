# ENGÜRÜ Yönetim → İCRA V18

**Sayaç:** 21/100 → **22/100**; tek teknik hedef `B07-02`. Gerçek kanıt kadar yeşil ✓.

**F01 (ana):** V13 tek Human Threshold™ kararını, mevcut 12 kriter için doğrulanmış owner/reviewer yetkisi ve Mac–DoneCheck kabul bağlantısıyla sonuçlandır. Yetkili insan eşiğinde tek net karar sun; gerçek kayda göre `İLERLE / GÜVENLİ_DUR`.

**F05 (destek):** `B07-02` için yerel HEAD, origin/main ve PR #14 HEAD `9f3b0fa9f0d5de86d9aa5dbd42e8e40c43ec5e24` Git ancestry'sini gerçek SHA, `merge-base`, `rev-list`, commit/blob ve kapsam farkıyla kanıtla. Yerel nesne erişimi için ilk tercih salt-okuma sorgusu; gereken uzaktaki nesneleri **izole geçici Git alanında** edinerek ana çalışma ağacını ve mevcut refs'i koru. Erişim veya kaynak yetkisi eksikse kesin HOLD gerekçesiyle teslim et.

**Koruma:** V16 çalışan Swift stage/patch, v0.6 kilidi, yerel branch/HEAD, dirty-path, kullanıcı uygulaması ve AudiV13. Canonical promotion/merge, signing, install ve resmî kabul ayrı yetkili kapılar.

**Yanıt (en çok 6 satır):**

`STATE=İLERLE/GÜVENLİ_DUR`
`SAYAÇ=21/100 → N/100`
`YENİ_✓=B07-02 / YOK`
`F01=PASS/HOLD + tek gerekçe`
`F05=PASS/HOLD + tek gerekçe`
`RESMÎ=0/12; KAPANAN=0/6; RAPOR_SHA256=...; SONRAKİ=...`

**Kalıcı sabit hedef:** H1 4/4 → H2 4/4 → H3 4/4 → Native Mac Engineer OSi → Verified Finish → `BITTI_DUR`.
