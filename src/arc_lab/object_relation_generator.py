from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Any

from .compact_hypothesis_search import GENERATION_CANDIDATES, GENERATION_SELECTOR, MODEL, PROVIDER, TASK_IDS, parse_hypotheses, parse_selector, selector_prompt
from .target_model import CachedTargetClient, NvidiaNIMProvider, TargetRequest
from .taskio import load_task

RUN = "ARC-R021"
SOLVER_VERSION = "object-relation-candidates-v1"
BASELINE_COVERED = {"0bb8deee"}


def candidate_prompt(task: dict[str, Any], test_input: list[list[int]]) -> str:
    return (
        "Solve this ARC task by first reasoning in a compact OBJECT/RELATION representation: identify background, connected colored objects, each object's color/size/bounding box/shape, repeated motifs, containment/touching/alignment/symmetry, and which object relations change from input to output. "
        "Use that representation to propose exactly three DISTINCT transformation hypotheses. Favor object-level operations (select, move, copy, recolor, crop, reflect, complete, connect, count, overlay) when supported; include a pixel-level hypothesis only when object structure is insufficient. "
        "For each hypothesis return a short rule (max 240 characters) and resulting test_output grid. Do not output the intermediate scene graph and do not replay training outputs. Return JSON only with key hypotheses containing exactly three objects with keys rule and test_output. No markdown.\n\n"
        "TRAINING:\n" + json.dumps(task["train"], separators=(",", ":")) +
        "\n\nTEST INPUT:\n" + json.dumps(test_input, separators=(",", ":"))
    )


def _candidate_record(h: dict[str, Any], expected: list[list[int]]) -> dict[str, Any]:
    rule, grid = h["rule"], h["test_output"]
    return {"rule": rule, "rule_sha256": hashlib.sha256(rule.encode()).hexdigest(), "test_output": grid, "candidate_correct": grid == expected}


