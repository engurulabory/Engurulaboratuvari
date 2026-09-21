# ENGÜRÜ Mac Engineer™ v0.6 — Rebuild/Install Preflight Evidence

Date: 2026-09-21

## STATE

**EXACT-SHA REBUILD/INSTALL PREFLIGHT — HOLD / REQUIRED DIFFERENCE IDENTIFIED**

## Verified truth

- Session Start: PASS
- Labory exact-main: `896dae54c8180129603bf6dae12b56715e7e799d`
- product source main: `3ac09bd7d022a6114b9066afca14ff170e0177c1`
- product source clean + exact origin/main: PASS
- canonical native build mapping: PASS
- historical runtime mapping present: false
- product/runtime source parity:
  - product files: 26
  - current runtime files: 27
  - exact: 26
  - changed: 0
  - missing current: 0
  - current-only: 1

## Required difference

1. Product `Info.plist` still declares:
   - `CFBundleShortVersionString = 0.4`
   - `CFBundleVersion = 0.4`

   Target: `0.6`.

2. Current runtime contains one source-like file not yet represented in the dedicated product source:

   `runtime/static/engineer-emblem.png`

This file is treated as a branding/source intake candidate before exact-SHA rebuild.

## Installed truth

Current installed app is still v0.4 and remains untouched by this preflight.

## JUDGMENT

No code drift was found across the 26 canonical runtime source files. Rebuild/install waits only for the minimal product-source alignment:

`version 0.4 → 0.6 + engineer-emblem.png source promotion`

## NEXT ACTION

Prepare a local product branch with only those two governed changes, run product verification, and commit locally. No push/merge/install in the preparation step.
