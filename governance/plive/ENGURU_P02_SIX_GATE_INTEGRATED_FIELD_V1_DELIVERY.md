# ENGÜRÜ P02 — Six Gate Integrated Native Field V1

**Fixed boundary:** six native gates, 4 existing P02 packages / 12 items, 4 DoneChecks, 7 field prerequisites, independent security, separate Human Threshold, verified native finish. Süzgeç™ v2.4 remains eight stages. No new core or gate.

**Runnable attachment:** `ENGURU_P02_SIX_GATE_INTEGRATED_FIELD_V1.zip`, SHA-256 `28547658e10ad7b0bc822aebe3c32867731489d81f5e627d4c9e877e71744445`. ZIP bytes are delivered separately through ChatGPT and **are not committed to GitHub**.

**Simulation:** `python3 -B "$HOME/Downloads/ENGURU_P02_SIX_GATE_INTEGRATED_FIELD_V1.zip" --self-test` → `SELF_TEST=PASS_FIXED_SIX_GATES_FAIL_CLOSED` on package-build machine. Real Mac OSi has not yet run this package.

**Field operation:** `python3 -B "$HOME/Downloads/ENGURU_P02_SIX_GATE_INTEGRATED_FIELD_V1.zip" --run` reads exact pinned local policy, decision, OSi runtime, three historic signing records, writes a uniquely named JSON receipt to AudiV13, and reports exact native G3/P02 HOLD boundary. No Keychain, private key, signing, canonical P02 writer, item mutation, grant issuance or human approval.

**Crucial boundary:** This is an integrated **read-only field preflight and fail-closed simulation**, NOT an executable authorized production-transition package. The latter requires actual owner-qualified signer, pinned trust + signed exact grant, authoritative existing P02 state writer with nonce/CAS durable acceptance, native item readbacks and separate Human Threshold. Preflight PASS never converts native 0/6 or P02 0/12 into a PASS. Avoid extra readiness reports after this: focus real code/authority binding within six locked gates.

**Status:** INTEGRATED_FIELD_BUNDLE_READY / MAC_EXECUTION_PENDING / NATIVE_0_OF_6 / P02_0_OF_12 / VERIFIED_FINISH_HOLD.
