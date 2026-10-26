# ENGÜRÜ Zülfikar™ V1.4.1 — Son bağımsız denetim / GitHub öncesi paket

**Kaynak:** Kabul edilmiş 26 Ekim 2026 DÖM V1.0 orijinal ZIP'i **aynen korunmuştur**. Bu klasör, bağımsız sert denetim ve onarımlarla üretilmiş **yeni bir kopyadır**.

## Hedef ve yöntem

Kullanıcının tek sabit hedefi → **T01 temel atma** → DÖM ile kapsam kanıtlı 100 → **T02 hedef hazırlığı** → DÖM ile kapsam kanıtlı 100 → **A01–A06** (mimari, teori, uçtan uca/finiş tasarımı, GitHub uygulaması, gerçek pilotlar, OSi ön hazırlığı). Her kapı yeni kanıtla ayrı değerlendirilir. 1–99 sadece teşhistir. **Gerçek hedef tamamlanması, bağımsız yetki ve kanıt gerektirir.**

## Gerçek çalışma

`python3 -B preflight.py` — yalnız yerel hazır/test verisi üretir. `dom/engine.py` gerçek yerel dosya onarımını, haricî işletim sistemi doğrulamasını, tekrar simülasyonu ve puanlamayı koordine eder. `dom/test_engine.py` + `dom/test_final_hardening.py`, kaynak ve yetki sınırını negatif testlerle denetler. Linux `sha256sum` ile sınanmıştır; macOS üzerinde `shasum -a 256` destek yolu kodda vardır, **Mac saha PASS'i iddia edilmez**.

## Son sonuç

- DÖM beş alan **20/20 × 5 = 100/100, sadece GitHub öncesi yerel hazırlık**.
- Mimari tasarım kaynak kontrolleri **10/10 PASS**, sekiz kapı tanımlı ve önceki kapı olmadan ilerleme reddi kodda.
- **59 test × 3 = 177 gerçek yerel unittest çalıştırması PASS** (izole geçici dosyalar ve ayrı süreç doğrulaması).
- Kaynak ve çalışma alanı SHA-256 kayıtları `SHA256_MANIFEST.json` dosyasındadır. `python3 -B verify_release.py` ile bağımsız bayt doğrulaması yapılır; `github_stage/` salt-okunur GitHub aktarım taslağıdır.
- Gerçek GitHub PR/Actions, gerçek Mac OSi kurulum, owner DoneCheck/Human Threshold ve 10 genel yeteneğin ürün 100/100'ü **BU SONUÇTA YOKTUR**.

Ayrıntılı sert eleştiri ve onarımlar: `SON_ACIMASIZ_DENETIM.md`; GitHub'a geçiş prosedürü: `GITHUB_GECIS_PLANI.md`; hazırlık raporu: `evidence/pre_github_readiness_report.json`.

**DUR:** Açık kullanıcı izni gelinceye kadar GitHub veya Mac üzerinde işlem yapılmayacak. PiLive korunur.
