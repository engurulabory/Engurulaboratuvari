import { execFileSync } from 'node:child_process';
import { readFileSync, statSync } from 'node:fs';
import { inspectWorkspaceHealth, STEWARD_SCOPES, STEWARD_VERSION } from './index.mjs';

function trackedFiles() {
  return execFileSync('git', ['ls-files', '-z'], { encoding: 'utf8' }).split('\0').filter(Boolean);
}

function textContents(files) {
  const out = [];
  for (const path of files) {
    try {
      const stat = statSync(path);
      if (!stat.isFile() || stat.size > 1000000) continue;
      out.push({ path, content: readFileSync(path, 'utf8') });
    } catch {}
  }
  return out;
}

const files = trackedFiles();
const result = inspectWorkspaceHealth({
  scope: STEWARD_SCOPES.LABORY,
  files,
  contents: textContents(files),
  workItems: [],
});

const receipt = {
  schemaVersion: '1.0',
  stewardVersion: STEWARD_VERSION,
  mode: 'READ_ONLY_SCHEDULED_CYCLE',
  destructiveActionsAllowed: false,
  repository: 'engurulabory/Engurulaboratuvari',
  observedAt: new Date().toISOString(),
  trackedFileCount: files.length,
  state: result.status,
  cycle: result.cycle,
  findings: result.repository?.findings ?? [],
};

console.log(JSON.stringify(receipt, null, 2));
if (result.status === 'BLOCKED') process.exit(3);
