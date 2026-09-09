# ENGÜRÜ TRUST PRODUCTIZATION™ v1

## Niyet
Legacy trust varlıklarını yeni ürün yığınına dönüştürmeden, mevcut doğrulanmış ENGÜRÜ güvenlik ve governance motorları üzerinde sade bir ürünleşme mimarisi kurmak.

## Authority
Niyet → mevcut core reuse → evidence → DoneCheck™ → Human Threshold™ → Verified Finish.

## Locked structure

### MayaShield™ — PRODUCT_CANDIDATE
Amaç: AI/model kullanımı sırasında şirket bilgisini, fikrî mülkiyeti ve hassas bağlamı koruyan kullanıcı/kurum güvenlik ürünü.

Reuse-first motor:
- IP & Model Trust Gate™
- Secret Zero™
- Security Fleet™
- Human Threshold™
- DoneCheck™
- Evidence

Candidate flow:
`INPUT → CLASSIFY → PROVIDER/MODEL TRUST CHECK → MINIMUM DISCLOSURE/SANITIZE → AUTHORITY DECISION → EXECUTION BOUNDARY → EVIDENCE → DONECHECK → HUMAN THRESHOLD`.

State: CANDIDATE / HOLD. Ayrı repo ve satış yüzeyi, ürün intake + demand proof + runtime contract tamamlanınca açılır.

### Safety Decision Layer™ — DEVELOPER_PRODUCT_CANDIDATE
Amaç: ajan/uygulama eylemleri için policy + risk + authority karar API/SDK yüzeyi.

Candidate contract:
`REQUEST → POLICY → RISK → AUTHORITY → PASS | HOLD | BLOCKED → EVIDENCE`.

Reuse-first motor:
- MİZAN™
- Human Threshold™
- IP & Model Trust Gate™
- policy/evidence patterns

State: CANDIDATE / HOLD. MayaShield saha/demand kanıtından önce bağımsız ürünleştirme açılmaz.

### TRUSTSPINE™ — TRUST_BACKBONE_CAPABILITY
Ürün değildir. Güven zincirinin omurgasıdır:
`Language Governance → IP Trust → Security → DoneCheck → Evidence → MİZAN → Human Threshold → Verified Finish`.

State: INTERNAL / HOLD until exact implementation ownership is evidenced.

### MİZAN™ — GOVERNANCE_CAPABILITY
Ürün değildir. Evidence ve başarı kriterlerini değerlendirip Human Threshold'a karar girdisi üretir.

Boundary:
- MİZAN = değerlendirme / eşik mantığı
- Human Threshold = nihai insan yetki sınırı

State: INTERNAL / HOLD until canonical implementation path is evidenced.

### Maya Trust™ — ASSURANCE_SURFACE
Şimdilik bağımsız SaaS değildir. Engürü ürünlerinin doğrulanmış güven/evidence durumunu sunan gelecekteki assurance yüzeyidir.

Olası public signals:
- Security state
- DoneCheck state
- Human Threshold state
- evidence reference
- last verified date

State: FUTURE_SURFACE / HOLD.

## Productization order
1. ENGÜRÜ Builder™
2. Artist Manager AI™
3. MayaShield™ candidate intake / demand proof
4. Existing planned-product queue according to current Product/Core Map
5. Safety Decision Layer™ only after developer demand/evidence

Bu sıra mevcut Labory execution planini değiştirmez; trust ürün adaylarını gelecekteki intake için hazırlar.

## Creation rule
`reuse → extend → adapter → new core`

MayaShield ve Safety Decision Layer için mevcut trust/security/governance motorları yeniden yazılmaz. Ayrı kod ancak ürün sınırı bunu zorunlu kıldığında eklenir.

## Publication rule
PRODUCT_CANDIDATE, aktif/satılabilir ürün sayısına girmez. Public CTA ancak repository, runtime, DoneCheck evidence, Verified Finish ve Human Threshold PASS olduğunda açılır.
