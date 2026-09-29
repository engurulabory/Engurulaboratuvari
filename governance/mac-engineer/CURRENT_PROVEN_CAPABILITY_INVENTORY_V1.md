# ENGÜRÜ Mac Engineer™ — Current Proven Capability Inventory v1

## STATE

This document records the current observed and proven capability inventory of
ENGÜRÜ Mac Engineer™ on OSi.

It is a capability truth surface, not a future roadmap.

Status vocabulary:

- `VERIFIED` — field or regression evidence exists.
- `VERIFIED_BOUNDED` — proven within defined engineering boundaries.
- `PARTIAL` — capability substrate exists, but end-to-end field proof is incomplete.
- `FIELD_TEST_REQUIRED` — mechanism or platform capability exists, but the exact user-facing behavior has not yet been field-proven.

---

## 1. CURRENT TECHNICAL TRUTH READ

**STATUS — VERIFIED**

Reads repository, branch, HEAD, working tree, roadmap, session state and current operator truth.

Typical use:

`enguru-mac status`

---

## 2. CANONICAL BOOT

**STATUS — VERIFIED**

Determines current version, current gate/objective, active authority and next required action.

Typical use:

Canonical boot runs inside operator workflows.

---

## 3. LOCAL DOCTOR

**STATUS — VERIFIED**

Checks local runtime, Git state, Evidence surfaces, GitVault and recovery prerequisites.

Typical use:

`enguru-mac doctor`

---

## 4. OPERATOR CONTINUE / NEXT ACTION DISPATCH

**STATUS — VERIFIED**

Selects the correct operator action from current canonical state or stops safely with HOLD.

Typical use:

`enguru-mac continue`

---

## 5. FAIL-CLOSED ENGINEERING

**STATUS — VERIFIED**

Stops when branch, authority, Evidence, state, test result or repository truth does not satisfy the contract.

Typical use:

Automatic operator behavior.

---

## 6. SOURCE / PRODUCT CHANGE

**STATUS — VERIFIED_BOUNDED**

Reads existing product truth and applies bounded necessary source changes.

Typical use:

Canonical objective
→ operator action
→ `enguru-mac continue`

---

## 7. BUILD

**STATUS — VERIFIED**

Runs real build workflows, including Mac-native / Swift build surfaces.

Observed substrate includes:

- `swift`
- `xcodebuild`
- local product build paths

---

## 8. TEST / REGRESSION

**STATUS — VERIFIED**

Runs targeted tests and full regression suites and does not manufacture PASS when tests fail.

Typical use:

Operator-controlled test execution.

---

## 9. ROOT-CAUSE REPAIR

**STATUS — VERIFIED**

Supports:

`READ → ROOT_CAUSE → SMALLEST_SUFFICIENT_CHANGE → TEST → REGRESSION`

Used repeatedly in real control-plane and product repairs.

---

## 10. MIGRATION / CANONICAL RECONCILIATION

**STATUS — VERIFIED**

Repairs mismatches between runtime context, repository truth, session state, canonical state and product lifecycle state.

---

## 11. ADVANCED CODE ENGINEERING

**STATUS — VERIFIED_BOUNDED**

Mac Engineer can:

- read source code;
- understand repository context;
- generate new source;
- modify existing source;
- implement bounded features;
- repair defects;
- build;
- run targeted tests;
- run full regression;
- reconcile architecture/state contracts;
- produce implementation Evidence.

Proven across real control-plane and product engineering work.

Boundary:

This status does not claim that every arbitrary software project can yet be autonomously completed without human or Second Look involvement.

---

## 12. NEW PRODUCT FROM BRIEF

**STATUS — VERIFIED_BOUNDED**

Can turn a bounded product brief into a real product implementation.

Field example:

`Local CSV Inspector`

Gate 8 demonstrated real product creation and verification from a bounded brief.

---

## 13. RELEASE LIFECYCLE

**STATUS — VERIFIED**

Supports controlled lifecycle operations including:

`RELEASE`
→ `RUNTIME VERIFY`
→ `REPLACEMENT`
→ `ROLLBACK`
→ `RECOVERY`
→ `PROVENANCE`

---

## 14. FINISHED PRODUCT DELIVERY ACCEPTANCE

**STATUS — VERIFIED**

Supports technical delivery acceptance and stops at Human Threshold™ where human authority is required.

---

## 15. EVIDENCE / DONECHECK™

**STATUS — VERIFIED**

Produces and verifies:

- receipts
- Evidence files
- SHA256 digests
- DoneCheck™ results
- canonical readbacks
- Human Threshold™ bindings

Does not treat an unsupported textual claim as proof.

---

## 16. RECOVERY / OFFLINE CONTINUITY

**STATUS — VERIFIED**

