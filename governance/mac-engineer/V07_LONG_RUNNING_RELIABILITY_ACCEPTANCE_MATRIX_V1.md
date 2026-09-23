# ENGÜRÜ Mac Engineering™ v0.7 — Long-Running Reliability Acceptance Matrix v1

**State:** CANONICAL ACCEPTANCE CONTRACT  
**Objective:** `V0_7_LONG_RUNNING_RELIABILITY`  
**Engineering mode:** GitHub-first → one consolidated Mac milestone commissioning  
**Authority:** Existing v0.5/v0.6 reliability truth + DoneCheck v1.2 authority model  
**Rule:** Mevcut hakikat + gerekli fark. Reuse → extend → adapter → new core.

## 1. BASELINE TRUTH REUSED

v0.5 already establishes the reliability foundation:

- task/reliability state machine;
- checkpoint/resume foundation;
- recovery classification and rollback basis;
- idempotency foundation;
- single-writer foundation.

v0.6 already establishes verified field behavior:

- checkpoint → restart → same-task resume PASS;
- bounded recovery field proof PASS;
- real Mac engineering task 7/7 VERIFIED PASS;
- Local Evidence Bundle VERIFIED PASS;
- Mandatory DoneCheck PASS;
- v0.6 VERIFIED FINAL / LOCKED.

v0.7 therefore extends duration, repetition, interruption diversity, concurrency pressure and Evidence continuity. It does not create a parallel reliability architecture.


## 2026-09-23 — EFFECTIVE MAC-NATIVE AUTHORITY RECONCILIATION

The original GitHub-first acceptance rows remain historical Evidence for the engineering path already executed. The current effective finish path is reconciled to **ENGÜRÜ Mac-Native Engineering Authority™** because GitHub Actions execution is externally blocked by the provider billing state.

This reconciliation preserves the truth boundary:

- GitHub A09 external PASS is **not manufactured** from local Evidence;
- GitHub A09 remains **EXTERNAL_BLOCKED / DEFERRED** and must be reconciled when external execution becomes available;
- local engineering continuity and local Verified Finish proceed through the locked 13-gate Mac-native contract;
- Mac becomes primary engineering execution authority only after local gates 8–13 and Human Threshold™ PASS.

Effective remaining sequence:

`Gate 8 Multi-Repo Local Field Proof → Gate 9 Restart/Recovery → Gate 10 Offline/GitVault Reconciliation → Gate 11 DoneCheck™ v1.2 Migration Verification → Gate 12 ≥8h Consolidated Mac Campaign + Final Verify → Gate 13 Human Threshold™ + Authority Transition`

The original A09/A10/A11 GitHub-first sequence below is retained as historical specification context; where it conflicts with this reconciliation, **this effective Mac-native authority section governs the current v0.7 finish path**.

## 2. EXACT ACCEPTANCE MATRIX

