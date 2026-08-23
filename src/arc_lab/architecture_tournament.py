from __future__ import annotations
import argparse, json, hashlib
from dataclasses import asdict
from pathlib import Path
from typing import Any
from .scoring import task_solved
from .target_model import CachedTargetClient, GenerationConfig, NvidiaNIMProvider, TargetRequest
from .taskio import load_task

MODEL='deepseek-ai/deepseek-v4-flash-0731'; PROVIDER='nvidia-nim'
SOLVER_VERSION='hypothesis-train-replay-v1'
GENERATION=GenerationConfig(temperature=0.0,top_p=1.0,top_k=None,max_output_tokens=4096)
TASK_IDS=['00dbd492','05f2a901','0607ce86','06df4c85','070dd51e','0bb8deee','0d3d703e','1190bc91']

def protocol_manifest()->dict[str,Any]:
 p={'schema_version':1,'run':'ARC-R017','role':'reasoning-systems-inventor','hypothesis':'Requiring DeepSeek to state a transformation hypothesis and replay it on every training input, then accepting its test grid only when those replay grids exactly match every training output, will improve exact accuracy over the frozen ARC-R016 direct-JSON comparator on the same eight deterministic dev_validation tasks without changing model or generation budget.','primary_variable':'structured hypothesis + exact training-replay verification gate','frozen_comparator':'ARC-R016 nvidia-direct-json-baseline-v1','provider':PROVIDER,'model':MODEL,'solver_version':SOLVER_VERSION,'generation':asdict(GENERATION),'attempts_per_test':1,'split':'dev_validation','selection_rule':'first eight lexicographically ordered IDs from frozen ARC-R016 dev_validation manifest','task_ids':TASK_IDS,'primary_metric':'exact task accuracy versus ARC-R016 on identical IDs','secondary':['new solves','regressions','verification pass rate','parse failures','provider failures','tokens','runtime'],'success_threshold':'PROMOTE only if treatment has at least one new solve and strictly more solved tasks than comparator with no public-eval use','falsification':'REJECT if treatment does not strictly beat comparator; INCONCLUSIVE only for missing coverage/provider failure that prevents matched comparison','public_evaluation_used':False,'exposure_note':'Known ARC-specific foundation-model exposure is not independently established; interpret as competition utility.'}
 raw=json.dumps(p,sort_keys=True,separators=(',',':')).encode(); p['manifest_sha256']=hashlib.sha256(raw).hexdigest(); return p

def prompt(task,test_input):
 return '''Solve this ARC task. Infer one concise transformation rule. Then REPLAY that same rule on every training input. Return JSON only with exactly these keys: "rule", "train_predictions", "test_output". train_predictions must be a list of output grids in training-example order. test_output must be one grid. No markdown. Your test_output will be accepted only if every train_predictions grid exactly equals its known training output.\n\nTRAINING:\n'''+json.dumps(task['train'],separators=(',',':'))+'\n\nTEST INPUT:\n'+json.dumps(test_input,separators=(',',':'))

def parse(text):
 try:
  s=text.strip(); s=s[s.find('{'):s.rfind('}')+1]; obj=json.loads(s)
  return obj if isinstance(obj,dict) else None
 except Exception:return None

def run(training_dir:Path, baseline_path:Path, cache_dir:Path, output:Path):
 base=json.loads(baseline_path.read_text()); base_by={r['task_id']:r for r in base['records']}
 client=CachedTargetClient(NvidiaNIMProvider(),cache_dir); records=[]; calls=hits=inp=out=tot=pf=parsef=verified_tests=0; runtime=0.0
 for tid in TASK_IDS:
  task=load_task(training_dir/f'{tid}.json',require_test_outputs=True); preds=[]; tests=[]
  for i,pair in enumerate(task['test']):
   req=TargetRequest(model=MODEL,prompt=prompt(task,pair['input']),solver_version=SOLVER_VERSION,task_id=f'{tid}:test{i}',attempt_index=0,generation=GENERATION)
   try:
    r=client.generate(req); calls+=0 if r.cache_hit else 1; hits+=int(r.cache_hit); inp+=r.input_tokens or 0; out+=r.output_tokens or 0; tot+=r.total_tokens or 0; runtime+=r.runtime_seconds
    obj=parse(r.text); parsef+=int(obj is None); verified=False; grid=None
    if obj is not None and isinstance(obj.get('train_predictions'),list) and isinstance(obj.get('test_output'),list):
     verified=obj['train_predictions']==[x['output'] for x in task['train']]
     if verified: grid=obj['test_output']; verified_tests+=1
    preds.append([] if grid is None else [grid]); tests.append({'test_index':i,'verified':verified,'parsed':obj is not None,'cache_hit':r.cache_hit,'input_tokens':r.input_tokens,'output_tokens':r.output_tokens,'total_tokens':r.total_tokens,'runtime_seconds':r.runtime_seconds,'finish_reason':(r.provider_metadata or {}).get('finish_reason')})
   except Exception as e:
    pf+=1; preds.append([]); tests.append({'test_index':i,'error_type':type(e).__name__,'error':str(e)[:200]})
  expected=[x['output'] for x in task['test']]; solved=len(preds)==len(expected) and all(preds) and task_solved(preds,expected); b=bool(base_by[tid]['solved']); records.append({'task_id':tid,'baseline_solved':b,'treatment_solved':solved,'new_solve':solved and not b,'regression':b and not solved,'tests':tests})
 bs=sum(r['baseline_solved'] for r in records); ts=sum(r['treatment_solved'] for r in records); new=sum(r['new_solve'] for r in records); reg=sum(r['regression'] for r in records)
 verdict='PROMOTE' if ts>bs and new>=1 else ('INCONCLUSIVE' if pf else 'REJECT')
 report={'schema_version':1,'run':'ARC-R017','protocol':protocol_manifest(),'baseline_solved':bs,'treatment_solved':ts,'task_count':len(TASK_IDS),'baseline_accuracy':bs/len(TASK_IDS),'treatment_accuracy':ts/len(TASK_IDS),'new_solves':new,'regressions':reg,'verification_passed_tests':verified_tests,'parse_failures':parsef,'provider_failures':pf,'calls':calls,'cache_hits':hits,'input_tokens':inp,'output_tokens':out,'total_tokens':tot,'runtime_seconds':runtime,'records':records,'verdict':verdict,'adversarial_interpretation':'The verification gate may improve validity while suppressing correct test guesses when a model cannot reproduce all training outputs in the requested schema. Any delta on eight tasks is directional, not a full-split estimate.'}
 output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n'); return report

def main():
 p=argparse.ArgumentParser(); p.add_argument('training_dir',type=Path); p.add_argument('--baseline',type=Path,required=True); p.add_argument('--cache-dir',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args(); r=run(a.training_dir,a.baseline,a.cache_dir,a.output); print(json.dumps({k:r[k] for k in ['baseline_solved','treatment_solved','new_solves','regressions','provider_failures','calls','total_tokens','runtime_seconds','verdict']},sort_keys=True))
if __name__=='__main__':main()
