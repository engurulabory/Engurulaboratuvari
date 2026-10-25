# ENGÜRÜ Yetenek Hasadı V1.1 — Kabul ve Kanıt Matrisi

**Canonical:** `AGENTS.md` → V3 SHA-256 `11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc` → Zülfikar V1.3. Bu dosya kayıtlı durumun kaynak açıklamasıdır, otomatik resmî kabul değildir.

| Hedef | GitHub teknik doğrulama | Resmî / saha durumu |
|---|---|---|
| H01 tek amaç | `goal.json`, CI şema kontrolü | Tasarım adayı |
| H02 gerçek değer | `paired-gain` beş eş koşullu test şeması | Gerçek kullanıcı verisi HOLD |
| H03 özgün ID | 10 hedef ID, 30 kaynak adayı | Gerçek kazanımlar HOLD |
| H04 yetki | Kendiliğinden terfi kapatıldı | Bağımsız reviewer / Human Threshold HOLD |
| H05 DAG | GitHub → OSi ayrımı, devir planı | OSi yürütme 0 |
| H06 bütçe | Sıfır zorunlu ücretli API sözleşmesi | Gerçek donanım ölçümleri HOLD |
| H07 karşıt örnek | Negatif Python testleri, SIM2 | Dış saldırı sınaması HOLD |
| H08 kanıt | 12 yerel işlem testi, SIM1–3 mantıksal | 12 dış beceri gerçek test HOLD |
| H09 SHA-kilit | `verify_head.py` git HEAD byte eşliği, V3 SHA | Dış kaynak commit/lisans HOLD |
| H10 rollback | Yalıtılmış inceleme dalı, devre hazırlığı | Yetkili kabul HOLD |

## Sayısal gerçek ayrım

- **30/30 SOURCE_OBSERVED_ONLY:** 30 public GitHub deposunun README'si erişilip README Git SHA-1 blob kimliği kaydedildi. Kaynak arşivi SHA-256 ve lisans onayı henüz elde edilmedi.
- **12/12 LOCAL_OPERATION_IMPLEMENTED:** Standart Python beceri çekirdeği operatörleri kaynakta tanımlı ve CI test kapsamındadır. Bunlar 12 bağımsız haricî Codex/Claude becerisi yerine geçmez.
- **SIM1/SIM2/SIM3:** Yerel veri ve sentetik karşıt durumlar; gerçek dış servis veya Mac OSi saha simülasyonu değildir.
- **Exact-head:** CI'de `github.event.pull_request.head.sha` checkout, `git show HEAD:<path>` eşliği ve canonical kaynak SHA-256 doğrulaması gerekir.
- **Bağımsız insan/issuer:** henüz 0 kabul makbuzu. İmza, ödeme, yayın, merge ve yerel saha kendi yetkisinde kalır.

## GitHub teknik PASS / resmî Verified Finish ayrımı

Teknik GitHub PASS ancak aynı PR HEAD üzerinde bütün zorunlu CI işlerinin SUCCESS ve kaynak kimliklerinin PASS olmasıyla raporlanır. Resmî `GITHUB_VERIFIED_FINISH`, ayrı bağımsız inceleme, özgün kabul ID'leri ve Human Threshold şartları gerçekleştiğinde değerlendirilebilir. Mac OSi kurulumu bu PR'de 0.
