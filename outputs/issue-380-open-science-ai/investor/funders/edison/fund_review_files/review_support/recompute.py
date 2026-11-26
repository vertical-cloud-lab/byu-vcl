#!/usr/bin/env python3
"""Recompute the supplied funder-list review. CSV rows are logical records: header=1.
Run from the directory containing FUNDERS.md and the seven supplied CSV files.
No web access or changes to original inputs. Requires pandas and numpy.
"""
from pathlib import Path
import json, hashlib
import pandas as pd
import numpy as np
ROOT=Path.cwd(); OUT=ROOT/'review_support'; OUT.mkdir(exist_ok=True)
files=['investors.csv','investor_links.csv','deals.csv','ventures.csv','programs.csv','source_checks_deals.csv','edison_audit_comparison.csv']
tables={f:pd.read_csv(ROOT/f,dtype=str).fillna('') for f in files}
for d in tables.values(): d.insert(0,'csv_row',np.arange(len(d))+2)
I,L,D,V,P,C,A=[tables[f] for f in files]
lines=(ROOT/'FUNDERS.md').read_text().splitlines()
checks=[]
def check(section,entity,measure,reported,actual,line=''):
    checks.append(dict(line=line,section=section,entity=entity,measure=measure,reported=reported,recomputed=actual,status='verified' if reported==actual else 'mismatch'))
def record(section,entity,measure,actual):
    checks.append(dict(line='',section=section,entity=entity,measure=measure,reported='',recomputed=actual,status='recomputed'))
def cells(s): return [x.strip() for x in s.strip().strip('|').split('|')]
Ln=L.assign(led_n=L.led.astype(int))
allcounts=L.groupby('investor').key.nunique();allleads=Ln[Ln.led_n>0].groupby('investor').key.nunique()
basecounts=L[L.universe!='U4'].groupby('investor').key.nunique();baseleads=Ln[(Ln.universe!='U4')&(Ln.led_n>0)].groupby('investor').key.nunique()
u4counts=L[L.universe=='U4'].groupby('investor').key.nunique();u4leads=Ln[(Ln.universe=='U4')&(Ln.led_n>0)].groupby('investor').key.nunique()
expanded=[]
for r in D[D.counted=='yes'].to_dict('records'):
    leads={s.strip() for s in r['lead'].split('|') if s.strip()}
    names=leads|{s.strip() for s in r['investors'].split('|') if s.strip()}
    for name in names:
        expanded.append({**{k:r[k] for k in ['csv_row','key','venture','universe','type','date','amount_usd']},'investor':name,'is_lead':name in leads})
E=pd.DataFrame(expanded)
early=E[E.type.isin(['pre_seed','seed','angel','accelerator','series_a'])].groupby('investor').agg(early_events=('csv_row','nunique'),led_events=('is_lead','sum'),ventures=('key','nunique'))
for lo,hi,sec,counts,leads in [(80,119,'U1-U3 leaders',basecounts,baseleads),(128,147,'U4 leaders',u4counts,u4leads),(216,240,'Corporate arms',allcounts,allleads),(254,265,'Accelerators',allcounts,allleads),(271,300,'Angels',allcounts,allleads),(308,327,'Growth and state',allcounts,allleads)]:
    for n in range(lo,hi+1):
        r=cells(lines[n-1])
        if len(r)<4 or not r[2].isdigit():continue
        for label,k,s in [('ventures',2,counts),('led_ventures',3,leads)]:
            if r[k].isdigit():check(sec,r[0],label,int(r[k]),int(s.get(r[0],0)),n)
for n in range(333,363):
    r=cells(lines[n-1])
    if len(r)<4 or not r[2].isdigit():continue
    for label,k,col in [('early_events',2,'early_events'),('early_leads',3,'led_events')]:
        check('Early rounds (record counts)',r[0],label,int(r[k]),int(early.loc[r[0],col]),n)
for n in range(166,192):
    r=cells(lines[n-1])
    if len(r)>=3 and r[-1].isdigit():check('Thesis table counts',r[0],'ventures',int(r[-1]),int(allcounts.get(r[0],0)),n)
