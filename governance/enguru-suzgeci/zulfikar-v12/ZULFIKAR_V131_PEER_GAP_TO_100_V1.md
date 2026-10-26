# ENGÜRÜ Zülfikar™ V1.3.1 · Muadil Yetkinlik Analizi ve 100/100 Operasyonel Yol

**Tarih:** 2026-10-26 · **STATE:** `GITHUB_OPERATIONAL_BRIDGE_REVIEW / REAL_OSI_FIELD_HOLD`
**Sabit hedef:** Gerçek mühendislik görevlerinde kanıtlı, yetkili, devam ettirilebilir ve bitişi denetleyen çalışma. Sonra gerçek kullanıcı faydası, bağımsız gerçek muadil denemeleri ve saha.
**Puan uyarısı:** 88/100 önceki yönetim değerlendirmesidir; bağımsız benchmark sonucu değildir. `100/100` bütünsel hedef **yalnız gerçek iş/OSi/son kullanıcı kanıtıyla** kazanılır. Hedef ve GitHub kod kapılarındaki 100/100 yerel sınırlı teknik rubriktir.

## 1. Muadil ürün taraması — üretici belgelerinde ifade edilen kabiliyetler

| Muadil | Güncel üretici/açık kaynak belge kabiliyeti | Zülfikar'ın mevcut sınırı | Hasat edilen uygulama kararı |
|---|---|---|---|
| OpenAI Codex CLI/Work | Çalışma alanı sandbox ve izin politikası, izinli shell, oturum devamı, subagent, review | Zülfikar salt-okunur doğrulayıcı; OS düzeyinde sandbox veya genel executor değil | İlgili gerçek Mac Engineer yetki/action registry ve ayrı izin kapısını doğrula, ikinci sandbox iddiası üretme |
| Claude Code | Hooks, modüler skills/agents, checkpoint/rewind, CLI | Zülfikar CLI analizi var, resmî devam/checkpoint doğrulaması yok | Donmuş mission+sourceHead, resume kanıtı olmadan HOLD, gerçek işletim köprüsü ayrı |
| Cursor Agent | Çok dosyalı kodlama, terminal, tarayıcı ve checkpoint | Zülfikar arayüz/görsel motor değil | Mevcut Mac Engineer/Work ve UI görsel kapılarını kullan, görsel ürün kabulünü ayrı tut |
| GitHub Copilot cloud agent | Issue → branch/work → PR → CI/review; sıkı görev ve kabul kriterleri | Zülfikar kalite kapısı var, gerçek Work aksiyon haritası eksik | Aynı proje/work ID + mevcut aksiyon kaydı + tek yazıcı + gerçek kanıt bağı |
| OpenHands | Local browser/agent backend, Docker/VM izolasyonu, araçlar | Yerel OSi uygulama doğrulaması yok | Local-first; Mac Engineer motor gerçek saha/izin kapısında, GitHub gözlem ayrı |
| Aider | Repo map, Git commit/diff, tekrar test/lint | Görev kanıtı ve kod onarımı döngüsü Zülfikar içinde otomatik değil | Existing Work/GitHub test/PR feedback ile ayrı ara kontrol ve regresyon kaydı |

