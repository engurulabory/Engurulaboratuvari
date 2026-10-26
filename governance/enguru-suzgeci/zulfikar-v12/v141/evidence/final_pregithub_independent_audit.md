# ENGÜRÜ Zülfikar™ V1.4.1 — Son Bağımsız GitHub Öncesi Denetim

## Yönetim kararı

**`READY_FOR_CONTROLLED_GITHUB_REVIEW_COMMIT`** / `GITHUB_WRITE=0` / `MAC_OSI_WRITE=0` / `OFFICIAL_PRODUCT_FINISH=HOLD`.

### Kapsamlı mühendislik puanı

| Alan | İlk bağımsız eleştiri (analitik) | Son denetim |
|---|---:|---:|
| Özgün hedefin canlı SHA kontrolü | 14/20 | 20/20 |
| Özgün kabul kriterlerinin bütünlüğü | 12/20 | 20/20 |
| Üç farklı gerçek tur ve makbuz tutarlılığı | 12/20 | 20/20 |
| Güncel çapraz oturum kanıtı ve dosya değişim algısı | 18/20 | 20/20 |
| Eksik veri halinde HOLD, regresyon ve aktarım güvenliği | 18/20 | 20/20 |
| **Yalnız GitHub öncesi kod/test hazırlığı** | **74/100** | **100/100** |

İlk puan bağımsız kod incelemesinde ortaya çıkan kusurlara göre yapılan analitik teşhistir; kaynak dosyasında mevcut eski puan yerine yeni sahte ölçüm değildir. Son puan, yalnız yukarıdaki beş yerel hazırlık alanının belirlenen test/kanıt sınırlarıdır.

## Tespit edilen gerçek kusurlar ve onarım

1. Bitiş kanıtı SHA beyanını doğruluyordu fakat **özgün hedef kaynak dosyasının canlı baytlarını** son değerlendirme anında kontrol etmiyordu. Canlı kaynak SHA eşitliği zorunlu kılındı; symlink ve eksik kaynak HOLD.
2. Birleştirilmiş handoff denetimi, **özgün `contract.criteria` yerine kısmen/substitüe edilmiş evidence kriterleri** kabul edebiliyordu. Tam set eşitliği zorunlu; eksik/fazla ID raporlanıyor.
3. Üç fazlı görev turunda üst raporun `taskOutcome`, `exitCode`, `fault/recovery` ve `regressionClear` alanları **gerçek tur makbuzuyla çapraz doğrulanmıyordu**. Çelişkide EXECUTION_HOLD.
4. Dış inceleme callback'i sırasında hedef/sonuç/inceleme/checkpoint dosyaları değişebilirdi. Callback sonrası tekrar SHA ile doğrulama eklendi, değişimde COMPLETION_HOLD.
5. Eksik veya bozuk kabul gereksinimleri istisna oluşturabiliyordu. Kaynağı ve açık şartları bildiren yapılandırılmış EVIDENCE_HOLD ile onarıldı.

## Deneysel kanıt

- **126 farklı unittest × 3 ayrı yerel koşu = 378/378 PASS**, gerçek test yürütmesi ve SHA'lı loglar.
- **10/10** sekiz kapılı mimari yapısal kontrol PASS.
- Başlangıç 112 mevcut test korundu; **14 yeni karşıt test** eklendi.
- Üç test koşusu, üç farklı üretim ürünü veya bağımsız Mac saha gözlemcisi anlamına gelmez. Testlerdeki süreç makbuzları yerel geçici pilot kanıtıdır; kendi kendine bildirilen `processObserved` gerçek Mac/kullanıcı gözleminin yerine geçmez.
- Geçerli yerel aday, owner/DoneCheck veya VERIFIED_FINISH üretmez. Mevcut gerçek reviewer ve owner doğrulaması ayrıca zorunludur.

## GitHub geçiş kuralları (sonraki ayrı adım)

- Salt-okunur gözlenen PR: `#246`, draft, HEAD `4780d96ccb16ca4a922846ab48918262c7845f47`. Yazmadan önce HEAD'i yeniden uzlaştır.
- Yeni kod, yeni test ve güncellenmiş preflight/workflow'u **yalnız inceleme dalında**, tek yazıcıyla kaydet. `main` ve PiLive korunur.
- GitHub kaynak SHA eşitliği, gerçek yeni commit SHA, CI workflow ve **126×3=378** gerçek test sonucunu doğrula. Sonuç alınana kadar `GITHUB_CI=HOLD`.
- Mac OSi, PiLive saha kullanıcı görevleri, bağımsız reviewer, Human Threshold ve resmî ürün bitişi ayrı kabul.

**Son sınır:** `GITHUB_PREPARATION=100_100_IN_DEFINED_SCOPE → READY_TO_COMMIT → STOP`.
