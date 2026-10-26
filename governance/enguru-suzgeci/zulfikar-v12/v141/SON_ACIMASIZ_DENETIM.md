# ENGÜRÜ Zülfikar™ V1.4.1 / Döngü Onarım™ V1.0 — Son Karşıt Mühendislik Denetimi

**Tarih:** 26 Ekim 2026  
**Kullanıcı hedefi:** 1) Sert/bağımsız eleştiri; 2) bütün GitHub-öncesi erişilebilir kusurları onar ve DÖM ile tekrar doğrula; 3) GitHub kayıt/CI aşamasına **yetki bekleyerek** gel, orada dur. PiLive korunur.

## Eleştiri: Gerçek teknik eksikler ve onarım

| ID | Başlangıçta görülen zayıflık | Yerel onarım | Kanıt / kabul |
|---|---|---|---|
| F01 | Sekiz kapı şemada sıralıydı, çalışan yürütücüde bir kapı önceki onay olmadan başlayabiliyordu. | T01 sonrası her kapı için **tam önceki kapı + aynı goalId + 100 puan + owner scope + dış doğrulayıcı** kabulü aranır. | Kırmızı durumlar ve sekiz kapının hepsinde sıra sınaması; `test_39`–`test_44`, `test_58` PASS. |
| F02 | Kaynak doğrulaması yalnız callback'in `True` sözüne güveniyordu. | Kaynak yolunun gerçek dosyası `O_NOFOLLOW` ve FD üzerinden okunup SHA-256 karşılaştırılır. Kaynak her tur ve kapanıştan önce yeniden ölçülür. | `test_36`–`test_38`, `test_45`–`test_48` PASS. |
| F03 | SHA zinciri tek başına aynı anda iki yazıcıyı engellemiyordu. | `fcntl.flock(LOCK_EX|LOCK_NB)` ile döngü boyunca tek yerel süreç; yazıcı çıkınca kilidin serbest bırakılması. | Gerçek ayrı süreçler `test_54`, `test_59` PASS. |
| F04 | Günlük dosyası sembolik/sabit bağlantı veya kesik satır yoluyla risk taşıyordu. | `O_NOFOLLOW`, normal dosya/tek link, inode eşliği, son satır sonlandırması, kayıt alanı ve zincir kontrolü. | `test_49`–`test_53`, önceki tahrifat testleri PASS. |
| F05 | Test komutu sadece Linux `sha256sum` destekliyordu. | Yerel kanıt testleri Linux `sha256sum`, mevcut değilse macOS `shasum -a 256` çağırır. | Linux gerçek süreç PASS; **Mac üstünde çalıştırılmadı**. |
| F06 | Hazırlık puanı yalnız test adlarının varlığına dayanıyordu. | Tekil unittest sonuçları ve exit code'un **3 ayrı turda** geçmesi, şema kontrolleri ve ilave karşıt güvenlik testleri puan kaynağına bağlandı. | 59 gerçek test × 3 = 177/177 PASS. |
| F07 | Kaynak kopyasının GitHub yerleşimi ve CI işinin kapsamı kesin paketlenmemişti. | Depoya taşınacak göreli yol haritası ve yalnız PR üzerinde test yapacak read-only CI taslağı ayrı `github_stage` altında hazırlandı. | Kaynak ve kopya SHA manifesti; GitHub'a hiçbir yazma yapılmadı. |
| F08 | Simülasyon ve dosya üretimi resmî gerçek ürün bitişi gibi sunulabilirdi. | Her çıktı `acceptedScore=null`, `stagePassIssued=false`, `productVerifiedFinish=NOT_ISSUED`; reviewer/owner yetkileri haricî kaldı. | Sahte PASS reddi, artalan kaydının yetki oluşturmaması ve 100'de yalnız aday PASS. |

## Bilinçli kabul sınırları — GitHub öncesi yeniden adlandırılmayan eksikler

1. **Gerçek Mac OSi, GitHub CI ve resmî insan kabulü yapılmadı.** Yerel izole sınama onların yerini tutamaz.
2. **Yerel SHA zinciri kimlik doğrulayan dijital imza değildir.** Günlük yazma yetkisi olan biri tüm zinciri yeniden hesaplayabilir. Saha kabulünde gerçek yetkili haricî imza/pin ve DoneCheck gerekir.
3. **Dış doğrulayıcı callback'ine sahada yetkili güven kökünden bağlanılması gerekir.** Testteki taklit `lambda: True`, üretim izin ve imzası değildir.
4. **10 yeteneğin tamamının gerçek dünyada 100/100 olduğuna dair kanıt yok.** Yerel 100 puanı DÖM'ün GitHub öncesi hazırlık sözleşmesi ve sekiz kapı mimarisi ile sınırlıdır.
5. **`github_stage` yalnız aktarım taslağıdır**; kaynak HEAD uzlaştırması, bağımsız review, gerekli GitHub workflow güvenlik incelemesi ve gerçek Actions koşuları henüz gerçekleşmedi. `main` ve PiLive değişmedi.

## Gerçek kabul yöntemi ve hüküm

- Denetim alanları: **D01–D05**, 20'şer puan, toplam 100; her alan eski davranış testleri + yeni karşıt testlerle bağlı.
- Mimari: **T01, T02, A01–A06** tam 8 kapı; yalnız kendi kapsamı 100 ve dış kabulü varsa sonraki kapı.
- Yerel simülasyon: hedef → kaynak → mimari → simülasyon → değerlendirme → açıklar → onarım → **gerçek ayrı süreç** → yeni simülasyon → değerlendirme → kanıt adayı.
- **Kabul:** `DÖM_LOCAL_PRE_GITHUB_PREPARATION_100_PASS`. **İlerleme:** `GH_REGISTRATION_REVIEW_REQUIRED`; GitHub yayımlama/CI başlatma yetkisi bu raporla verilmez.

**Karar:** GitHub'a **geçiş öncesi yerel kaynak/kanıt paketi** hazırdır. Gerçek GitHub başarı puanı henüz oluşmadı. Kullanıcının “GitHub'a geçelim” iznini bekleyerek DUR.
