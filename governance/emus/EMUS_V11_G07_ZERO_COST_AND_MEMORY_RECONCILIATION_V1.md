# EMÜS G07 — GH-09-C3 paid-route guard and 24 GiB OSi RAM budget

Date: 2026-10-24
State: ROUTER_NEGATIVE_CI_PASS / LIVE_END_TO_END_ZERO_PAID_HOLD

## Reviewed sources
- shared_ai/runtime.py: SharedAIRuntime._eligible checks production authority, verified privacy, commercial use and cost, SECRET local-only, estimated_cost <= request.cost_ceiling, capabilities and health.
- shared_ai/http_server.py: build_runtime_from_env() registers one local Ollama provider when ENGURU_LOCAL_ENABLED=1; model and commercial grant are explicit environment conditions. It does not register paid providers.
- engurulabory/enguru-mac-engineer review/emus-p1-source-pinned-integration-20261023 runtime/provider.py: Mac Engineer config probes Shared AI identity; chat uses local router HTTP /v1/enguru/respond and payload cost_ceiling=0, data_class=INTERNAL, required_capabilities text+reasoning. Note ENGURU_SHARED_AI_BASE_URL can be changed by environment; actual current OSi value requires field inspection.

## New adversarial CI
- tests/test_emus_g07_zero_cost_routes.py run 40076342529 PASS under Labory Final Gate, commit c9ba20189064f276afaead561553035496f093c9.
- Asserts explicit local provider registration, paid fallback after failed local invocation is skipped, all-paid candidates HOLD, SECRET external provider blocked, unapproved zero-cost provider blocked. Synthetic provider records used: no actual paid API invoked.

## Exact OSi field evidence, preserved
- EMUS_G07_OSI_20261024T070319Z.json SHA256 3376076390447c41f5b30c139541a5e3b6b6287fbbba305ff8fbafd65a9b2cab: installed Apache-2.0 license, model qwen3:14b Q4_K_M, 24 GiB installed RAM, 5.304s first probe response_match=false.
- EMUS_G07_OSI_V2_20261024T075239Z.json SHA256 ab0b6ed8d92ff49a3d45d94f81f1d02289bd8fe4d4bdac6a4b3b8ac51c5fad7e: full model digest bdbd181c33f2ed1b31c972991882db3cf4d192569092138a7d29e973cd9debe8; installed /api/ps size_vram=9,769,446,276 bytes (~9.10 GiB, ~40.7% of 24 GiB), response_match=true, 3.485s total, 8 tokens, eval_duration_ns=246214000.

## Resource decision
- 24 GiB total = 25,769,803,776 bytes. Ollama /api/ps reports 9,769,446,276 bytes allocated to loaded model, approximately 37.9% of byte total; equivalent 9.10 GiB / 24 GiB.
- Exact model size on disk from /api/tags: 9,276,198,565 bytes, approximately 8.64 GiB. Other Ollama /api/ps size may include runtime allocations.
- This is one-model loaded VRAM information, not an independent application peak RSS or guaranteed available RAM. Baseline/peak memory, memory pressure under simultaneous Swift app/runtime and swap effects require additional field evidence. No stable workload budget is accepted yet.

## Acceptance decision
GH-09-C3=HOLD_UNVERIFIED because deterministic zero-cost router negative tests PASS but current exact Mac field environment, runtime-to-router live cost evidence and any alternate fallback paths need independently collected real end-to-end evidence.
GH-09-C4=FIELD_EVIDENCED for real local inference and observed loaded model memory. Full product memory budget HOLD in separately tracked requirement.
No additional criteria counted in this packet. SUBCRITERIA=15/76, OFFICIAL_ACCEPTANCE=0/19, GITHUB_VERIFIED_FINISH=HOLD.