for n in range(199,211):
    r=cells(lines[n-1]);arms=[a.strip() for a in r[1].split(',')]
    check('Parent rollups',r[0],'ventures',int(r[2]),L[L.investor.isin(arms)].key.nunique(),n)
lt=L.merge(I[['investor','type']],on='investor',how='left')
order=['venture_firm','corporate_venture','angel','accelerator','growth_pe_hedge','public_investor','philanthropy','government_grant','crowdfunding','crypto_fund_or_dao','bank_or_debt','other','unclassified']
for n in range(155,159):
    r=cells(lines[n-1]);x=lt[lt.universe==r[0]]
    check('Type mix',r[0],'links',int(r[1]),len(x),n)
    for k,typ in enumerate(order,2):
        check('Type mix',r[0],typ,int(r[k].strip('%') or '0'),int(round(100*sum(x.type==typ)/len(x))),n)
for label,unis in [('U1-U3',['U1','U2','U3']),('U1-U4',['U1','U2','U3','U4'])]:
    v=V[V.universe.isin(unis)];l=L[L.universe.isin(unis)];d=D[D.universe.isin(unis)];ct=l.groupby('investor').key.nunique()
    metrics={'ventures':len(v),'funding_found_yes':sum(v.funding_found=='yes'),'funders':len(ct),'links':len(l),'singletons':sum(ct==1),'funders_ge5':sum(ct>=5),'top10_link_sum':ct.nlargest(10).sum(),'top10_link_share':ct.nlargest(10).sum()/len(l),'event_rows':len(d),'counted_event_rows':sum(d.counted=='yes'),'counted_event_4field_groups':len(d[d.counted=='yes'].drop_duplicates(['key','date','type','amount_usd']))}
    for k,value in metrics.items():record('Headline recomputation',label,k,value)
check('Bottom line','U1-U3','ventures',640,len(V[V.universe!='U4']),21)
check('Bottom line','U1-U3','funded',448,sum((V.universe!='U4')&(V.funding_found=='yes')),22)
check('Bottom line','U1-U3','funders',1697,len(basecounts),23)
check('Bottom line','U1-U3','funding events (counted CSV records)',1320,sum((D.universe!='U4')&(D.counted=='yes')),23)
check('Bottom line','U1-U3','singletons',1294,sum(basecounts==1),24)
check('Bottom line','U1-U3','funders_ge5',102,sum(basecounts>=5),25)
check('Bottom line','U1-U3','top10 share rounded percent',9,round(100*basecounts.nlargest(10).sum()/sum(L.universe!='U4')),26)
for col in ['ours','edison','both']:record('Independent audit','40 ventures',col+'_sum',A[col].astype(int).sum())
tot=A[['ours','edison','both']].astype(int).sum()
for k,value in {'ours_overlap_share':tot['both']/tot['ours'],'edison_overlap_share':tot['both']/tot['edison'],'only_ours_sum':tot['ours']-tot['both'],'only_edison_sum':tot['edison']-tot['both'],'current_links_on_audited_keys':sum(L.key.isin(A.key)),'original_zero_funding_gaps':sum((A.ours=='0')&(A.edison!='0'))}.items():record('Independent audit','40 ventures',k,value)
for k,value in C.check.value_counts().items():record('Source checks','all',k,value)
record('Source checks','fetchable','text_fraction',sum(C.check=='found')/sum(C.check!='unavailable'))
record('Source checks','fetchable','text_or_markup_fraction',sum(C.check.isin(['found','in page markup (logo or link)']))/sum(C.check!='unavailable'))
for u in ['U1','U2','U3','U4']:
    v=V[V.universe==u];l=L[L.universe==u];ct=l.groupby('investor').key.nunique()
    for k,value in {'ventures':len(v),'funding_found_yes':sum(v.funding_found=='yes'),'no_funding_found':sum(v.funding_found=='none_found'),'bootstrapped_stated':sum(v.funding_found=='bootstrapped_stated'),'funders_ge3':sum(ct>=3)}.items():record('Universe counts',u,k,value)
