# ENGÜRÜ Five Minute Controller — pilot adapter

State: **STAGED / PR ONLY / NO SCHEDULE RUNNING**. Linked worklist: Issue #192.

This reuses the existing ENGÜRÜ Closed-Loop Production Core, Language Governance, Süzgeç, Management, Engineering and DoneCheck authorities. No new verification core.

Management selects at most one eligible task; Engineering executes only allowlisted, read-only SHA-256 file observation; Management independently rechecks the actual source. Results produce a deterministic receipt. Owner retains Human Threshold authority.

**Release safety:** Editable flags are insufficient for activation. The scheduled path always returns `HOLD_GUVENLI_DUR` until canonical B1-signed DoneCheck receipt verification is implemented and tested. An open PR does not enable GitHub's default-branch scheduled workflow.

**Current limitations:** This is a read-only, isolated pilot. Autonomous code generation, persistent task leases, GitHub issue writeback, cross-repo commands, and Verified Finish receipt authentication are follow-on evidence-gated integrations; they are not claimed in this PR.
