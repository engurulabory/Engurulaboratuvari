# ENGÜRÜ Mac Engineering™ v0.6 — Archive Decision

Date: 2026-09-21

## STATE

**ARCHIVE DECISION — PASS / PRESERVE-FIRST**

The decision is intentionally non-destructive.

## Classification

### Historical handoff

`~/Desktop/ENGURU_Mac_Engineer_Project_Handoff_v1`

Decision: **PRESERVE AS PROVENANCE UNTIL v0.6 VERIFIED FINAL / LOCKED.**

Reason: it remains useful historical-source and build-continuity evidence. It is not canonical product source.

After v0.6 final closure it may be moved, without content mutation, to an archive location under:

`~/Enguru/Archive/MacEngineer/Provenance/`

### Exact-SHA install backups

`~/Enguru/Backup/MacEngineer/`

Decision: **RETAIN AS ROLLBACK + RECOVERY EVIDENCE.**

At minimum preserve:
- the backup used during the recovered first install attempt;
- the pre-v0.6 backup from the successful install retry.

No deletion is authorized during v0.6 closeout.

### Runtime build app

`~/Enguru/Runtime/MacEngineer/App/ENGÜRÜ Mac Engineer.app`

Decision: **KEEP ACTIVE GENERATED ARTIFACT.**

It is part of the verified current runtime/install provenance chain and matches the installed app native hash.

## Governance

- canonical source remains `engurulabory/enguru-mac-engineer`;
- runtime/build/backup/historical artifacts do not become source authority;
- destructive cleanup remains outside this closure;
- later cleanup is evidence-led and reversible.

## NEXT ACTION

**Real Mac Engineering Task.**
