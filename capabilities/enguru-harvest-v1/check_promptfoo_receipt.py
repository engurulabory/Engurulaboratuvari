"""Inspect a real promptfoo CLI JSON receipt without false model-evaluation claims."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=HERE/"promptfoo-eval-output.json"
cfg=HERE/"promptfooconfig.json"
data=json.loads(p.read_text(encoding="utf-8"))
assert isinstance(data,(dict,list)) and len(p.read_bytes())>60
config=json.loads(cfg.read_text(encoding="utf-8"))
assert config["providers"]==["echo"]
assert len(config["tests"])==2
# The external CLI's exit code proves the assertions were met. This receipt
# only proves offline evaluator functionality; no LLM quality or user gain.
out={
  "schema":"enguru.harvest.p08-promptfoo-offline/v1",
  "state":"PASS_OFFLINE_ECHO_PROVIDER_CLI_UNREVIEWED",
  "config_sha256":hashlib.sha256(cfg.read_bytes()).hexdigest(),
  "output_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
  "test_count":2,
  "paid_api":0,
  "provider":"echo",
  "actual_model_used":False,
  "external_skill_proven":False,
  "osi_executed":False
}
(HERE/"promptfoo-offline-receipt.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps(out,sort_keys=True))
