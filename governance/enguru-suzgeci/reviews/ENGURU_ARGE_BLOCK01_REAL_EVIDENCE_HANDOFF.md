# BLOK 01 — A01–A09 birleşik gerçek kanıt teslim şartları
STATE: EVIDENCE_HANDOFF_READY / ACCEPTANCE_HOLD
Source: Issue #205, V19 18x13 canonical research matrix, PR #207 review-only.

## Tek blok, 18 vaka
18 vaka x 13 kontrol = 234 hücre. Her bir vaka için aynı beş gerçek kanıt ailesi gereklidir:

| Alan | Gerçek teslim | Mevcut kabul |
|---|---|---|
| E5 | Müşteri/üreticiden bağımsız doğrulayıcı kimliği, tarih, gerçek kullanım ve yeniden denetlenebilir kaynak/imza | 0/18 |
| Customer deployment | Müşteri exact release+edition+commit, SBOM/manifest, gerçek deployment SHA-256 ve yetkili teyit | 0/18 |
| G01/G02/G03 | Dış etki uzlaştırma, ilişkisel yetki ve zaman tazeliği için gerçek test girdileri/çıktıları, negatif senaryo, doğrulayıcı | HOLD |
| K12 | Aynı kapsam ve iş yüküyle mevcut ENGÜRÜ ve adayın ölçülmüş ROI/TCO: lisans, altyapı, ekip, operasyon, risk; bağımsız hesap tekrar testi | HOLD |
| Yetki ve final | A03 görev kapsamlı owner/issuer imzalı grant ve trust root, bağımsız reviewer, DoneCheck v1.2 ve Human Threshold | HOLD |

## Diğer kapılar
A04 Kâşifi özgün canonical kaynak/ref/release, SHA-256, lisans/güvenlik kapsamı gerekir. V19 önceki kararlar ve source SHA-256 3906f7bd6ae07d26547babc172d1337cfdfeff85244ece95efb76c3cb448df08 korunur.
18 yayımlanmış müşteri ve teknoloji kaynak adayları E5 bağımsız mühendislik denetimi değildir. Replit Temporal kullanımının tarihsel, Restate geçişinin daha yeni olduğuna dair karşıt kaynaklar saklanır.

## Roller ve yetki kapısı
Customer/owner: üretim sürüm kanıtını sağlar. Bağımsız E5 gözlemcisi: gerçek kullanım ve bağımsız kaynak onayı sağlar. Canonical issuer: A03 grant ve güven kökü yetkisini doğrular. Bağımsız GitHub reviewer: PR #207 exact diff ve test kararını verir. DoneCheck ve Human Threshold: resmî bitişi karara bağlar.
Bu belge owner veya reviewer ataması ve grant yerine geçmez.

## Birleşik çıkış eşiği
18/18 E5, gerçek müşteri sürümü, G01-G03 geçerli testler, K12 nicel fayda/TCO, Kâşifi canonical kaynak, A03 gerçek grant/trust, yetkili review ve DoneCheck kabulü kanıtlanınca resmî 9/9 kararı yalnız mevcut authority zinciri üzerinden alınır.
%20 eksik vaka/görev karşıt senaryosu HOLD üretmelidir. GitHub test PASS ≠ bağımsız E5 veya saha PASS.

CURRENT: GitHub 50/100, OSi 0/100, resmî 0/40; BLOK01 0/9; independent E5 0/18.
NEXT: gerçek customer/owner/reviewer kayıtlarıyla 18 vakalık tek teslimi al, kaynak imza ve SHA doğrula, ortak blok çıkış testini tekrar yürüt.
