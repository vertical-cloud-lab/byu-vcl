from pathlib import Path
import json, hashlib
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportion_confint
import statsmodels.formula.api as smf

BASE=Path(__file__).resolve().parent
ROOT=BASE/'inputs' if (BASE/'inputs').exists() else BASE.parent
OUT=BASE; OUT.mkdir(exist_ok=True)
c=pd.read_csv(ROOT/'companies_master.csv'); e=pd.read_csv(ROOT/'events.csv')
SEED=3802026; B=12000; rng=np.random.default_rng(SEED)
valid_types=['market_cap','private_valuation','acquisition_price']
commercial_status=['private_vc','public','acquired','private_bootstrapped','private_pe','defunct']
c['valid_value']=c.latest_value_type.isin(valid_types)&(c.latest_value_usd>0)
c['eligible_commercial']=c.ownership_status.isin(commercial_status)&c.category.ne('ai_for_science_model')
c['expanded_commercial']=~c.ownership_status.isin(['nonprofit','government','foundation'])&~c.category.isin(['ai_for_science_model','foundation','open_infrastructure'])
c['value_usd']=c.latest_value_usd.where(c.valid_value)
c['multiple']=c.value_usd/c.funding_total_usd.where(c.funding_total_usd>0)
for label,kinds in {'acquisition':['acquisition'],'take_private':['take_private'],'shutdown':['shutdown'],'bankruptcy':['bankruptcy'],'failure':['shutdown','bankruptcy'],'ipo':['IPO']}.items():
 c[label]=c.slug.isin(e.loc[e.kind.isin(kinds),'slug']).astype(int)
c['current_acquired']=c.ownership_status.eq('acquired').astype(int)
c['current_private_pe']=c.ownership_status.eq('private_pe').astype(int)
c['current_defunct']=c.ownership_status.eq('defunct').astype(int)
c['value_date_parsed']=pd.to_datetime(c.latest_value_date,format='mixed',errors='coerce')
c['value_age_years']=(pd.Timestamp('2026-11-23')-c.value_date_parsed).dt.days/365.25
c['cohort_decade']=(c.founded_year-2000)/10
c['log_value']=np.log10(c.value_usd)
c['log_multiple']=np.log10(c.multiple)
c['delta_open']=c.openness_current-c.openness_initial
c['physical_analogue']=c.group.isin(['D','E','F','G'])

def ci_median(x):
 x=np.asarray(pd.Series(x).dropna(),float)
 if not len(x):return (np.nan,np.nan)
 z=np.median(rng.choice(x,size=(B,len(x)),replace=True),axis=1)
 return tuple(np.quantile(z,[.025,.975])) if len(x)>1 else (np.nan,np.nan)
def summary(d,keys,label):
 rows=[]
 for key,g in d.groupby(keys,dropna=False):
  key=key if isinstance(key,tuple) else (key,)
  r=dict(zip(keys,key));r['sample']=label;r['n']=len(g)
  r['funding_n']=int((g.funding_total_usd>0).sum());r['value_n']=g.value_usd.notna().sum();r['multiple_n']=g.multiple.notna().sum()
  for x in ['value_usd','multiple']:
   v=g[x].dropna();r[x+'_median']=v.median();r[x+'_q25']=v.quantile(.25);r[x+'_q75']=v.quantile(.75);r[x+'_mean']=v.mean();r[x+'_min']=v.min();r[x+'_max']=v.max()
   r[x+'_median_lo'],r[x+'_median_hi']=ci_median(v)
  for ev in ['acquisition','take_private','shutdown','bankruptcy','failure','ipo','current_acquired','current_private_pe','current_defunct']:
   k=int(g[ev].sum());r[ev+'_k']=k;r[ev+'_rate']=k/len(g);r[ev+'_lo'],r[ev+'_hi']=proportion_confint(k,len(g),method='wilson')
  rows.append(r)
 return pd.DataFrame(rows)
frames=[]
for label,d in [('all_rows',c),('commercial',c[c.eligible_commercial]),('expanded_commercial',c[c.expanded_commercial])]:
 for score in ['openness_current','openness_initial']:
  t=summary(d,[score],label);t.insert(1,'score_basis',score);t=t.rename(columns={score:'openness'});frames.append(t)
levels=pd.concat(frames,ignore_index=True);levels.to_csv(OUT/'openness_summary.csv',index=False)
sector=summary(c[c.eligible_commercial],['category'],'commercial');sector.to_csv(OUT/'sector_summary.csv',index=False)
frames=[]
for score in ['openness_current','openness_initial']:
 t=summary(c[c.eligible_commercial],['category',score],'commercial');t.insert(1,'score_basis',score);t=t.rename(columns={score:'openness'});frames.append(t)
pd.concat(frames,ignore_index=True).to_csv(OUT/'sector_openness_summary.csv',index=False)