| Gate | Capability | GitHub-first acceptance | Milestone Mac acceptance | Required Evidence |
|---|---|---|---|---|
| V07-A01 | Long-run task-state correctness | Deterministic fixture executes at least **1,000 governed task-state transitions**. Every transition is schema-valid, task identity remains stable, terminal states remain terminal, and final persisted state reconciles with the journal/checkpoint truth. | Same canonical task model remains coherent throughout the consolidated campaign. | CI receipt + transition summary + persisted-state digest |
| V07-A02 | Durable resume across interruption | Three canonical interruption classes are exercised: **before durable commit**, **after checkpoint commit**, **after durable side-effect receipt**. Each class runs at least **10 repetitions**. Resume returns to the same governed task and chooses the latest valid durable state/LKG path. | At least one real runtime/app restart resumes the same task from durable truth. | fixture receipts + checkpoint/LKG lineage + task-id continuity |
| V07-A03 | Idempotency stress | The same idempotency key/work unit is replayed at least **100 times**. PASS requires **exactly one durable side effect** and a deterministic replay result for the remaining attempts. | Repeated user/runtime resume preserves the same exactly-once durable outcome. | idempotency ledger summary + side-effect count |
| V07-A04 | Single-writer / concurrency safety | At least **16 concurrent contenders** target the same task mutation boundary. PASS requires one canonical writer at a time, consistent persisted state, and deterministic outcomes for all contenders. | Real runtime remains coherent when app/runtime control paths overlap during the campaign. | lock/writer receipts + final-state digest |
| V07-A05 | Bounded retry / watchdog | Retry behavior is read from the canonical runtime policy. Total attempts remain bounded by **1 + configured retry limit**. Watchdog expiry produces one governed terminal/recovery decision and a traceable reason. | A real transient-failure case demonstrates bounded recovery or bounded HOLD without an open-ended loop. | retry trace + watchdog receipt + terminal reason |
| V07-A06 | Provider / network / process recovery | Deterministic fixtures cover **provider unavailable**, **network timeout**, and **child-process exit**. Each class includes one recoverable path and one exhausted path. Task identity and durable Evidence remain continuous. | Consolidated campaign includes at least one real interruption from the runtime/process/network surface available on the Mac. | fault-fixture receipts + recovery classification |
| V07-A07 | Resource discipline | CI stress fixture completes without uncontrolled temporary/cache accumulation. Every created runtime artifact is either canonical durable state/Evidence or is reclaimed by the defined cleanup path. | Campaign duration is **at least 8 hours**. After warm-up, peak RSS remains **≤ 2.0×** the warm baseline and final RSS remains **≤ 1.5×** the warm baseline; runtime cache/temporary artifacts reconcile at closeout. | resource samples + storage reconciliation |
| V07-A08 | Evidence continuity across restart | Every tested restart chain preserves canonical task id, checkpoint lineage, attempt/restart sequence and before/after evidence linkage. Structured Evidence remains machine-verifiable. | Local Evidence bundle covers the full campaign from start receipt through final closeout. | Evidence manifest + hashes + restart lineage |
| V07-A09 | GitHub CI fault-injection campaign | The targeted v0.7 reliability suite completes **5 consecutive PASS runs** on the exact candidate head, followed by one full product regression PASS and diff/scope validation. | Not applicable until the milestone candidate is exact-main accepted. | five targeted run IDs + full regression run ID |
| V07-A10 | DoneCheck v1.2 milestone integration | Every V07-A01…A09 criterion has a machine-readable acceptance result and Evidence reference. An inconclusive criterion resolves to HOLD. | Mac campaign output is consumed by Mandatory DoneCheck JSON → DoneCheck v1.2. | DoneCheck verification receipt |
| V07-A11 | Consolidated Mac long-run commissioning | Begins only after GitHub engineering candidate is exact-main accepted. | One campaign, **≥ 8 hours**, includes at least **3 controlled interruption events** spanning available runtime/process/network classes; task/evidence continuity remains reconciled and idempotent effects remain exactly-once. | Local campaign bundle + event timeline + final reconciliation |
| V07-A12 | Human Threshold™ / version lock | Engineering evidence is complete before human authority. | Human Threshold reviews the verified campaign and final DoneCheck result. | Human decision receipt + canonical lock update |

## 3. PASS CONTRACT

v0.7 engineering candidate can advance to Mac commissioning when:

`V07-A01…A10 = PASS`

and the candidate is accepted on exact-main.

v0.7 can become **VERIFIED / LOCKED** only when:

`A01…A10 PASS → exact-main → A11 PASS → DoneCheck v1.2 PASS → A12 Human Threshold → canonical reconciliation`

Any criterion with insufficient Evidence remains **HOLD**. A real execution blocker is **BLOCKED**.

## 4. REQUIRED DIFFERENCE

The matrix converts the existing v0.5/v0.6 reliability foundations into measurable v0.7 acceptance gates.

No new core is required.

Next engineering package:

`V07-A01 + V07-A02 → LONG_RUN_TASK_STATE_AND_DURABLE_RESUME`
