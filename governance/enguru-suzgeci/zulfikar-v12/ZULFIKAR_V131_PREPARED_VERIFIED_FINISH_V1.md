# ENGÜRÜ Zülfikar™ V1.3.1 — Hazırlık Finişi Kabul Sözleşmesi

**Tarih:** 26 Ekim 2026
**Yönetim hedefi:** GitHub hazırlık kalitesi üç ayrı boyutta kanıtlı 100/100 olduğunda PREPARED_VERIFIED_FINISH_GITHUB teknik kabulü verilebilir. Gerçek Mac ürün VERIFIED_FINISH yetkisi bu tanımın dışında kalır.

## 1. Ayrı puan defterleri

| Alan | Önceki gerçek saha dâhil puan | Hazırlık rubriği hedefi |
|---|---:|---:|
| Operasyonel olgunluk / operasyonel hazırlık | 91/100 HOLD | 100/100 |
| Gerçek uçtan uca bitirme / bitirme hazırlığı | 65/100 HOLD | 100/100 |
| Gerçek proje aktarımı / projeler arası hazırlık | 90/100 HOLD | 100/100 |

Önceki puanlar gerçek saha gereklilikleri için korunur. Hazırlık puanı GitHub'ın çalıştırılmış kaynak, güvenlik, uygulama ve kanıt sözleşmesinin kalitesini ölçer. Gerçek görev yürütme, kesintiden kurtarma, Mac GUI, owner/issuer, DoneCheck ve saha kabulü ayrı kanıtla değerlendirilir.

## 2. ENGÜRÜ Süzgeci ve Zülfikar üç tur

- **Tur 1 — Hakikat ve kaynağı koruma:** Immutable git HEAD, gerçek registered-action kimlikleri, tek yazıcı, owner/issuer ve kaynak SHA eşliği.
- **Tur 2 — Onarım ve uygulanabilirlik:** Native PiLive, Mac Engineer restart/recovery ve Web build/regression için üç mevcut kayıtlı yetenek–aksiyon–handler–yetki eşlemesi. Yeni core, issuer, handler veya ücretli API sıfır.
- **Tur 3 — Karşıt sınama:** Yanlış head, sahte owner/işlem sonucu, yanlış aksiyon, sahte yeniden başlatma, bağımlılık makbuzu, yarım kalmış veri girişi, bozuk kontrol kimliği ve yanlış ürün PASS durumları güvenli HOLD.

İlk CI turu kaynak içindeki kontrol yazım farkını yakaladı: OP04_REGISTRY_HEAD_BYTES_PINNED ile OP04_REGISTRY_HEAD_BYTES_PINN uyuşmuyordu. Kaynak sözleşmesinin sabit PINNED kimliği korundu; kod bu kimliğe göre onarıldı. Tekrarlanan GitHub gerçek test kapısında üç hazırlık alanı 100/100 PASS oldu.

### 3 × 10 kontrol

- **OP01–OP10 — Operasyonel hazırlık:** Kaynak, hedef, yürütme aksiyonuna devir, SHA, üç pilot, özel makbuz denetimi, tek yazıcı, yanlış PASS, tek inceleme dalı ve subprocess regresyonları.
- **E01–E10 — Uçtan uca bitirme hazırlığı:** Donmuş iş sırası, gerçek HEAD, dependency bağı, handler yetkisi, kurtarma kanıt sınırı, SHA eşliği, bağımsız gözlem, DoneCheck, Mac ayrımı ve negatif test.
- **P01–P10 — Projeler arası hazırlık:** Üç aile, üç kayıtlı yetenek, handler/authority, üç ayrı preflight, yanlış HEAD/aksiyon, 14 kanıt alanı, owner kapsamı, mevcut motor kullanımı ve replay.

Çalıştırılabilir doğrulayıcı: zulfikar_v131_prepared_finish.py. Kaynak sözleşmesi: ZULFIKAR_V131_PREPARED_FINISH_CONTRACT_V1.json. Karşıt test: test_zulfikar_v131_prepared_finish.py.

Öncelik sırası: GitHub kaynak kodunun 30/30 gerçek kontrolü → 3 farklı CI test turu → HEAD/CI kanıtı → hazırlık teknik kabulü → gerçek Mac yetkili saha. Sözleşmede sadece hedefin yazılı olması PASS için yeterli değildir.

## 3. Korunan gerçek saha kapıları

Üç farklı gerçek görevde yetkili sonuç 3/3, Mac owner kimliği/izin kaydı, source→handler→test→binary→görünen kullanıcı sonucu, durable checkpoint/restart recovery, adil gerçek muadil denemesi, DoneCheck v1.2 ve Human Threshold kendi gerçek kabul koşullarına tabidir.

PiLive Work PR #241 mevcut tek aktif mühendislik yazıcısıdır. Tasarım PR #245 yaratıcı kabulü kendi scope'unda sürdürür. OSi Birleşik Sistem Mimarisi PR #244 fabrika HOLD durumunda kalır. Zülfikar PR #246 yalnız bu yöntemin hazırlık incelemesi ve kanıt kaydıdır. main ve Mac/OSi orijinalleri korunur.

**Yönetim hükmü:** PREPARED_VERIFIED_FINISH_GITHUB → REAL_MAC_FIELD_3_OF_3 → ALL_FIELD_DOMAINS_100_OF_100 → AUTHORIZED_DONECHECK/HUMAN_THRESHOLD → VERIFIED_FINISH → BITTI_DUR.

**Bu aşama:** Hazırlık tamamlanıp GitHub CI tarafından doğrulansa bile ürün Verified Finish, gerçek görev yürütmesi veya kullanıcı kabulü beyanı verilmez.