for k,value in P.funds_companies.value_counts().items():record('Programs','funds_companies',k,value)
for k,value in I.type_source.value_counts().items():record('Investor typing','type_source',k,value)
for label,x in [('all',L),('U1-U3',L[L.universe!='U4']),('U2',L[L.universe=='U2'])]:
    y=x[x.database_only!='1']
    for k,value in {'links':len(x),'links_without_database_only_flag':len(y),'funders':x.investor.nunique(),'funders_without_database_only_flag':y.investor.nunique()}.items():record('Source sensitivity',label,k,value)
venturemap={'u4-comfyui':'Comfy-Org','u4-danswer':'onyx-dot-app','u4-embedchain':'mem0ai','u4-pynecone':'reflex-dev','u4-aitable':'u4-apitable','u4-zinc':'u4-zincsearch'}
lc=L.assign(canonical_key=L.key.replace(venturemap)).drop_duplicates(['investor','canonical_key'])
record('Six duplicate venture pairs','all','distinct_ventures',V.key.replace(venturemap).nunique());record('Six duplicate venture pairs','all','links',len(lc))
for name in ['Y Combinator','Guillermo Rauch','Paul Copplestone','Lux Capital','Olivier Pomel']:
    record('Six duplicate venture pairs',name,'ventures',lc[lc.investor==name].canonical_key.nunique())
casegroups={}
for n in I.investor:casegroups.setdefault(n.casefold(),[]).append(n)
aliasgroups=[['Sapphire Ventures','SAP Ventures'],['Partech','Partech International']]+[g for g in casegroups.values() if len(g)>1]
fmap={name:group[0] for group in aliasgroups for name in group}
lm=L.assign(canonical_investor=L.investor.replace(fmap)).drop_duplicates(['canonical_investor','key'])
for label,x in [('all',lm),('U1-U3',lm[lm.universe!='U4'])]:
    record('Nine conservative investor alias merges',label,'funders',x.canonical_investor.nunique());record('Nine conservative investor alias merges',label,'links',len(x))
wrong=[846,864,898,899,900,901,902,933]
ex=E[~E.csv_row.isin(wrong)].drop_duplicates(['investor','key'])
record('Eight excluded acquisition/IPO records','all','remaining_links',len(ex));record('Eight excluded acquisition/IPO records','all','remaining_funders',ex.investor.nunique())
# These are separate sensitivities, not a purported fully cleaned final database.
rawlinks=set(map(tuple,E[['investor','key']].drop_duplicates().to_numpy()))
publishedlinks=set(map(tuple,L[['investor','key']].to_numpy()))
assert rawlinks==publishedlinks
for col,fn in [('ventures',lambda x:x.key.nunique()),('U1',lambda x:sum(x.universe=='U1')),('U2',lambda x:sum(x.universe=='U2')),('U3',lambda x:sum(x.universe=='U3')),('led_ventures',lambda x:sum(x.led.astype(int)>0)),('rounds',lambda x:x['rounds'].astype(int).sum()),('database_only_links',lambda x:x.database_only.astype(int).sum())]:
    actual=L.groupby('investor').apply(fn,include_groups=False)
    assert (I[col].astype(int).to_numpy()==I.investor.map(actual).to_numpy()).all(),col
pd.DataFrame(checks).to_csv(OUT/'audit_checks.csv',index=False)
# Full ranking and metadata are supporting, not an endorsed cleaned dataset.
rank=L.groupby('investor').key.nunique().rename('ventures_all').to_frame().join(basecounts.rename('ventures_U1_U3')).fillna(0).astype(int).sort_values('ventures_all',ascending=False)
rank.to_csv(OUT/'recomputed_rankings.csv')
(OUT/'input_sha256.json').write_text(json.dumps({f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files+['FUNDERS.md','PROTOCOL.md']},indent=2))
print(pd.DataFrame(checks).groupby(['section','status']).size().to_string())
print('Wrote',OUT/'audit_checks.csv')
