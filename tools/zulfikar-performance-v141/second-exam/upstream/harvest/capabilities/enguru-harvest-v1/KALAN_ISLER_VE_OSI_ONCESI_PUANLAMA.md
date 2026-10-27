# ENGÜRÜ Yetenek Hasadı™ — Zülfikar V1.3.1 Kalan İş ve Devir Kararı

**Karar tarihi:** 26 Ekim 2026. Kaynak: `READINESS_SCORECARD_V1.json`.
**Kabul edilen son kanıtlı başlangıç:** PR #243 `0d714edaeaa0b4347766b31cd2e0d33c1d6ce489`, 5/5 GitHub workflow SUCCESS, Harvest içinde 3/3 job, 73/73 Python regresyon ve 30/30 mantıksal simülasyon.

## Değerlendirme

- **GitHub Verified Finish hazırlık puanı: 63/100.** Exact-head CI ve kaynak doğrulaması PASS; gerçek kullanıcı faydası, lisans/güvenlik kabulü, 12 bağımsız PROVEN beceri ve owner Human Threshold ayrı HOLD. Resmî `GITHUB_VERIFIED_FINISH=HOLD`.
- **OSi öncesi hazırlık puanı: 55/100.** GitHub kaynakları, makbuz haritası ve devir tasarımı güçlü. Gerçek Mac çalışma ortamı, imzalı/local runtime saha makbuzu, SQLite canary, kaynak kullanım yetkisi ve owner girişi hâlâ kanıt bekliyor. `OSI_EXECUTION=0`, `OSi_FIELD=HOLD`.
- Bunlar **açık ağırlıklı analist puanlarıdır**; canonical otorite veya otomatik DoneCheck PASS'i değildir.

## K01–K05 kalan işler ve en yakın bitiş şartı

| Paket | Kalan hedef | Kanıtlı mevcut kazanım | Kapı |
|---|---|---|---|
| K01 | Beş gerçek *kullanıcı* görevi ile faydayı tekrarlı ölç | 5 gerçek kaynak-ID mikrobenchmark'ında %99.7 civarı süre düşüşü | HOLD_REAL_USER_VALUE |
| K02 | Seçilen her haricî kaynak için lisans, güvenlik, arşiv SHA ve ücretsiz erişim sınırı | 30 README gözlemi, 29 lisans metni gözlemi, 30 karantina | HOLD_REUSE_AUTHORITY |
| K03 | Gerçek yetkili Codex/Claude Code ajan deneyleri; Claude'un eski npm yolunu yetkili alternatifle değiştir | Agent Skills uyumu ve Codex CLI sürüm PASS, Claude eski npm CLI HOLD | HOLD_REAL_AGENT |
| K04 | Yeni HEAD üzerinde 5/5 CI ve 3/3 Harvest job, Zülfikar karar matrisi ile kanıt uzlaştırması | Eski HEAD'de 5/5 ve 3/3 PASS | EXACT_HEAD_CI_REPEAT |
| K05 | Tek owner'ın GitHub teknik hazırlık hükmü; ayrı canonical DoneCheck ve OSi geçiş yetkisi | Tek-owner V1.3.1 kaynakta açık: ikinci peer reviewer teknik hazırlık için zorunlu değil | HOLD_HUMAN_THRESHOLD |

## OSi devrinden önce üç sınır

1. GitHub teknik kaynak ve CI kimliği exact-head ile doğrulanır.
2. Gerçek ürün Verified Finish, kaynak/lisans ve yetkili kabul ayrı bir kapıda kanıtlanır.
3. Mac OSi kurulum/çalıştırma ancak kullanıcının ayrı saha kararı ve özgün ürün kabulüyle ilerler; burada `0`.

**Tek insan sahibi:** `engurulabory`. **Yeni ücretli API zorunluluğu:** 0. **Yeni insan reviewer hesabı:** 0. **Merge:** 0.

**Yeni referans:** Sonraki bütün mühendislik ve kabul kontrolleri `READINESS_SCORECARD_V1.json` üzerinden sayısal karşılaştırılabilir; puan yükselişi ancak kanıtla gerçekleşir.
