"""Prospective, inference-only E7 extension. Historical inputs remain read-only."""
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import sys, json, hashlib, gzip, subprocess, time
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

ROOT = Path(r'C:\Users\Mete\Desktop\KARAKUTU3.0')
DEST = ROOT / '_COWORK' / 'faz_e'
PREFIX = 'E7_GOZLEM_KAYBI_20261008'
SEEDS = [42,43,44,45,46]
ARMS = ['merkezi','fedavg','fedprox_gercek']
PILLARS = ['CDSA-BB3','CDSA-ATM','CDSA-MRO']
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def utc(): return datetime.now(timezone.utc).isoformat()
def write(p,obj):
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def repo(pillar): return ROOT/pillar/'12_GitHub_Repo'/pillar.lower()
def inputs():
    paths=[]
    for pillar in PILLARS:
        r=repo(pillar)
        paths+=list((r/'src').rglob('*.py'))
        paths+=list((r/'data').glob('*.json'))
        paths += [r/'experiments'/n for n in ['faz_a_config.py','faz_a_staged.py','faz_b_robustness.py','faz_e_kayit.py','faz_e_kampanya.py']]
        paths += list((r/'experiments'/'results'/'e_kayit').glob('*.json'))
        for arm in ARMS:
            paths += [r/'experiments'/'results'/f'params_e7_{arm}_t{s}.json' for s in SEEDS]
    return sorted(set(paths))
def plan():
    path=DEST/f'{PREFIX}_ONKAYIT.json'
    assert not path.exists(), 'Never overwrite a prospective plan'
    obj={'created_utc':utc(),'code_sha256':sha(__file__),'human_instruction':'E1/E2/E7/E9 feasible work and new document versions',
         'scope':'Five-seed inference robustness on existing E5/E6 checkpoints; no retraining; not all historical E7 arms.',
         'excluded':'E1 maintenance modalities, E2 action-dependent dynamics, E9 human coding and unknown inclusion probabilities are not fabricated.',
         'pillars':PILLARS,'arms':ARMS,'training_seeds':SEEDS,'evaluation':{'reps':3,'steps':600,'env_seeds':[942,943,944],'new_api_reset_seeds':[2026,2027,2028],'noise_seeds':[10000,10001,10002],
         'conditions':['clean','gauss_0.05','gauss_0.10','gauss_0.20','drop_0.05','drop_0.10','all modality drops defined in each actual config'],
         'condition_source':'Unmodified faz_b_robustness.conditions/perturb; underlying environment remains clean'},
         'inference':'deterministic argmax','primary':'macro F1 from pooled 1800-decision confusion matrix',
         'secondary':['critical recall','mean reward','accuracy'], 'statistics':{'unit':'training seed','paired':'condition minus clean within the same trained seed','confidence':.95,'bootstrap_resamples':20000,'bootstrap_seed':0,'rule':'If paired interval includes zero report not measured, never equivalence','multiplicity':'Pointwise exploratory intervals, no familywise significance claim','generalization':'Fixed synthetic evaluation observations, no independent real-world or human validation'},
         'historical_hashes':{str(p):sha(p) for p in inputs()},'outputs':{p:str(DEST/f'{PREFIX}_{p}_SONUC.json') for p in PILLARS}}
    write(path,obj)
    print(json.dumps({'plan':str(path),'protected_sources':len(obj['historical_hashes'])}))
def metrics(cm):
    c=np.asarray(cm,dtype=float); n=c.shape[0]
    den=c.sum(0)+c.sum(1)
    f=np.divide(2*np.diag(c),den,out=np.zeros(n),where=den>0)
    return {'macro_f1':float(f.mean()),'per_class_f1':f.tolist(),'accuracy':float(np.trace(c)/c.sum())}
def interval(values):
    v=np.asarray(values,dtype=float); rng=np.random.default_rng(0)
    b=v[rng.integers(0,len(v),(20000,len(v)))].mean(1)
    lo,hi=np.quantile(b,[.025,.975])
    return {'mean':float(v.mean()),'sd':float(v.std(ddof=1)),'ci95':[float(lo),float(hi)],'seed_values':v.tolist()}
