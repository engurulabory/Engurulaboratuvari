# ENGÜRÜ Yetenek Hasadı™ V1.1 — Gerçek GitHub teknik deney defteri

**Kanıt kapsamı:** PR #243, izole GitHub inceleme dalı. 12 dış kabul ID'si bağımsız korunur. Bu dosya gerçek CI yürütme tanıklarını listeler; **teknik deney başarıları resmî PROVEN değildir**.

## Gerçek CI gözlemleri

| ID | Kaynak/Deney | Teknik kanıt | Özgün kabul |
|---|---|---|---|
| P01 | Codex gerçek runtime ve talimat hiyerarşisi | Hesap/yürütme şartı ayrıştırılacak | HOLD |
| P02 | Claude Code gerçek runtime | Ticari şartlar ve gerçek yetki gerekiyor | HOLD |
| P03 | Agent Skills resmî `skills-ref` | İki ENGÜRÜ SKILL.md doğrulaması; geçersiz örnek reddi | Teknik PASS / PROVEN HOLD |
| P04 | Anthropic PDF/DOCX SKILL.md | Upstream tam commit altında ikisi de biçimsel PASS, lisans Anthropic şartlarına bağlı; kod/skill icrası 0 | Biçim PASS / yeniden kullanım HOLD |
| P05 | MCP reference server üzerinden stdio | Gerçek sunucu icrası bekliyor | HOLD |
| P06 | MCP Python SDK 2.3.0 | Gerçek bellek içi istemci–sunucu araç çağrısı ve protokol müzakeresi | Teknik PASS / PROVEN HOLD |
| P07 | MCP TypeScript SDK 2.4.0 | Gerçek linked in-memory client/server tool çağrısı + bozuk parametre reddi; 2025-era taşıma testi | Teknik PASS / PROVEN HOLD |
| P08 | promptfoo 0.125.0 | `echo` ile 2/2 gerçek değerlendirme, model API çağrısı 0 | Teknik PASS / gerçek model etkisi HOLD |
| P09 | Hypothesis 6.170.9 | 4 özellik testi, 140 örnek/test; ilk karşıt örnek tespit edilip onarıldı | Teknik PASS / PROVEN HOLD |
| P10 | Ruff 0.16.8 | Gerçek Python kaynak lint PASS; E741 hatası onarıldı | Teknik PASS / PROVEN HOLD |
| P11 | uv 0.13.5 | Çevrimdışı kilit iki çalışmada SHA-256 eşliği | Teknik PASS / PROVEN HOLD |
| P12 | LM Evaluation Harness | Gerçek harness icrası ve karşılaştırılabilir görev kanıtı bekliyor | HOLD |

**Teknik deneyler:** P03/P06/P07/P08/P09/P10/P11 = 7 gerçekten çalıştırılan haricî araç/protokol denemesi; P04 = 1 haricî kaynağın biçim sınaması. 12 haricî beceriden **0/12 PROVEN**.

## Kaynak ve SHA zinciri

- 2026-10-26 son GitHub exact-head kanıtı: `91421c4d76ba0e399fe9cb8ed144e8a3e46a66bb`, 5/5 GitHub Actions SUCCESS.
- [GitHub Actions gerçek runner ve makbuzları](https://github.com/engurulabory/Engurulaboratuvari/actions/runs/40281228629).
- [Koşu çıktılarının ZIP makbuzu](https://github.com/engurulabory/Engurulaboratuvari/actions/runs/40281228629/artifacts/12631904767).
- Anthropic upstream format kimliği: `dbd4588f9e1033efb41dad4bef2f7947c8993d44`, PDF/DOCX lisans onayı 0.
- Resmî Agent Skills referans kaynağı: `69ef37e9424c0a7ea9dd2293b559e43ec8176379`.
- Python 47 regresyon PASS, mantıksal SIM1–SIM3 30/30 PASS.
- Exact HEAD baytları ve canonical V3 SHA-256 doğrulandı.

## Açık kapanış

Gerçek eş koşullu kullanıcı görevi/ölçümleri; P01/P02/P05/P12; bağımsız PR inceleme; kaynak bazlı tam lisans ve güvenlik izinleri; gerekli yetkili karar ve DoneCheck™ tamamlanana kadar `GITHUB_VERIFIED_FINISH=HOLD`.

`OSI_EXECUTION=0`; Mac OSi aktarımı hazırlanmış fakat icra edilmemiştir. `main` ve kullanıcı kararları korunur.