# Explicitly selected comparison sets; confidence intervals describe resampling of these cases, not population identification.
comparisons=[]
samples={'commercial':c[c.eligible_commercial], 'expanded':c[c.expanded_commercial],
'commercial_no_bigtech':c[c.eligible_commercial & c.category.ne('big_tech')],
'commercial_2000plus':c[c.eligible_commercial & c.founded_year.ge(2000)],
'commercial_recent_values':c[c.eligible_commercial & (c.value_age_years<=2)],
'physical_D_E_F_G':c[c.eligible_commercial & c.physical_analogue],
'group_E':c[c.eligible_commercial & c.group.eq('E')]}
for sector_name in sorted(c.loc[c.eligible_commercial,'category'].unique()):
 samples['sector_'+sector_name]=c[c.eligible_commercial & c.category.eq(sector_name)]
for vt in valid_types:
 samples['value_type_'+vt]=c[c.eligible_commercial & c.latest_value_type.eq(vt)]
samples['commercial_not_low_confidence']=c[c.eligible_commercial & c.confidence.ne('low')]
zero=c[c.eligible_commercial].copy()
zero.loc[zero.bankruptcy.eq(1)&zero.funding_total_usd.gt(0),'multiple']=0
samples['bankrupt_zero_recovery_assumption']=zero
for name,d in samples.items():
 for score in ['openness_current','openness_initial']:
  for threshold in [2,3]:
   dd=d[d[score].notna()].copy();dd['open_group']=dd[score]>=threshold
   for outcome in ['multiple','value_usd','acquisition','take_private','shutdown','failure']:
    a=dd.loc[dd.open_group,outcome].dropna().to_numpy();b=dd.loc[~dd.open_group,outcome].dropna().to_numpy()
    r={'sample':name,'score_basis':score,'open_threshold':threshold,'outcome':outcome,'n_open':len(a),'n_closed':len(b)}
    if not len(a) or not len(b):comparisons.append(r);continue
    if outcome in ['multiple','value_usd']:
     r.update(open_median=np.median(a),closed_median=np.median(b),median_ratio=np.median(a)/np.median(b))
     sa=np.median(rng.choice(a,(B,len(a))),axis=1);sb=np.median(rng.choice(b,(B,len(b))),axis=1)
     r['ratio_lo'],r['ratio_hi']=np.quantile(sa/sb,[.025,.975]);u,p=stats.mannwhitneyu(a,b,alternative='two-sided')
     r['cliffs_delta']=2*u/(len(a)*len(b))-1;r['p_value']=p
     if min(len(a),len(b))<2:r['ratio_lo']=np.nan;r['ratio_hi']=np.nan
    else:
     r.update(open_k=int(a.sum()),closed_k=int(b.sum()),open_rate=a.mean(),closed_rate=b.mean(),risk_difference=a.mean()-b.mean())
     # Newcombe score interval for independent proportions; remains informative for zero-event groups.
     al,au=proportion_confint(a.sum(),len(a),method='wilson');bl,bu=proportion_confint(b.sum(),len(b),method='wilson')
     r['rd_lo']=r['risk_difference']-np.sqrt((a.mean()-al)**2+(bu-b.mean())**2)
     r['rd_hi']=r['risk_difference']+np.sqrt((au-a.mean())**2+(b.mean()-bl)**2)
     r['p_value']=stats.fisher_exact([[a.sum(),len(a)-a.sum()],[b.sum(),len(b)-b.sum()]]).pvalue
    comparisons.append(r)
pd.DataFrame(comparisons).to_csv(OUT/'contrasts_sensitivity.csv',index=False)

models=[]
for score in ['openness_current','openness_initial']:
 for outcome in ['log_multiple','log_value','acquisition','take_private','failure']:
  for spec in ['unadjusted','sector_cohort','sector_cohort_value_type']:
   if spec=='sector_cohort_value_type' and outcome not in ['log_multiple','log_value']:continue
   formula=f'{outcome} ~ {score}'
   if spec!='unadjusted':formula+=' + C(category) + cohort_decade'
   if spec=='sector_cohort_value_type':formula+=' + C(latest_value_type)'
   d=c[c.eligible_commercial].dropna(subset=[score,outcome]+(['founded_year'] if spec!='unadjusted' else [])).copy()
   model=smf.ols(formula,d).fit(cov_type='HC3')
   beta=model.params[score];lo,hi=model.conf_int().loc[score];p=model.pvalues[score]
   r={'score_basis':score,'outcome':outcome,'specification':spec,'n':int(model.nobs),'parameters':len(model.params),'beta':beta,'lo':lo,'hi':hi,'p_value':p,'r_squared':model.rsquared}
   if outcome.startswith('log_'):r.update(percent_change=(10**beta-1)*100,percent_lo=(10**lo-1)*100,percent_hi=(10**hi-1)*100)
   models.append(r)
pd.DataFrame(models).to_csv(OUT/'regression_results.csv',index=False)

