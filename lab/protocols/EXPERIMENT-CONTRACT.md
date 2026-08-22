# Experiment Contract

Every solver experiment must declare before execution:

- hypothesis;
- baseline solver commit/version;
- one primary treatment/change;
- target model and exact generation settings;
- task split and task IDs or manifest hash;
- maximum attempts per task;
- API/compute budget;
- primary metric and secondary diagnostics;
- success threshold;
- falsification conditions.

After execution record:

- exact solved/total and accuracy;
- new solves versus baseline;
- regressions versus baseline;
- calls, input/output tokens and runtime when observable;
- failure clusters;
- whether the effect survives a matched ablation;
- verdict: `PROMOTE`, `REJECT`, `INCONCLUSIVE`, or `INFRA_ONLY`.

Never change several unrelated variables and attribute the total delta to one idea.
