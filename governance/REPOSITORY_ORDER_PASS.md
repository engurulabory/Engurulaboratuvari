# Repository Order Pass™

## Purpose
Run alongside ENGÜRÜ PRODUCT & CORE MAP™ and convert discovery into a safe repository-order plan.

## Non-destructive phase only
Until Product & Core Map reaches PASS:

- do not delete repositories;
- do not merge repositories;
- do not rename canonical products;
- do not move large code surfaces;
- do not retire products;
- do not rewrite repository history.

Allowed before map completion:

- read/search/fetch;
- add inventory records;
- add missing documentation;
- record canonical pointers;
- identify duplicates and stale structures;
- open issues/PRs for review;
- add non-destructive manifests when their truth is verified.

## Steward checks per repository

1. repository purpose is explicit;
2. product/core classification is explicit;
3. canonical source/path is known;
4. README reflects current truth;
5. `.enguru/labory-manifest.json` exists where applicable;
6. governance contract link is current;
7. evidence and DoneCheck paths are discoverable;
8. release/deployment truth is separated from claims;
9. secrets are absent from repository content;
10. stale branches/docs are identified, not silently removed;
11. duplicate capabilities are mapped;
12. archive candidates are evidence-backed.

## Output
For every finding, Steward records:

`state → claim → evidence → next action`

Actions are tagged:

- SAFE_AUTO — non-destructive documentation/metadata order
- REVIEW — architecture or ownership judgment
- HUMAN_THRESHOLD — rename, merge, delete, retire, payment/publish/legal or irreversible external effect

## DoneCheck gate
Repository Order Pass can only close when Product & Core Map is PASS and all high-impact actions are either completed with evidence or explicitly held at Human Threshold.
