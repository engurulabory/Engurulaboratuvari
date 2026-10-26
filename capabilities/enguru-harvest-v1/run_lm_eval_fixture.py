"""P12: real LM Evaluation Harness CLI against an offline dummy-model fixture.

Only tiny local JSONL is used. No downloaded model, API key or real model gain.
The pinned upstream library actually loads a task and performs an evaluation.
"""
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from importlib.metadata import version

HERE=Path(__file__).resolve().parent
def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    upstream_sha="d6de81643928d653435c431bae19945d41d32520"
    with tempfile.TemporaryDirectory(prefix="enguru-lm-eval-p12-") as temp:
        root=Path(temp)
        task_dir=root/"tasks"
        task_dir.mkdir()
        samples=root/"enguru_fixture.jsonl"
        data=[{"question":"ENGURU deterministic A:", "answer":"lol"},
              {"question":"ENGURU deterministic B:", "answer":"lol"}]
        samples.write_text("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in data),encoding="utf-8")
        config=task_dir/"enguru_offline_dummy.yaml"
        config.write_text(
            "task: enguru_offline_dummy\n"
            "dataset_path: json\n"
            "dataset_kwargs:\n"
            "  data_files:\n"
            f"    test: {json.dumps(str(samples))}\n"
            "output_type: generate_until\n"
            "test_split: test\n"
            "doc_to_text: '{{question}}'\n"
            "doc_to_target: '{{answer}}'\n"
            "generation_kwargs:\n"
            "  until: ['\\n']\n"
            "metric_list:\n"
            "  - metric: exact_match\n"
            "    aggregation: mean\n"
            "    higher_is_better: true\n",
            encoding="utf-8"
        )
        out=root/"output"
        out.mkdir()
        env=os.environ.copy()
        env.update({"HF_DATASETS_OFFLINE":"1","HF_HUB_OFFLINE":"1",
                    "TRANSFORMERS_OFFLINE":"1","WANDB_DISABLED":"true",
                    "DO_NOT_TRACK":"1"})
        command=["lm-eval","run","--model","dummy","--tasks","enguru_offline_dummy",
                 "--include_path",str(task_dir),"--limit","2","--num_fewshot","0",
                 "--output_path",str(out),"--seed","1"]
        trial=subprocess.run(command,text=True,capture_output=True,env=env,timeout=180)
        candidates=list(out.rglob("*.json"))
        reports=[]
        for p in candidates:
            try:
                obj=json.loads(p.read_text(encoding="utf-8"))
            except (OSError,ValueError):
                continue
            if isinstance(obj,dict) and "results" in obj:
                reports.append((p,obj))
        found=False
        score=None
        for path,obj in reports:
            outcomes=obj["results"]
            if isinstance(outcomes,dict) and "enguru_offline_dummy" in outcomes:
                found=True
                metrics=outcomes["enguru_offline_dummy"]
                if isinstance(metrics,dict):
                    for key,val in metrics.items():
                        if "exact_match" in key and type(val) in (float,int):
                            score=val
                            break
                break
        result={
            "schema":"enguru.harvest.p12-lm-harness-offline/v1",
            "state":"PASS_REAL_HARNESS_DUMMY_FIXTURE_UNREVIEWED" if trial.returncode==0 and found and score==1 else "HOLD_HARNESS_FIXTURE",
            "upstream_commit":upstream_sha,"installed_distribution":version("lm_eval"),
            "cli_exit":trial.returncode,"task_evaluated":found,"fixture_sample_count":2,
            "exact_match":score,"dataset_sha256":sha(samples.read_bytes()),
            "task_yaml_sha256":sha(config.read_bytes()),
            "output_report_count":len(reports),
            "stdout_tail":trial.stdout[-1500:],"stderr_tail":trial.stderr[-2500:],
            "no_external_model":True,"api_calls":0,"osi_execution":0,
            "real_model_gain":"HOLD","independent_review":"HOLD",
            "official_proven":"HOLD"
        }
        (HERE/"lm-eval-harness-receipt.json").write_text(
            json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
            encoding="utf-8")
        print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        if result["state"].startswith("HOLD"):
            raise SystemExit(1)

if __name__=="__main__":
    main()