Supports:

- GitVault mirror
- restart/recovery
- offline reconciliation
- local authority continuity
- durable task/state recovery

Typical use:

`enguru-mac recover`

---

# CROSS-CUTTING OPERATOR SURFACES

## 17. TERMINAL / SHELL EXECUTION

**STATUS — VERIFIED**

Mac Engineer has a real local execution substrate.

Observed local tools include:

- `/bin/zsh`
- `/bin/bash`
- `python3`
- `git`
- `swift`
- `xcodebuild`
- `curl`
- `osascript`
- `open`
- `plutil`

Mac Engineer operator implementations execute local commands and use shell/process-backed engineering workflows.

Practical meaning:

Mac Engineer can use Terminal-level execution as part of its bounded engineering work.

This does not mean unrestricted arbitrary shell authority is automatically granted.
Canonical objective and authority boundaries still apply.

---

## 18. FILESYSTEM / FINDER / MACOS AUTOMATION

**STATUS**

`FILESYSTEM_OPERATIONS = VERIFIED`

`MACOS_AUTOMATION_SUBSTRATE = PRESENT`

`FINDER_GUI_OPERATOR = FIELD_TEST_REQUIRED`

Verified / observed substrate includes:

- filesystem read/write
- file creation and modification
- repository file operations
- local workspace operations
- `osascript`
- `open`
- `plutil`

Important distinction:

Filesystem capability is not the same as controlling the Finder graphical interface.

Current truth:

Mac Engineer can manipulate files through local filesystem/programmatic mechanisms.

Not yet field-proven:

Human-like Finder GUI navigation such as opening Finder, visually selecting an item, dragging, moving, renaming and confirming through the graphical interface.

---

## 19. INTERNET RESEARCH / HARVEST / LOCAL ASTRA

**STATUS**

`RESEARCH_HARVEST = VERIFIED`

`LOCAL_ASTRA_RUNTIME_HISTORY = PASS`

`HTTP_TRANSPORT_SUBSTRATE = PRESENT`

`GENERAL_BROWSER_OPERATOR = PARTIAL / FIELD_TEST_REQUIRED`

Observed capability includes:

- Research Harvest architecture and historical field verification
- Gate 8 Research / Verified Harvest lineage
- local Astra runtime PASS history
- local runtime/provider routing
- internet transport substrate such as `curl`
- research source collection / synthesis mechanisms

Important distinction:

Research Harvest is not identical to unrestricted human-like browser operation.

Current truth:

Mac Engineer has proven research/Harvest mechanisms and local Astra lineage.

Still requires explicit field proof:

- opening and navigating arbitrary websites;
- following multi-step browser UI flows;
- using Safari/Chrome as a general browser operator;
- handling login, forms and visual browser interaction end to end.

---

# HOW WE USE THESE CAPABILITIES

## Direct operator commands

```text
enguru-mac status
enguru-mac doctor
enguru-mac continue
enguru-mac verify
enguru-mac recover
```

## Engineering work model

Capabilities without a standalone CLI command run through the governed operator chain:

`HUMAN INTENT`
→ `CANONICAL OBJECTIVE`
→ `ACCEPTANCE BOUNDARY`
→ `OPERATOR ACTION`
→ `enguru-mac continue`
→ `EXECUTION`
→ `EVIDENCE`
→ `DONECHECK™`
→ `HUMAN THRESHOLD™ WHEN REQUIRED`
→ `VERIFIED RESULT`

---

# CURRENT FIELD-TEST BOUNDARIES

Fresh field verification is required before stronger authority is claimed for:

1. Finder graphical-interface operation.
2. General browser navigation.
3. Arbitrary live internet research outside already-proven Harvest paths.
4. Multi-step website interaction.
5. Natural-language intent → autonomous general engineering execution without a pre-authored operator action.

These are verification boundaries, not failure claims.

---

# GOVERNANCE

`STATE → CLAIM → EVIDENCE → JUDGMENT / NEXT ACTION`

`MEVCUT HAKİKAT + GEREKLİ FARK`

`REUSE → EXTEND → ADAPTER → NEW CORE`

No capability may be promoted beyond its current evidence level without fresh proof.

---

# CURRENT JUDGMENT

**CAPABILITY_COUNT — 19**

- Terminal execution — VERIFIED.
- Advanced code engineering — VERIFIED_BOUNDED.
- Filesystem operations — VERIFIED.
- Research Harvest — VERIFIED.
- Local Astra lineage — PASS.

Explicit field-verification boundaries:

- Finder GUI operator.
- General browser operator.
- unrestricted natural-language → autonomous work entry.

---

# NEXT ACTION

Run Package 01 Second Look against the canonical capability orchestration finish worklist.

Do not commit until Second Look returns PASS.
