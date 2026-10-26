# ENGÜRÜ Yetenek Hasadı™ · Zülfikar V1.4.1 kaynaklı devam

**Tarih:** 26 Ekim 2026. **Ürün:** Yetenek Hasadı V1.1, PR #243, yalıtılmış `review/enguru-yetenek-hasadi-v11-20261025`.
**Gerçek V1.4.1 kaynak:** aynı deponun PR #246 inceleme dalındaki immutable commit `8fbd40c8fde34e7f8d77d5079c4da86a1baa8dad`.
**Kaynak mührü:** `governance/enguru-suzgeci/zulfikar-v12/v141/GITHUB_SOURCE_SHA_SEAL_V1.json`; orijinal önceki ZIP SHA-256 `366d906c3f44e86d834a311365c2bead51f82509faec7568c6374209b5c9224e`.

## Sözleşmeye göre 8 kapılı tek hedef akışı

| V1.4.1 | Yetenek Hasadı gerçek içerik | Şart |
|---|---|---|
| T01 Temel | Hedef, önceki 65/100 GitHub ve 60/100 OSi kanıtı | Korunan geçerli kaynak/owner |
| T02 Hedef hazırlığı | H01–H10, P01–P12, K01–K05 | Tam kabul/negatif test sözleşmesi |
| A01 Mimari | Altı kütüphane, tek skill kernel, kaynak/kanıt ayrımı | Tek owner, yeni core 0 |
| A02 Teori ve karşıt | Sahte PASS, SHA kayması, yetki, kaynak değişimi | Zülfikar üç mantıksal tur + gerçek test |
| A03 E2E/finiş | PROVEN, gerçek kullanıcı faydası, DoneCheck, Human Threshold | Gerçek kaynaklı ayrı kapı |
| A04 GitHub icrası | Exact-head PR #243, pinned orijinal V1.4.1 378 test ve CI | Tüm zorunlu koşular SUCCESS |
| A05 Gerçek görev pilotları | Beş heterojen **gerçek kullanıcı** görevi ve 12 özgün haricî beceri | **HOLD**, gerçek görev makbuzu henüz yok |
| A06 OSi ön hazırlığı | GitHub'da SHA-256 devir paketi, rollback ve saha giriş planı | **PRE_FIELD_ONLY**, Mac icrası 0 |

**Bağımlılık:** Gerçek A05 PASS olmadan gerçek A06 bütünsel ürün kabulu açılmaz; daha eski GitHub-only devir tasarımı ayrı korunur. V1.4.1 kaynağındaki 100/100 DÖM sonucu sadece **mimari/yerel hazırlık kapsamıdır**.

## GitHub üzerinde çalışan gerçek V1.4.1 motorunu kaynaktan kullanma

- `ZULFIKAR_V141_SOURCE_REUSE.json` Git kaynak commit'i, mühür, sekiz aşama, yetki HOLD'unu kilitler.
- `reuse_zulfikar_v141.py` GitHub runner'da **sabit commit'i fetch eder**, mühürlü **18** gerçek kaynak dosyasının SHA-256'sını, path güvenliğini ve canonical saha yetki sınırını doğrular.
- Gerçek orijinal `preflight.py`, yalnız GitHub geçici dizininde çalıştırılır; üç ayrı **126 × 3 = 378 unittest** makbuzu ve önceki 100/100 tasarım kontrolü teyit edilir.
- Kod çekirdeği, kanıt ve macOS kaynakları PR #243'e kopyalanmaz; ikinci bir V1.4.1 çekirdeği veya yetkili issuer açılmaz.
- `test_zulfikar_v141_reuse.py` sahte PASS, kaynak mührü drift, bozuk kapı sırası ve eksik test saldırılarına ayrı kontrol sağlar.
- `v141-source-reuse-receipt.json` **teknik source reuse** delilidir. Bu kayıt `GITHUB_VERIFIED_FINISH=PASS`, `PROVEN=12/12` veya `OSI_FIELD=PASS` düzenleyemez.

## Puan ve sağlam duruş

Son kanıt puanı: GitHub **65/100**, OSi GitHub-only hazırlık **60/100**. Bu V1.4.1 kaynaklı icra **puan şişirmesi olmadan mevcut test metodunu güçlendirir**; yeni kullanıcı faydası/issuer yetkisi kanıtlanana kadar resmî bitiş HOLD'dur.

`PiLive` PARKED, `main` MERGE 0, Mac OSi execution 0, yeni ücretli API 0, ikinci insan owner 0.
