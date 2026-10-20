# ENGÜRÜ — Native OSi runtime source-qualified integration finding V1

**Kaynak:** Mac salt-okunur `ENGURU_OSI_TWIN_G3_SOURCE_BINDING_V1.zip`, ZIP SHA-256 `1ecfb3e7771b292a70708711ae3ed6d2b9243acc97597e83abc84a7e7c436699`. Sekiz dosyanın tümü Mac receipt SHA pinleriyle eşleşti.

**Gerçek runtime kaynağı:** `source/tools/enguru_osi_runtime.py`, SHA-256 `195b6ce3f5451030862a0a5256985dff9f56746d8cbfacb64ec6621ffedeb80f`, 25,582 bayt. Bu belge GitHub'a aktarılmış kaynak kopyası değildir; yerel canonical içerik değiştirilmedi.

## Doğrudan kaynak inceleme sonuçları

- `atomic_json` (line 72–85): temporary file, flush/fsync(file), os.replace; dizin fsync'i ve CAS şartı görünmüyor.
- `append_journal` (line 88–113): chained previousHash/entryHash, append and fsync(file); durable nonce reservation veya canonical P02 CAS transaction'ı görünmüyor.
- `verify_journal` (line 116–133): hash-chain verification; bağımsız authenticity signature kanıtı değil.
- `LiveRuntime.acquire` (line 261–277): runtime.lock üzerinde flock. Bu kilidin P02 canonical progress writer ile ortak olduğu kanıtlanmadı.
- Runtime `steward_projection`/cycle/health ekran çıktıları oluşturur. Bu **P02 canonical item state mutator olduğu anlamına gelmez**. Mevcut yetkili writer bu kaynakta tanımlanmış kabul edilmeyecek.

## G3-C kararı

**`RUNTIME_PRIMITIVES=SOURCE_VERIFIED` / `CANONICAL_P02_WRITER_AUTHORITY=HOLD_NOT_SOURCE_BOUND`**.

Parallel second writer üretme, runtime append_journal'ı tek başına production nonce ledger ilan etme, separate JSON/journal atomikliğini varsayma, imzalı grant henüz yokken native item increment etme.

## Bütünleşik altı bağın gerçek ihtiyaçları

1. G3-A: real signing producer source→binary attestation, matching Team/Bundle/profile, Secure Enclave key + human-presence, independently authorized issuer.
2. G3-B: enrolled independent trust, revocation, exact scoped P02.S01.01 signed grant and non-replay.
3. G3-C: **mevcut P02 canonical progress producer/writer** exact SHA, call contract and authorized mutation path, with durable CAS/nonce/journal atomicity, crash/restart red-team. Runtime utility primitives can be harvested only after confirmed compatibility.
4. G3-D: human-authorized first native transition + real Progress Core before/after.
5. P02: 12/12 native, 4/4 DoneCheck, 7/7 prereqs, G03/G04, independent security.
6. Human: separate native Human Threshold ACCEPTED, VERIFIED Finish and BITTI_DUR.

**Hakikat:** P01 2/2 verified preserved. P02 0/12 HOLD. G3-A–D HOLD. Final HOLD. Source transfer success is not field authorization.

**NEXT ACTION:** Mevcut canonical P02 writer'ın authoritative source path ve doğrudan uygulama arayüzünü *aynı* entegre iş zincirine bağlamak; signer'da exact build producer/provisioning kanıtını karşıt sınamaya dahil etmek. GitHub PR #190 draft; no production mutations.
