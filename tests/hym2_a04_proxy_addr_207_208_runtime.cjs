"use strict";
// HYM2/A04 disposable Node package behavior regression, not customer installation.
// Uses npm exact releases in GitHub runner scratch directories; checks actual
// IPv4-mapped IPv6 trust matching, canonical /104 and the numeric first-hop
// trust callback used by the pinned Medusa source. Source-only evidence.
const assert = require("node:assert/strict");
const path = require("node:path");
const oldDir = process.argv[2], newDir = process.argv[3];
assert(oldDir && newDir, "Two isolated npm installation directories required");
const old = require(path.resolve(oldDir, "node_modules/proxy-addr"));
const fixed = require(path.resolve(newDir, "node_modules/proxy-addr"));
const oldMeta = require(path.resolve(oldDir, "node_modules/proxy-addr/package.json"));
const newMeta = require(path.resolve(newDir, "node_modules/proxy-addr/package.json"));
assert.equal(oldMeta.version, "2.0.7");
assert.equal(newMeta.version, "2.0.8");

const outside = "203.0.113.7";
const inside = "10.3.2.1";
const wrongPrefix = "::ffff:10.0.0.0/8";
const fullPrefix = "::ffff:10.0.0.0/104";
const oldBad = old.compile(wrongPrefix);
const newBad = fixed.compile(wrongPrefix);
const oldCorrect = old.compile(fullPrefix);
const newCorrect = fixed.compile(fullPrefix);
assert.equal(oldBad(outside, 0), true,
  "Historic source regression: misconfigured /8 trusts outside IPv4");
assert.equal(newBad(outside, 0), false,
  "Patched 2.0.8 must reject outside IPv4 for malformed mapped /8");
assert.equal(oldCorrect(inside, 0), true);
assert.equal(newCorrect(inside, 0), true);
assert.equal(oldCorrect(outside, 0), false);
assert.equal(newCorrect(outside, 0), false);

const req = {
  connection: {remoteAddress: "198.51.100.10"},
  headers: {"x-forwarded-for": "203.0.113.4, 10.1.1.5"}
};
const hop = (address, i) => i < 1;
assert.equal(old(req, hop), fixed(req, hop),
  "Medusa numeric first-hop style must preserve address interpretation");
assert.deepEqual(old.all(req, hop), fixed.all(req, hop));
console.log(JSON.stringify({
  state:"PASS_DISPOSABLE_NPM_VERSION_BEHAVIOR_ONLY",
  oldVersion:oldMeta.version, fixedVersion:newMeta.version,
  malformedMappedSubnetOutsideIPv4OldTrusted:true,
  malformedMappedSubnetOutsideIPv4PatchedTrusted:false,
  canonicalMappedSubnetInsideTrusted:true,
  numericHopBehaviorEqual:true,
  medusaRealInstall:"HOLD",
  a04Official:"HOLD",
  verifiedFinish:"HOLD"
}));