def run(pillar):
    t0=time.monotonic(); plan_path=DEST/f'{PREFIX}_ONKAYIT.json'
    pr=json.loads(plan_path.read_text(encoding='utf-8'))
    assert pr['code_sha256']==sha(__file__)
    for p,h in pr['historical_hashes'].items():
        if f'\\{pillar}\\' in p: assert sha(p)==h,p
    r=repo(pillar); sys.path.insert(0,str(r/'experiments'));sys.path.insert(0,str(r))
    import faz_b_robustness as b
    import faz_a_config as cfg
    import faz_a_staged as staged
    result_path=DEST/f'{PREFIX}_{pillar}_SONUC.json'
    assert not result_path.exists()
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=r,capture_output=True,text=True)
    begin=utc(); records=[]; summary={}; reference_truths=None; checks=[]
    for arm in ARMS:
        summary[arm]={}; by_cond={}
        for seed in SEEDS:
            pf=staged.OUT/f'params_e7_{arm}_t{seed}.json'
            agent=staged.new_agent(seed);agent.set_params(staged._j2p(json.loads(pf.read_text(encoding='utf-8'))))
            for cname,kind,param in b.conditions():
                cm=np.zeros((cfg.N_ACTIONS,cfg.N_ACTIONS),dtype=int); rewards=[]; preds=[]; truths=[]; per_rep=[]
                for rep in range(b.EVAL_REPS):
                    env=cfg.make_env(b.SEED+900+rep)
                    s=staged.env_reset(env,seed=2026+rep) if cfg.NEW_STEP_API else staged.env_reset(env)
                    rng=np.random.default_rng(10000+rep);rcm=np.zeros_like(cm); reward=0.
                    for i in range(b.EVAL_STEPS):
                        obs=b.perturb(s,kind,param,rng);a=int(agent.act(obs,deterministic=True)[0])
                        s2,rv,done,info=staged.env_step(env,a); y=int(info[cfg.INFO_TRUE_KEY])
                        rcm[y,a]+=1;reward+=rv;preds.append(a);truths.append(y)
                        s=staged.env_reset(env) if done else s2
                    cm+=rcm;rewards.append(reward/b.EVAL_STEPS);per_rep.append(rcm.tolist())
                    if seed==42 and arm=='merkezi' and rep==0 and cname in ['clean','gauss_0.10','drop_0.10']:
                        original=b.eval_cond(agent,kind,param,rep)
                        assert original['confusion']==rcm.tolist()
                        assert abs(original['mean_reward']-reward/b.EVAL_STEPS)<1e-12
                        checks.append({'condition':cname,'legacy_function_exact':True})
                if reference_truths is None: reference_truths=truths
                assert truths==reference_truths, 'Identical clean truth sequence required'
                m=metrics(cm);critical=sorted(cfg.CRITICAL_ACTIONS);crit_total=int(cm[critical,:].sum())
                m.update(critical_recall=float(np.diag(cm)[critical].sum()/crit_total) if crit_total else None,
                         mean_reward=float(np.mean(rewards)))
                by_cond.setdefault(cname,[]).append(m)
                rid=f'{pillar}-E7-observation-{arm}-t{seed}-{cname}-20261008'
                records.append({'run_id':rid,'training_seed':seed,'arm':arm,'condition':cname,'checkpoint':str(pf),'checkpoint_sha256':sha(pf),
                    'git_commit':git.stdout.strip(),'plan_sha256':sha(plan_path),'code_sha256':sha(__file__),
                    'training_config_sources':{str(r/'experiments'/f):sha(r/'experiments'/f) for f in ['faz_a_config.py','faz_e_kampanya.py','faz_a_staged.py']},
                    'evaluation_config':{'reps':b.EVAL_REPS,'steps':b.EVAL_STEPS,'kind':kind,'param':param,'drop_indices':b.DROP_IDX.tolist()},
                    'data_sha256':hashlib.sha256(json.dumps(truths).encode()).hexdigest(),'predictions':preds,'true_labels':truths,
                    'confusion_matrix':cm.tolist(),'per_rep_confusion':per_rep,'metrics':m})
        for cname,vals in by_cond.items():
            entry={key:interval([v[key] for v in vals]) for key in ['macro_f1','critical_recall','mean_reward','accuracy']}
            d=interval([v['macro_f1']-c['macro_f1'] for v,c in zip(vals,by_cond['clean'])])
            d['difference_measured']=not(d['ci95'][0]<=0<=d['ci95'][1]);entry['paired_macro_f1_minus_clean']=d
            summary[arm][cname]=entry
    for p,h in pr['historical_hashes'].items():
        if f'\\{pillar}\\' in p: assert sha(p)==h,p
    pred_path=DEST/f'{PREFIX}_{pillar}_KOSULAR.json.gz'
    with gzip.open(pred_path,'wt',encoding='utf-8') as f:json.dump(records,f,ensure_ascii=False)
    obj={'pillar':pillar,'started_utc':begin,'completed_utc':utc(),'duration_seconds':time.monotonic()-t0,'plan':str(plan_path),'plan_sha256':sha(plan_path),
        'numpy_version':np.__version__,'python_version':sys.version,'historical_sources_unchanged':True,'run_count':len(records),'decisions_per_run':1800,
        'training_runs':0,'checkpoints':15,'summary':summary,'legacy_function_comparisons':checks,'predictions':str(pred_path),'predictions_sha256':sha(pred_path),
        'limitations':pr['statistics'],'original_training_records':[{str(p):sha(p)} for p in (r/'experiments'/'results'/'e_kayit').glob('*.json') if any(f'-{arm}-t{s}-' in p.name for arm in ARMS for s in SEEDS)]}
    write(result_path,obj)
    print(json.dumps({'pillar':pillar,'runs':len(records),'seconds':obj['duration_seconds'],'file':str(result_path)}))
if __name__=='__main__':
    if sys.argv[1]=='plan':plan()
    else:run(sys.argv[1])
