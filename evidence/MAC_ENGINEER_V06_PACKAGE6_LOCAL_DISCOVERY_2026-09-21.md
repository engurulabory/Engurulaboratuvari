# ENGÜRÜ Mac Engineer™ v0.6 — Package 6 Mac Local Discovery / Exact-Main Sync Evidence

Date: 2026-09-21

## STATE

**EXACT_MAIN_SYNC — PASS**

**LOCAL RUNTIME — OBSERVED ACTIVE / PROVENANCE HOLD**

## Mac canonical checkout

Observed on the user's Mac:

- local HEAD: `e4f7670429ccdc57178065093f45ced83d07696f`
- origin/main: `e4f7670429ccdc57178065093f45ced83d07696f`
- branch: `main`
- worktree: clean
- platform Python: `Python 3.14.7`

Earlier local Shared AI edits were preserved before sync on:

- branch: `local/package6-preserve-20260921T201619`
- commit: `d3e5dca`
- changed files preserved: 4

## Discovered Mac Engineer runtime

Primary installed app candidate:

- path: `~/Applications/ENGÜRÜ Mac Engineer.app`
- bundle id: `com.engurumaya.macengineer`
- display name: `ENGÜRÜ Mac Engineer`
- executable: `EnguruMacEngineer`

Additional runtime candidate:

- `~/Enguru/Runtime/MacEngineer/App/ENGÜRÜ Mac Engineer.app`

Observed active processes:

- `~/Applications/ENGÜRÜ Mac Engineer.app/Contents/MacOS/EnguruMacEngineer`
- Python runtime: `~/Enguru/Runtime/MacEngineer/runtime/app.py`
- Shared AI: `python -m shared_ai.http_server`
- Ollama: `ollama serve`

## Local AI services

Shared AI health:

- HTTP 200
- state: PASS
- runtime: UP
- active providers: 1

Ollama:

- reachable: true
- model: `qwen3:14b`
- family: qwen3
- parameter size: 14.8B
- quantization: Q4_K_M
- context length: 40960
- capabilities: completion / tools / thinking

## Truth boundary

The runtime is real and active.

However, the canonical GitHub repository currently contains no source/provenance record matching:

- `EnguruMacEngineer`
- `com.engurumaya.macengineer`
- `Runtime/MacEngineer`
- `runtime/app.py`

Therefore Package 6 cannot yet claim:

`canonical GitHub source == currently running Mac Engineer binary/runtime`

This is the next required difference.

## JUDGMENT

- Exact-main sync: **PASS**
- Runtime existence: **PASS**
- Runtime active: **PASS**
- Shared AI local route: **PASS**
- Ollama/qwen3:14b availability: **PASS**
- Runtime provenance binding to canonical GitHub source: **HOLD**
- Real Mac engineering task: **HOLD / NEXT**
- Product-level v0.6 final: **HOLD**

## NEXT ACTION

Discover the installed Mac Engineer app/runtime provenance non-destructively. Bind the current app/runtime to an evidence-backed source/version identity before using it for the real Package 6 engineering task.
