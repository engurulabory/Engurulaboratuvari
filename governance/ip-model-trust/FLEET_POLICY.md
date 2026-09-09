# ENGÜRÜ IP & MODEL TRUST FLEET POLICY™ v1.0

## State
ACTIVE — applies to every repository and work surface governed by ENGÜRÜ Labory.

## Locked rule
No Engürü repository, product, core, experiment, release mirror or control-plane change may claim Verified Finish unless its repository declares an IP classification manifest and passes the fleet security gate.

## Mandatory controls
1. Every governed repository MUST contain `.enguru/ip-model-trust.json`.
2. Every governed repository MUST run the Fleet Security Gate on pull requests and pushes to its canonical branch.
3. Secret Zero Rule™ is fail-closed. Detected credentials, private keys, tokens or passwords BLOCK the gate.
4. Unknown or malformed classification metadata BLOCKS the gate.
5. T4 Crown Jewel assets are Local-First. Cloud disclosure requires explicit Human Threshold™ evidence and minimum-disclosure treatment outside this repository gate.
6. T5 Restricted material MUST NOT be sent to general-purpose cloud models.
7. Repository security PASS proves repository enforcement only; it does not prove any external model provider's privacy or training policy.
8. Provider trust upgrades require current first-party evidence in MODEL_REGISTRY.json.

## Required manifest
```json
{
  "schemaVersion": "1.0",
  "governedBy": "ENGURU_IP_MODEL_TRUST_GATE_V1",
  "repository": "owner/repo",
  "defaultIpClass": "T3",
  "crownJewelPaths": [],
  "restrictedPaths": [],
  "humanThresholdRequiredForT4Cloud": true
}
```

## Fleet verdict
PASS — manifest valid + no Secret Zero violation.
HOLD — human/provider evidence is required for a T4 cloud disclosure decision.
BLOCKED — secrets, T5 misuse, missing/invalid manifest, or unknown governance contract.

## DoneCheck™
Repository-level security is complete only when:
- manifest exists and validates;
- CI gate executes;
- CI is green on the candidate commit;
- changes are merged to the canonical branch;
- central inventory records adoption status.