# Missing-value bounds for simple thresholds (not population bounds).
missing=[]
for score in ['openness_current','openness_initial']:
 for threshold in [2,3]:
  d=c[c.eligible_commercial & c[score].notna()]
  for isopen,g in d.groupby(d[score]>=threshold):
   missing.append({'score_basis':score,'threshold':threshold,'open_group':isopen,'n':len(g),'value_n':g.value_usd.notna().sum(),'multiple_n':g.multiple.notna().sum(),'value_observation_rate':g.value_usd.notna().mean(),'multiple_observation_rate':g.multiple.notna().mean(),'recorded_failure_rate':g.failure.mean(),'failure_rate_if_all_missing_value_failed':((g.failure.eq(1))|g.value_usd.isna()).mean()})
pd.DataFrame(missing).to_csv(OUT/'missingness_bounds.csv',index=False)

# Population failure-rate sensitivity to omitted failures (assumes no omitted successes).
failbounds=[]
for score in ['openness_current','openness_initial']:
 d=c[c.eligible_commercial & c[score].notna()]
 for op,g in d.groupby(d[score]>=2):
  n=len(g);k=g.failure.sum()
  for target in [.1,.25,.5]:
   m=max(0,int(np.ceil((target*n-k)/(1-target))))
   failbounds.append({'score_basis':score,'open_group':op,'observed_n':n,'observed_failures':int(k),'target_failure_rate':target,'additional_unrecorded_failures_needed':m})
pd.DataFrame(failbounds).to_csv(OUT/'omitted_failure_sensitivity.csv',index=False)

# Capture vs distribution and outlier concentration.
concentration=[]
for group,d in [('all_valid_values',c[c.valid_value]),('commercial',c[c.eligible_commercial & c.valid_value]),('commercial_software',c[c.eligible_commercial & c.valid_value & c.category.eq('software')])]:
 vals=d.sort_values('value_usd',ascending=False)
 concentration.append({'sample':group,'n':len(vals),'sum_usd':vals.value_usd.sum(),'top1_share':vals.value_usd.head(1).sum()/vals.value_usd.sum(),'top3_share':vals.value_usd.head(3).sum()/vals.value_usd.sum(),'top5_share':vals.value_usd.head(5).sum()/vals.value_usd.sum(),'top3':';'.join(vals.slug.head(3))})
pd.DataFrame(concentration).to_csv(OUT/'concentration.csv',index=False)

# Exit event and licensing alignment checks.
events_audit=e.merge(c[['slug','category','eligible_commercial','openness_initial','openness_current']],on='slug',how='left',validate='many_to_one')
events_audit.to_csv(OUT/'events_audit.csv',index=False)
# Most recent recorded pre-exit changes are only calendar-year ordered; no price/event causal regressions.
closing=e[e.kind.eq('relicense')&e.direction.eq('closing')].copy()
first_acq=e[e.kind.isin(['acquisition','take_private'])].groupby('slug').year.min()
closing['first_acq_or_takeprivate_year']=closing.slug.map(first_acq)
closing['at_or_after_first_acq_year']=closing.year>=closing.first_acq_or_takeprivate_year
closing.to_csv(OUT/'closing_event_audit.csv',index=False)

# Record-level denominator, source and data problems remain visible.
c.to_csv(OUT/'companies_analysis.csv',index=False)
issues={'rows':len(c),'model_release_rows':int(c.category.eq('ai_for_science_model').sum()),'eligible_commercial_n':int(c.eligible_commercial.sum()),'expanded_commercial_n':int(c.expanded_commercial.sum()),'nonvaluation_amounts':c.loc[c.latest_value_usd.notna()&~c.valid_value,'slug'].tolist(),'unknown_status_n':int(c.ownership_status.isna().sum()),'funding_missing_n':int(c.funding_total_usd.isna().sum()),'funding_zero_slugs':c.loc[c.funding_total_usd.eq(0),'slug'].tolist(),'events_rows':len(e),'events_missing_year_n':int(e.year.isna().sum()),'input_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['companies_master.csv','events.csv','SCHEMA.md','FINDINGS_BRIEF.md','RECOMMENDATIONS.md','suggested_proposal_language.md']},'seed':SEED,'bootstrap_replicates':B,'as_of':'2026-11-23'}
(OUT/'audit_metadata.json').write_text(json.dumps(issues,indent=2))
print(json.dumps(issues,indent=2))
print('\nCOMMERCIAL LEVEL SUMMARY\n',levels[levels['sample']=='commercial'][['score_basis','openness','n','value_n','multiple_n','value_usd_median','multiple_median','acquisition_k','take_private_k','shutdown_k','bankruptcy_k']].to_string(index=False))
print('\nSECTORS\n',sector[['category','n','value_n','multiple_n','value_usd_median','multiple_median','acquisition_k','take_private_k','failure_k']].to_string(index=False))
print('\nKEY COMPARISONS\n',pd.DataFrame(comparisons).query("sample=='commercial' & open_threshold==2").to_string(index=False))
print('\nMODELS\n',pd.DataFrame(models).to_string(index=False))
