# ENGÜRÜ Mac Engineer™ v0.6 — Product Exact-Main + Rebuild Preflight

Date: 2026-09-21

## STATE

**PRODUCT EXACT-MAIN CI + REBUILD PREFLIGHT — PASS**

## Product exact-main

- repository: `engurulabory/enguru-mac-engineer`
- local HEAD: `28b901ab3303f4be3c7356b11218b62422f2da42`
- local origin/main: same
- remote main: same
- private repository: true
- default branch: main

Product CI:

- run id: `35645771602`
- run number: 3
- event: push
- exact head SHA: `28b901ab3303f4be3c7356b11218b62422f2da42`
- status: completed
- conclusion: success

## Fresh rebuild/install preflight

- state: PASS
- issues: 0
- target version: 0.6
- product source version: 0.6
- product source build version: 0.6
- canonical runtime mapping: true
- historical runtime mapping present: false

Runtime source parity:

- product files: 27
- current runtime files: 27
- exact: 27
- changed: 0
- missing current: 0
- current only: 0

Current installed app remains:

- version: 0.4
- executable SHA-256: `168d9560148bb61e20b05aa7abea2a0546f7b23568551e8724997fd2e2c5c784`

## JUDGMENT

The canonical v0.6 product source is exact-main, CI-verified and build-ready. Current runtime source already matches the canonical product source exactly. Only the native installed app remains on v0.4.

## NEXT ACTION

Build the native app from exact product SHA `28b901ab…`, preserve rollback copies, install the built v0.6 bundle, launch it, verify live runtime/app provenance, and write field Evidence.