**Başvuru bağlantıları** (belgelenmiş kabiliyet ≠ eş koşullu gerçek benchmark):
- [Codex izin/sandbox](https://learn.chatgpt.com/docs/agent-approvals-security), [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- [Claude Code skills/agents/rewind](https://support.claude.com/en/articles/14554922-claude-code-user-faq), [Claude hooks](https://support.claude.com/en/articles/14554000-claude-code-power-user-tips)
- [Cursor Agent](https://cursor.com/docs/agent/overview), [Cursor Cloud](https://prod.cursor.com/help/ai-features/background-agents)
- [GitHub Copilot Agent](https://docs.github.com/en/copilot/concepts/agent-capabilities/about-agents/about-github-copilot-agents)
- [OpenHands Agent Canvas](https://github.com/OpenHands/docs/blob/main/openhands/usage/agent-canvas/overview.mdx)
- [Aider kaynak ve test entegrasyonu](https://github.com/Aider-AI/aider)

Muadiller bu turda kurulmadı veya çalıştırılmadı. Ürün sürüm/fiyat/eş bütçe koşulları sabitlenmeden performans sıralaması yapılmaz. Ücretli API=0 hedefi korunur.

## 2. 88/100'dan görünen gerçek farklar

| Gap ID | Eksik / ihtiyaç | Bu tur üretilen fark | Şu anki kabul |
|---|---|---|---|
| ZF131-G01 | Görev→kaynak→aksi̇yon eşliği | Mevcut Mac Engineer `CAPABILITY_EXECUTION_BINDING` + `OPERATOR_ACTION_REGISTRY` ile exact handler/authority bridge | GitHub kod/test PASS adayı; gerçek motor dispatch HOLD |
| ZF131-G02 | Sahte yetki/sahte bitiş | Owner/issuer, HT ve official finish çitleri | GitHub kod/test PASS adayı |
| ZF131-G03 | Tek yazıcı ve aynı iş kimliği | `missionId/workId`, tek yazar, conflicting count/reused control fail-closed | GitHub kod/test PASS adayı |
| ZF131-G04 | Bağımlılık ve süreklilik | Delilli dependency list ve açık `RESUME_PROPOSED` HOLD | Gerçek durable checkpoint/resume **HOLD** |
| ZF131-G05 | Çalışma alanı güvenliği | HEAD SHA, committed registry byte ve read-only preflight; remote push/dryRun kapısı | GitHub preflight PASS adayı; OS-enforced sandbox/ gerçek kaynak yürütme HOLD |
| ZF131-G06 | Gerçek kod→test→onarım | Test edilip Work/Mac Engineer existing handler'a yönlendirme | Gerçek görev yürütme ve onarım döngüsü **HOLD** |
| ZF131-G07 | Bağımsız karşıt veri ve muadiller | Adil benchmark manifestinde aynı görev/sürüm/girdi/metrik eşliği | Gerçek peer trial **HOLD** |
| ZF131-G08 | Gerçek kullanıcı sonuçları | E1–E5 ve PiLive U01–U12 ile evidence map | Saha kullanıcı faydası **HOLD** |
| ZF131-G09 | Yerel sıfır ek ücret | Kayıtlı mevcut motor ve Python stdlib kullanımı, ek ücretli API=0 | Code dependency PASS adayı; Mac saha HOLD |
| ZF131-G10 | Human Threshold/DoneCheck | Kaynakta kanıtlanmış rol sınırı, resmî finiş STOP | Yetkili gerçek kabul **HOLD** |

**Mevcut icra aracı:** `zulfikar_v131_operational_bridge.py` sadece `preflight --input manifest.json` okur; eylem yürütmez, dosya yazmaz, GitHub push etmez. Source HEAD ve iki registry committed-byte doğrular; manfest izinli olsa bile cevap `PREFLIGHT_READY_EXISTING_OPERATOR_ONLY` der ve `realTaskExecuted=false` olur. Mevcut motorun görev yetkisini genişletmez.

**Bağımsız Work yazıcısı:** PiLive PR #241. Bu dal Zülfikar'ın kendisine ait inceleme/kapıdır; PiLive koduna, başka oturumların kaynaklarına, canonical, OSi app veya main'e yazım yok.

## 3. Sabit başarı ölçüsü / 100/100 hedef ölçütleri

**Teknik GitHub bridge spesifikasyonu:** Aşağıdaki 10 kriterin tamamı gerçek GitHub HEAD CI ile doğrulanırsa yalnız `GITHUB_READ_ONLY_BRIDGE_TESTS=100/100`:
1. Kaynak README, V3 canonical SHA ve goal v1.3.1 şeması korunur.
2. Mevcut Mac Engineer binding ve registry kaynaklarının HEAD baytları doğrulanır.
3. Tek proje ve work kimliği + tek owner/issuer korunur.
4. Bağımlılık kanıtı ve teklik fail-closed.
5. İki çalışan kayıtlı yetkili action için preflight kanıtı; yeni handler/core yok.
6. Tek yazıcı ve remote write/HT/finish negatifleri reddedilir.
7. Kaynak drift ve bozuk JSON deterministic HOLD.
8. CLI pozitif/negatif gerçek subprocess ve kaynak pin kontrolü.
9. En az üç farklı görev profili; her biri yalnız source-bound preflight, gerçek task execution sayılmaz.
10. Exact HEAD 3× test ile CI kanıtı.

**Gerçek 100/100 OPERASYONEL hedef** için ayrıca en az:
- 3 farklı **gerçek kullanıcı projesi**; `INTAKE → authorized handler → code/test/repair → binary/runtime/evidence` izi, 3/3 gerçek saha teslimi.
- En az üç onaylı kalıcı checkpoint/resume; kesinti+retry, idempotency ve tek writer gözlemi.
- Gerçek Mac Engineer–OSi üzerinde kaynak/davranış SHA, açık Human Threshold; gerekli ürünün resmî DoneCheck'i.
- Eş koşullu, dondurulmuş manifest, beş eş deneme/peer ile kontrollü benchmark; kaynak, sürüm, fiyat, kullanıcı etkisi ve yanlış PASS sayacı.
- Gerçek ve bağımsız kullanıcı geri bildirimi, göreve harcanan süre, müdahale ve tekrar hata yüzdesi.

Kriterlerin yazılması gerçek performans 100 değildir. **İlerleme standardı:** Teknik tasarım tamamlanır, mevcut runner/Work üzerinde gerçek görev kanıtı elde edilir, Mac OSi yetkisi ve DoneCheck bağımsız geçirilir; sonra 100/100 onaylanabilir.

## 4. Zülfikar 3 tur simülasyon/kanıt

- **SIM1 — Kaynak/otorite:** Sabit action+handler+authority eşliği; değişen kaynak, sahte owner/issuer, dual writer durumlarının HOLD'u.
- **SIM2 — Devam/onarma:** Dependency ve checkpoint doğrulaması; kanıtsız resume → HOLD; real operator dispatch yalnız yetkili action'a.
- **SIM3 — Karşıt ve CI:** Üç gerçek registry profiliyle read-only CLI, bozuk action/unhashable input, terminal ve source pin regresyonları ×3; exact-head GitHub CI.

**Kalıcı sınır:** `GOAL=100` ve `GITHUB_CODE=100` kendi rubriğinin adıdır. `OSi_FIELD=HOLD / PEER_REAL_BENCHMARK=HOLD / OPERATIONAL_100=HOLD / VERIFIED_FINISH=HOLD`.

**Çalışma sırası:** muadil hasadı → gap register → minimal bridge → 3 tur GitHub CI → gerçek üç görevli saha kampanyası → bağımsız benchmark → OSI → DoneCheck/Human Threshold → `VERIFIED_FINISH → BITTI_DUR`.
