# ENGÜRÜ Yetenek Hasadı™ V1.1 — Gerçek GitHub teknik deney defteri

**Kanıt kapsamı:** PR #243, izole GitHub inceleme dalı. 12 dış kabul ID'si bağımsız korunur. Bu dosya gerçek CI yürütme tanıklarını listeler; **teknik deney başarıları resmî PROVEN değildir**.

## Gerçek CI gözlemleri

| ID | Kaynak/Deney | Teknik kanıt | Özgün kabul |
|---|---|---|---|
| P01 | Codex gerçek runtime ve talimat hiyerarşisi | Hesap/yürütme şartı ayrıştırılacak | HOLD |
| P02 | Claude Code gerçek runtime | Ticari şartlar ve gerçek yetki gerekiyor | HOLD |
| P03 | Agent Skills resmî `skills-ref` | İki ENGÜRÜ SKILL.md doğrulaması; geçersiz örnek reddi | Teknik PASS / PROVEN HOLD |
| P04 | Anthropic PDF/DOCX SKILL.md | Upstream tam commit altında ikisi de biçimsel PASS, lisans Anthropic şartlarına bağlı; kod/skill icrası 0 | Biçim PASS / yeniden kullanım HOLD |
| P05 | Everything MCP referans sunucusu 2.0.1 / stdio | Node 24 ayrı proses, 16 araç keşfi, gerçek echo çağrısı ve SHA-256 makbuzu | Teknik PASS / PROVEN HOLD |
| P06 | MCP Python SDK 2.3.0 | Gerçek bellek içi istemci–sunucu araç çağrısı ve protokol müzakeresi | Teknik PASS / PROVEN HOLD |
| P07 | MCP TypeScript SDK 2.4.0 | Gerçek linked in-memory client/server tool çağrısı + bozuk parametre reddi; 2025-era taşıma testi | Teknik PASS / PROVEN HOLD |
| P08 | promptfoo 0.125.0 | `echo` ile 2/2 gerçek değerlendirme, model API çağrısı 0 | Teknik PASS / gerçek model etkisi HOLD |
| P09 | Hypothesis 6.170.9 | 4 özellik testi, 140 örnek/test; ilk karşıt örnek tespit edilip onarıldı | Teknik PASS / PROVEN HOLD |
| P10 | Ruff 0.16.8 | Gerçek Python kaynak lint PASS; E741 hatası onarıldı | Teknik PASS / PROVEN HOLD |
| P11 | uv 0.13.5 | Çevrimdışı kilit iki çalışmada SHA-256 eşliği | Teknik PASS / PROVEN HOLD |
| P12 | LM Evaluation Harness (kaynak SHA pinli) | Gerçek CLI, iki satır yerel JSONL ve dummy model, exact_match=1.0 (yalnız örnek veri) | Teknik PASS / gerçek model faydası HOLD |

**Teknik deneyler:** P03/P05/P06/P07/P08/P09/P10/P11/P12 = 9 gerçekten çalıştırılan haricî araç/protokol değerlendirmesi; P04 = 1 haricî kaynağın biçim sınaması. 12 haricî beceriden **0/12 PROVEN**.

## Kaynak ve SHA zinciri

- 2026-10-26 P05 kaynak HEAD: `ee013493f0ec28bac533638040dbf143bc0ec556`, 5/5 GitHub Actions SUCCESS. P12 gerçek değerlendirme [ayrı runner'da PASS](https://github.com/engurulabory/Engurulaboratuvari/actions/runs/40282455391); aynı eski HEAD'deki Ruff F401 sorunu sonraki commit'te onarıldı. Güncel exact-head tüm CI kararı ayrıca doğrulanır.
- [P05 gerçek stdio runner ve makbuzları](https://github.com/engurulabory/Engurulaboratuvari/actions/runs/40282127487).
- [P12 gerçek LM Eval runner ve makbuzları](https://github.com/engurulabory/Engurulaboratuvari/actions/runs/40282455391).
- [Koşu çıktılarının ZIP makbuzu](https://github.com/engurulabory/Engurulaboratuvari/actions/runs/40281228629/artifacts/12631904767).
- Anthropic upstream format kimliği: `dbd4588f9e1033efb41dad4bef2f7947c8993d44`, PDF/DOCX lisans onayı 0.
- Resmî Agent Skills referans kaynağı: `69ef37e9424c0a7ea9dd2293b559e43ec8176379`.
- Python 47 regresyon PASS, mantıksal SIM1–SIM3 30/30 PASS.
- Exact HEAD baytları ve canonical V3 SHA-256 doğrulandı.

## Açık kapanış

Gerçek eş koşullu kullanıcı görevi/ölçümleri; P01/P02 yetkili ajan runtime; P04 gerçek beceri yürütme ve lisans; bağımsız PR inceleme; kaynak bazlı tam lisans ve güvenlik izinleri; gerekli yetkili karar ve DoneCheck™ tamamlanana kadar `GITHUB_VERIFIED_FINISH=HOLD`.

`OSI_EXECUTION=0`; Mac OSi aktarımı hazırlanmış fakat icra edilmemiştir. `main` ve kullanıcı kararları korunur.

## Makinece denetlenebilir kanıt kapsaması

`upstream_execution_coverage.json` ve `test_upstream_execution_coverage.py` P01–P12 özgün kimliklerini korur: **9 gerçek haricî teknik icra, 1 ayrı biçim incelemesi, 2 yetki/HOLD; resmî PROVEN 0/12.** Makbuzların hiçbirinde Mac OSi icrası veya gerçek kullanıcı faydası kabulü beyan edilmez.
