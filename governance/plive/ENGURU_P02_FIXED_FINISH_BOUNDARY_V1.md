# ENGÜRÜ P02 — FIXED FINISH BOUNDARY (OWNER REQUESTED)

**KABUL SINIRI KESİN / DEĞİŞMEZ:** Mevcut altı kapıdan başka kapı yok. Dört canonical P02 paketi, 12 native item, dört DoneCheck, yedi saha önkoşulu, bağımsız güvenlik, Human Threshold korunur. Mevcut ENGÜRÜ Süzgeci™ v2.4 sekiz aşaması ve tek Progress Core sabittir.

| Kapı | Yalnız gerçek native PASS koşulu |
|---|---|
| 01 G3-A | Exact signer source/build/binary linkage, eligible profile, authenticated issuer, user presence and independent trust enrollment |
| 02 G3-B | Authenticated scope-bound signed grant, revocation, expiry, nonce/replay, HEAD, preimage, evidence and policy |
| 03 G3-C | **Mevcut** yetkili P02 canonical writer, durable CAS/nonce/journal, crash/restart, independent security |
| 04 G3-D | Yetkili real P02.S01.01 transition + Progress Core native before/after readback |
| 05 P02 | Real 12/12, DoneCheck 4/4, prerequisites 7/7, G03/G04 and independent security PASS |
| 06 Finish | Separate Human Threshold ACCEPTED + native finishState VERIFIED → BITTI_DUR |

**KABUL HÜKMÜ:** Her kapı PASS veya HOLD; `engineering ready`, `9/9 CI`, `source found`, `SHA pass`, `offline crypto verified` resmi PASS değildir. Altı kapıdan herhangi biri HOLD ⇒ finish HOLD. Gate-7, yeni core, ikinci writer, yeni sayaç, yeni SORTİ ya da yeni koşul açma. Yeni bulguyu mevcut altı kapıya yerleştir; yalnız gerçek yeni kritik güvenlik riski ve açık insan kapsam onayı istisna.

**Tek native preflight teslimi**: `ENGURU_P02_FIXED_FINISH_PREFLIGHT_V1.zip` SHA-256 `7c4b5532469670d56e6b0836cda4c9ac41448b021bd86741ba62745efc80d06a` (ChatGPT attachment; ZIP bytes GitHub'a yüklenmedi). `python3 -B "$HOME/Downloads/ENGURU_P02_FIXED_FINISH_PREFLIGHT_V1.zip" --self-test` ardından `--observe`: G3 politika/karar ve gerçek runtime SHA pins; Mac source transfer ZIP SHA; altı kapının kesin native kriter ve blocker receipt'i AudiV13'e yeni dosya olarak. Kaynak veya gerçek yetki otomatik PASS sayılmaz. Sadece salt-okunur; canonical, signer, Keychain, app, git yazımı yok.

**İki aşamalı tek kapanış teslimi**: 1) Mac native preflight receipt; 2) aynı receipt ve gerçek kaynak koduyla PR #190'da bütünleşik uygulama ve bağımsız karşıt sınama; 3) yetkili native production operations for 01–06 in one bounded acceptance package **only after prerequisites**. Gerçek Mac accepted receipts olmadan `BITTI_DUR` yok.

**STATE:** FIXED_FINISH_BOUNDARY_LOCK_CANDIDATE / NATIVE_G3_A_TO_D_HOLD / P02_0_OF_12_HOLD / VERIFIED_FINISH_HOLD.
