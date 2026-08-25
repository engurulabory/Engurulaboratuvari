const VERSION = "steward-commissioning-v1";
const OWNER = "engurulabory";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, state: "PASS", service: "ENGURU_LABORY_STEWARD", version: VERSION });
    }
    if (request.method === "GET" && url.pathname === "/commissioning/proof") {
      return json(await proof(env));
    }
    if (request.method === "POST" && url.pathname === "/commissioning/run") {
      if (!authorized(request, env)) return json({ ok: false, state: "BLOCKED", reason: "UNAUTHORIZED" }, 401);
      return json(await runCycle(env, "manual"));
    }
    return json({ ok: false, state: "HOLD", reason: "NOT_FOUND" }, 404);
  },

  async scheduled(controller, env, ctx) {
    ctx.waitUntil(runCycle(env, `cron:${controller.cron || "unknown"}`));
  }
};

async function runCycle(env, source) {
  const startedAt = now();
  const cycleId = `steward-hourly-${startedAt.slice(0, 13)}`;
  try {
    const repos = await discoverRepos(env);
    const digest = await sha256(JSON.stringify(repos.map(r => [r.full_name, r.updated_at, r.archived, r.fork]).sort()));
    const prior = await env.DB.prepare("SELECT inventory_digest, repo_count FROM steward_cycles ORDER BY finished_at DESC LIMIT 1").first();

    for (const repo of repos) {
      await env.DB.prepare(`INSERT INTO steward_inventory(repository,first_seen_at,last_seen_at,visibility,default_branch,archived,fork,updated_at,raw_json)
        VALUES(?,?,?,?,?,?,?,?,?)
        ON CONFLICT(repository) DO UPDATE SET last_seen_at=excluded.last_seen_at,visibility=excluded.visibility,default_branch=excluded.default_branch,archived=excluded.archived,fork=excluded.fork,updated_at=excluded.updated_at,raw_json=excluded.raw_json`)
        .bind(repo.full_name, startedAt, startedAt, repo.visibility || null, repo.default_branch || null, repo.archived ? 1 : 0, repo.fork ? 1 : 0, repo.updated_at || null, JSON.stringify(repo)).run();
    }

    const expected = parseExpected(env.EXPECTED_REPOSITORIES);
    const names = new Set(repos.map(r => r.full_name));
    const missingExpected = expected.filter(name => !names.has(name));
    const newlyChanged = prior && (String(prior.inventory_digest) !== digest || Number(prior.repo_count) !== repos.length);

    if (newlyChanged) {
      await addFinding(env, startedAt, "INVENTORY_CHANGED", null, "HOLD", { previous_digest: prior.inventory_digest, current_digest: digest, repo_count: repos.length });
    }
    for (const name of missingExpected) {
      await addFinding(env, startedAt, "EXPECTED_REPOSITORY_NOT_VISIBLE", name, "HOLD", { source });
    }

    const detail = {
      source,
      version: VERSION,
      repo_count: repos.length,
      expected_count: expected.length,
      missing_expected: missingExpected,
      inventory_changed: Boolean(newlyChanged),
      github_auth: env.GITHUB_TOKEN ? "TOKEN" : "PUBLIC_ONLY"
    };
    const status = missingExpected.length ? "HOLD" : "PASS";
    const finishedAt = now();
    await env.DB.prepare(`INSERT OR REPLACE INTO steward_cycles(cycle_id,started_at,finished_at,status,repo_count,inventory_digest,detail_json)
      VALUES(?,?,?,?,?,?,?)`).bind(cycleId, startedAt, finishedAt, status, repos.length, digest, JSON.stringify(detail)).run();
    return { ok: true, state: status, cycle_id: cycleId, started_at: startedAt, finished_at: finishedAt, ...detail };
  } catch (error) {
    const finishedAt = now();
    const detail = { source, version: VERSION, error: String(error) };
    await env.DB.prepare(`INSERT OR REPLACE INTO steward_cycles(cycle_id,started_at,finished_at,status,repo_count,inventory_digest,detail_json)
      VALUES(?,?,?,?,?,?,?)`).bind(cycleId, startedAt, finishedAt, "BLOCKED", 0, "ERROR", JSON.stringify(detail)).run();
    await addFinding(env, finishedAt, "RUNTIME_ERROR", null, "BLOCKED", detail);
    return { ok: false, state: "BLOCKED", cycle_id: cycleId, ...detail };
  }
}

async function discoverRepos(env) {
  const headers = { "accept": "application/vnd.github+json", "user-agent": "enguru-labory-steward/1.0", "x-github-api-version": "2022-11-28" };
  if (env.GITHUB_TOKEN) headers.authorization = `Bearer ${env.GITHUB_TOKEN}`;
  const endpoint = env.GITHUB_TOKEN
    ? "https://api.github.com/user/repos?per_page=100&affiliation=owner&sort=updated"
    : `https://api.github.com/users/${OWNER}/repos?per_page=100&type=owner&sort=updated`;
  const response = await fetch(endpoint, { headers });
  if (!response.ok) throw new Error(`GitHub discovery failed: ${response.status}`);
  const rows = await response.json();
  return rows.filter(r => String(r.owner?.login || "").toLowerCase() === OWNER);
}

async function proof(env) {
  const rows = (await env.DB.prepare("SELECT cycle_id,started_at,finished_at,status,repo_count,inventory_digest,detail_json FROM steward_cycles ORDER BY finished_at DESC LIMIT 24").all()).results || [];
  const pass = rows.filter(r => r.status === "PASS").length;
  const blocked = rows.filter(r => r.status === "BLOCKED").length;
  const latest = rows[0] || null;
  const distinctWindows = new Set(rows.map(r => String(r.cycle_id).replace("steward-hourly-", ""))).size;
  const observationPass = rows.length >= 24 && pass === 24 && distinctWindows >= 24;
  const state = blocked ? "BLOCKED" : observationPass ? "PASS" : "HOLD";
  const findings = (await env.DB.prepare("SELECT at,kind,repository,state,detail_json FROM steward_findings ORDER BY at DESC LIMIT 20").all()).results || [];
  return {
    ok: state !== "BLOCKED",
    state,
    version: VERSION,
    gates: {
      runtime_reachable: latest ? "PASS" : "HOLD",
      inventory_discovery: latest && latest.status !== "BLOCKED" ? "PASS" : latest ? "BLOCKED" : "HOLD",
      observation_24_hourly_cycles: observationPass ? "PASS" : "HOLD"
    },
    evidence: {
      hourly_cycles_seen: rows.length,
      hourly_cycles_pass: pass,
      hourly_cycles_blocked: blocked,
      distinct_hourly_windows: distinctWindows,
      latest_cycle: latest,
      recent_findings: findings
    }
  };
}

async function addFinding(env, at, kind, repository, state, detail) {
  await env.DB.prepare("INSERT INTO steward_findings(at,kind,repository,state,detail_json) VALUES(?,?,?,?,?)")
    .bind(at, kind, repository, state, JSON.stringify(detail || {})).run();
}

function parseExpected(value) {
  return String(value || "").split(",").map(v => v.trim()).filter(Boolean);
}

function authorized(request, env) {
  if (!env.STEWARD_CONTROL_TOKEN) return false;
  return request.headers.get("authorization") === `Bearer ${env.STEWARD_CONTROL_TOKEN}`;
}

function now() { return new Date().toISOString(); }
async function sha256(value) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, "0")).join("");
}
function json(value, status = 200) {
  return new Response(JSON.stringify(value), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "x-content-type-options": "nosniff" } });
}
