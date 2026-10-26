# ENGÜRÜ Yetenek Hasadı™ · Zülfikar V1.4.1 · OSi Öncesi Tam Hazırlık

**Tek hedef:** GitHub kanıtlı ürün adayının Mac OSi alanına ileride, tek sahibin ayrı izin verdiği durumda güvenli devri ve ilk gerçek çalışma adımlarını eksiksiz planlamak. `OSi_PRE_FIELD_PREPARATION=100/100`, gerçek Mac saha `0`, `HUMAN_THRESHOLD=HOLD`, `OFFICIAL_VERIFIED_FINISH=HOLD`. Uygulamaya hazır hükmü, saha testinin yapıldığı hükmü değildir.

## 8 Zülfikar kapısı · 5/5 hazırlık kanıtı

T01 **Temel:** GitHub canonical kaynak kimliği, ürün sınırı, korunacak masaüstü/OSi özgünleri, tek owner ve riskler; gerçek Mac envanteri giriş görevi olarak hazırlanır. Kanıtlar: `goal.json`, `UPSTREAM_GITHUB_PINS_30.json`, `OSI_HANDOFF_PREPARATION.md`, `osi_entry_preparation.json`, `ZULFIKAR_V141_SOURCE_REUSE.json`.

T02 **Hedef:** OSi uygulama hedefi, bağımlılık kapıları, Mac gerçek ilk adım listesi, saha kabul soruları, güvenli durma koşulları. Kaynaklar: `ZULFIKAR_V131_100_GATE_CONTRACT.json`, `ZULFIKAR_100_FINIS_VE_SINIRLAR.md`, `WORK_PACKAGES_ZULFIKAR_V13.json`, `PILOT_APPLICATION_PREP_V141.json`, `osi_entry_preparation.json`.

A01 **Yerel mimari:** GitHub kaynak pinlerinden OSi dosya manifestine güven; sha256; Mac'e var olan dosyanın üzerine yazmama; yalıtılmış alan; yerel geçici SQLite aday planı. Kaynaklar: `build_github_osi_handoff.py`, `test_github_osi_handoff.py`, `OSI_HANDOFF_PREPARATION.md`, `osi_preflight_contract.py`, `osi_entry_preparation.json`.

A02 **Karşıt teori:** bozuk ZIP, symlink, sahte Mac/owner, bozuk manifest, bozuk rollback, yanlış kaynak SHA, tekrarlı/yeniden başlatma idempotency test planı. Kaynaklar: `test_github_osi_handoff.py`, `test_osi_preflight_contract.py`, `zulfikar_finish_gate.py`, `test_zulfikar_finish_gate.py`, `osi_preflight_contract.py`.

A03 **Uçtan uca ve finiş tasarımı:** GitHub çıkışı → owner saha yetkisi → salt-okunur Mac sistem envanteri → SHA-kilitli kopya → yalıtılmış yerel pilot → SQLite/restart → yetkili DoneCheck → insan saha kabulü. Kaynaklar: `OSI_HANDOFF_PREPARATION.md`, `ZULFIKAR_100_FINIS_VE_SINIRLAR.md`, `osi_entry_preparation.json`, `ZULFIKAR_V131_100_GATE_CONTRACT.json`, `GITHUB_APPLICATION_PREP_V141.md`.

A04 **GitHub mühendisliği / devir:** exact HEAD source byte eşliği, V3 SHA, 30 kaynak pin, Github-only ZIP ve makbuz, teknik CI yolu. Kaynaklar: `verify_head.py`, `build_github_osi_handoff.py`, `READINESS_AUDIT_V3.json`, `UPSTREAM_GITHUB_PINS_30.json`, `.github/workflows/enguru-harvest-v1.yml`.

A05 **Gerçek saha pilotu hazırlığı:** owner-yetkili saha giriş talimatları, yerel izole yeniden başlatma, sıfır veri kaybı/yan etki kriteri, SQLite/idempotency kayıt şablonu, Mac uyumluluk sürüm keşfi. Kaynaklar: `osi_entry_preparation.json`, `PILOT_APPLICATION_PREP_V141.json`, `test_osi_preflight_contract.py`, `OSI_HANDOFF_PREPARATION.md`, `KALAN_ISLER_VE_OSI_ONCESI_PUANLAMA.md`. **Saha deneyi henüz yapılmadı**.

A06 **İcra öncesi son mühür:** örnek kaynak ZIP'i, SHA-256 ve manifest, bağımsız yerel kopya için SHA prosedürü, rollback, en düşük yetki ve yetkili owner kararı kapısı. Kaynaklar: `build_github_osi_handoff.py`, `test_github_osi_handoff.py`, `osi_preflight_contract.py`, `READINESS_AUDIT_V3.json`, `ZULFIKAR_V141_SOURCE_REUSE.json`.

## Hazırlığın gerçek 100/100 kabul şartı

- 8 kapı × 5 kaynaklı özgün kanıt, exact Git HEAD bayt eşliği ve mevcut canonical V3 SHA kilidi.
- Üç ayrı simülasyon turu: tutarlılık, karşıt yanlış yetki, bütünleşik devre hazırlığı; negatif durumlar zorunlu HOLD.
- GitHub CI üzerinde gerçek Python ve mevcut kaynak/ZIP güvenlik testlerinin yürütülmesi.
- Bağımlılık belgesi, kaynak/lisans seçimi, Mac runtime/OS/arch/sürüm envanter kontrolü, tek owner karar mekanizması ve saha durma adımları **hazır ve yazılı**.
- Gerçek Mac uyumluluğu, SQLite saha canary, orijinal dosya kopyalama ve Human Threshold: **gelecekte gerçek yetkili OSi çalışması ile kanıtlanacak**.

## Uygulama anı (yalnız ayrı owner yetkisiyle)

1. GitHub kaynak ve 100/100 hazırlık makbuzunun SHA'sını doğrula; korunan Mac orijinallerini tara.
2. Önce Mac salt-okunur çevre envanteri; eksik mimari/sürüm/dependency varsa HOLD.
3. GitHub ZIP'i yalnız yeni izole dizine kopyala; SHA karşılaştır; mevcut dosyanın üstüne yazma. SHA farkı varsa HOLD.
4. Yerel güvenli DB/saha canary, idempotency, restart ve geri dönüş; yalnız owner onayıyla.
5. Kullanıcı ekranında gerçek fayda, kaynak izinleri ve canonical DoneCheck/owner kabulü; PASS halinde ürün finişi, aksi halde HOLD.

**Sabit:** `OSI_EXECUTION=0`, `MAIN_MERGE=0`, `MANDATORY_PAID_API=0`, `OWNER=engurulabory`. Hazırlık PASS saha kapısını otomatik açmaz.