def run(training_dir: Path, cache_dir: Path, output: Path) -> dict[str, Any]:
    client = CachedTargetClient(NvidiaNIMProvider(), cache_dir)
    records=[]; calls=cache_hits=input_tokens=output_tokens=total_tokens=provider_failures=0; runtime_seconds=0.0
    for tid in TASK_IDS:
        task=load_task(training_dir/f"{tid}.json", require_test_outputs=True); tests=[]
        for i,pair in enumerate(task["test"]):
            tr={"test_index":i}; expected=pair["output"]
            try:
                req=TargetRequest(model=MODEL,prompt=candidate_prompt(task,pair["input"]),solver_version=SOLVER_VERSION+":candidates",task_id=f"{tid}:test{i}",attempt_index=0,generation=GENERATION_CANDIDATES)
                resp=client.generate(req); calls+=0 if resp.cache_hit else 1; cache_hits+=int(resp.cache_hit); input_tokens+=resp.input_tokens or 0; output_tokens+=resp.output_tokens or 0; total_tokens+=resp.total_tokens or 0; runtime_seconds+=resp.runtime_seconds
                hs=parse_hypotheses(resp.text); tr["candidate_stage"]={"parsed":hs is not None,"cache_hit":resp.cache_hit,"input_tokens":resp.input_tokens,"output_tokens":resp.output_tokens,"total_tokens":resp.total_tokens,"runtime_seconds":resp.runtime_seconds,"finish_reason":(resp.provider_metadata or {}).get("finish_reason")}
                if hs is None: tests.append(tr); continue
                cs=[_candidate_record(h,expected) for h in hs]; tr["candidates"]=cs; tr["candidate_set_has_correct"]=any(c["candidate_correct"] for c in cs)
                sreq=TargetRequest(model=MODEL,prompt=selector_prompt(task,[h["rule"] for h in hs]),solver_version=SOLVER_VERSION+":selector",task_id=f"{tid}:test{i}",attempt_index=0,generation=GENERATION_SELECTOR)
                sr=client.generate(sreq); calls+=0 if sr.cache_hit else 1; cache_hits+=int(sr.cache_hit); input_tokens+=sr.input_tokens or 0; output_tokens+=sr.output_tokens or 0; total_tokens+=sr.total_tokens or 0; runtime_seconds+=sr.runtime_seconds
                sel=parse_selector(sr.text); tr["selector_stage"]={"parsed":sel is not None,"selected_index":sel,"cache_hit":sr.cache_hit,"input_tokens":sr.input_tokens,"output_tokens":sr.output_tokens,"total_tokens":sr.total_tokens,"runtime_seconds":sr.runtime_seconds}; tr["selected_correct"]=None if sel is None else cs[sel]["candidate_correct"]
            except Exception as exc:
                provider_failures+=1; tr["error_type"]=type(exc).__name__; tr["error"]=str(exc)[:200]
            tests.append(tr)
        parseable=all(t.get("candidate_stage",{}).get("parsed") for t in tests); covered=parseable and all(t.get("candidate_set_has_correct",False) for t in tests); selected=parseable and all(t.get("selected_correct") is True for t in tests)
        records.append({"task_id":tid,"baseline_candidate_covered":tid in BASELINE_COVERED,"treatment_candidate_covered":covered,"selected_correct":selected,"new_candidate_coverage":covered and tid not in BASELINE_COVERED,"candidate_coverage_regression":tid in BASELINE_COVERED and not covered,"tests":tests})
    parseable=sum(all(t.get("candidate_stage",{}).get("parsed") for t in r["tests"]) for r in records); covered=sum(r["treatment_candidate_covered"] for r in records); selected=sum(r["selected_correct"] for r in records); new=sum(r["new_candidate_coverage"] for r in records); regressions=sum(r["candidate_coverage_regression"] for r in records)
    verdict="INCONCLUSIVE" if provider_failures else ("PROMOTE" if covered>=3 and new>=2 and regressions==0 else "REJECT")
    report={"schema_version":1,"run":RUN,"role":"object-centric-researcher","hypothesis":"Explicit compact object/relation reasoning before the same three-candidate generation step will raise candidate-oracle coverage from ARC-R020's 1/8 to at least 3/8 on the identical frozen slice without losing the prior covered task.","primary_variable":"object/relation representation instruction before candidate generation","frozen_comparator":"ARC-R020 compact-hypothesis-select-v1 candidate oracle","provider":PROVIDER,"model":MODEL,"solver_version":SOLVER_VERSION,"candidate_generation":{"temperature":0.0,"top_p":1.0,"max_output_tokens":3072},"selector_generation":{"temperature":0.0,"top_p":1.0,"max_output_tokens":512},"task_ids":TASK_IDS,"split":"dev_validation","public_evaluation_used":False,"baseline_candidate_covered_tasks":1,"treatment_parseable_tasks":parseable,"treatment_candidate_covered_tasks":covered,"treatment_selected_correct_tasks":selected,"new_candidate_coverage_tasks":new,"candidate_coverage_regressions":regressions,"success_threshold":"PROMOTE iff candidate coverage >=3/8, >=2 new covered tasks, and no loss of ARC-R020's covered task; provider failures => INCONCLUSIVE.","calls":calls,"cache_hits":cache_hits,"input_tokens":input_tokens,"output_tokens":output_tokens,"total_tokens":total_tokens,"runtime_seconds":runtime_seconds,"provider_failures":provider_failures,"records":records,"verdict":verdict,"adversarial_interpretation":"Prompt wording may help through extra semantic scaffolding rather than object-centric representation specifically; eight tasks are directional and object structure may not suit every ARC family."}
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n"); return report


def main():
    p=argparse.ArgumentParser(); p.add_argument("training_dir",type=Path); p.add_argument("--cache-dir",type=Path,required=True); p.add_argument("--output",type=Path,required=True); a=p.parse_args(); r=run(a.training_dir,a.cache_dir,a.output); print(json.dumps({k:r[k] for k in ["treatment_parseable_tasks","treatment_candidate_covered_tasks","treatment_selected_correct_tasks","new_candidate_coverage_tasks","candidate_coverage_regressions","calls","total_tokens","runtime_seconds","provider_failures","verdict"]},sort_keys=True))

if __name__=="__main__": main()
