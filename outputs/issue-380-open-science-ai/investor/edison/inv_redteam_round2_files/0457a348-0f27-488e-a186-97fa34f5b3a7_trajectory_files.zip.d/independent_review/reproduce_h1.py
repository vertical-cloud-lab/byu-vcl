#!/usr/bin/env python3
"""Recompute H1 from immutable raw listings and cached source observations.
Run: python reproduce_h1.py --output rerun
No network is needed. The supplied return table is used only for the original
snapshot's endpoint prices/benchmark ratios and four non-raw sensitivity names;
all returns, summaries and models are recomputed. Independent specifications use
cached Yahoo daily histories plus raw offer/deal terms instead.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--output', default='rerun')
parser.add_argument('--bootstrap', type=int, default=50000)
args = parser.parse_args()
DEST = Path(args.output)
if not DEST.is_absolute(): DEST = ROOT / DEST
DEST.mkdir(parents=True, exist_ok=True)
raw = pd.read_csv(ROOT/'inputs/cohort_listings_verified.csv')
ret = pd.read_csv(ROOT/'inputs/h1_returns.csv')
market_long = pd.read_csv(ROOT/'market_observations.csv', parse_dates=['date'])
market = {t:d.set_index('date').sort_index() for t,d in market_long.groupby('ticker')}

def price(series, date):
    return series.loc[:pd.Timestamp(date)].dropna().iloc[-1]

def metrics(frame):
    d = frame.copy()
    d['years'] = (pd.to_datetime(d.end_date)-pd.to_datetime(d.listing_date)).dt.days/365.25
    d['multiple'] = d.end_value_per_share/d.offer_price
    d['pme'] = d.multiple/d.qqq_multiple
    d['cagr'] = d.multiple**(1/d.years)-1
    d['q_cagr'] = d.qqq_multiple**(1/d.years)-1
    d['excess'] = d.cagr-d.q_cagr
    d['first_multiple'] = d.end_value_per_share/d.first_day_close
    d['first_pme'] = d.first_multiple/d.qqq_multiple
    d['first_excess'] = d.first_multiple**(1/d.years)-1-d.q_cagr
    d['igv_excess'] = d.cagr-(d.igv_multiple**(1/d.years)-1)
    d['log_pme'] = np.log(d.pme)
    d['year'] = pd.to_datetime(d.listing_date).dt.year
    return d

mapping = {'Pivotal Software':'Pivotal','MariaDB plc':'MariaDB',
'Domo (now Huckleberry.ai)':'Domo','Instructure (first listing)':'Instructure (2015 listing)',
'Instructure Holdings (second listing)':'Instructure (2021 listing)'}
r = raw.copy()
r['company'] = r.company.replace(mapping)
r['cohort'] = r.cohort.map({'open-source':'open_source','closed-source':'closed'})
d = r.merge(ret[['company','end_date','end_value_per_share','qqq_multiple','igv_multiple']],
            on='company', validate='one_to_one')
d['end_value_per_share'] = d.exit_price_per_share.fillna(d.end_value_per_share)
# Replication of original tax-basis shortcut, not an assumed actual investor trade.
d.loc[d.company.eq('SolarWinds'),'end_value_per_share'] = 18.5/2+1.5/2+1/2+.5*14.05
for i,row in d.iterrows():
    if pd.isna(row.first_day_close) and row.status.startswith('listed'):
        tick = 'HUCK' if row.company=='Domo' else row.ticker
        if pd.Timestamp(row.listing_date) in market[tick].index:
            d.loc[i,'first_day_close'] = market[tick].loc[row.listing_date,'close']
base_names = ret.loc[ret.cohort.isin(['open_source','closed']) & ret.company.ne('JFrog'),'company'].tolist()
rep = metrics(d[d.company.isin(base_names)])
assert len(rep)==39
# Independent common latest valid daily close. Nov24 daily closes in fetched feeds
# were null; metadata prices are deliberately not silently substituted for closes.
econ = d.copy()
econ.loc[econ.exit_price_per_share.isna(),'end_date'] = '2026-11-23'
for i,row in econ.iterrows():
    if pd.isna(row.exit_price_per_share):
        tick = 'HUCK' if row.company=='Domo' else row.ticker
        econ.loc[i,'end_value_per_share'] = price(market[tick].close,'2026-11-23')
    for bench,col in [('QQQ','qqq_multiple'),('IGV','igv_multiple')]:
        econ.loc[i,col] = price(market[bench].adjclose,econ.loc[i,'end_date'])/price(market[bench].adjclose,row.listing_date)
su = econ[econ.company.eq('SUSE')].iloc[0]
econ.loc[econ.company.eq('SUSE'),'end_value_per_share'] = 16*price(market['EURUSD=X'].close,su.end_date)/price(market['EURUSD=X'].close,su.listing_date)
econ.loc[econ.company.eq('SolarWinds'),'end_value_per_share'] = 18.5/2+1.5/2+1/2+.5*market['NABL'].loc['2021-07-20','close']
econ.loc[econ.company.eq('MuleSoft'),'end_value_per_share'] = 36+.0711*market['CRM'].loc['2018-05-02','close']
econ = metrics(econ)
legal = econ.copy()
for i,row in legal.iterrows():
    if pd.notna(row.exit_price_per_share): legal.loc[i,'end_date'] = row.exit_close_date
    for bench,col in [('QQQ','qqq_multiple'),('IGV','igv_multiple')]:
        legal.loc[i,col] = price(market[bench].adjclose,legal.loc[i,'end_date'])/price(market[bench].adjclose,row.listing_date)
su = legal[legal.company.eq('SUSE')].iloc[0]
legal.loc[legal.company.eq('SUSE'),'end_value_per_share'] = 16*price(market['EURUSD=X'].close,su.end_date)/price(market['EURUSD=X'].close,su.listing_date)
legal = metrics(legal)

sc = {}
sc['A: memo snapshot, raw offer/deal reconstruction'] = rep.copy()
allrep = metrics(d)
sc['B: JFrog counted as open-origin'] = allrep[allrep.company.isin(base_names+['JFrog'])].copy()
z = sc['B: JFrog counted as open-origin'].copy();z.loc[z.company.eq('JFrog'),'cohort']='closed'
sc['C: JFrog counted as closed'] = z
extras=[]
for co,tick in [('Tenable','TENB'),('UiPath','PATH'),('C3.ai','AI'),('Amplitude','AMPL')]:
    row=ret[ret.company.eq(co)].iloc[0]
    extras.append({'company':co,'ticker':tick,'cohort':'open_source' if co=='Tenable' else 'closed',
    'listing_date':row.listing_date,'offer_price':row.offer_price,'first_day_close':row.first_day_close,
    'end_date':row.end_date,'end_value_per_share':row.end_value_per_share,
    'qqq_multiple':row.qqq_multiple,'igv_multiple':row.igv_multiple,'status':'listed'})
sc['D: all memo late additions (not rule-complete)'] = metrics(pd.concat([d[d.company.ne('JFrog')],pd.DataFrame(extras)],ignore_index=True))
z=rep.copy();z['multiple']=z.first_multiple;z['pme']=z.first_pme;z['excess']=z.first_excess;z=z.dropna(subset=['excess']);z['log_pme']=np.log(z.pme)
sc['E: first-day close entry']=z
z=rep.copy();z['pme']=z.multiple/z.igv_multiple;z['log_pme']=np.log(z.pme);z['excess']=z.igv_excess
sc['F: IGV benchmark']=z
z=rep.copy();ix=z.company.eq('Hortonworks');z.loc[ix,'end_value_per_share']=1.305*16;z.loc[ix,'end_date']='2021-10-08'
for bench,col in [('QQQ','qqq_multiple'),('IGV','igv_multiple')]:
    z.loc[ix,col]=price(market[bench].adjclose,'2021-10-08')/price(market[bench].adjclose,'2014-12-12')
sc['G: hold Hortonworks through Cloudera exit']=metrics(z)
sc['H: exclude SPAC/reference-price entries']=rep[~rep.company.isin(['MariaDB','AvePoint','Palantir'])].copy()
years=set(rep[rep.cohort.eq('open_source')].year)&set(rep[rep.cohort.eq('closed')].year)
sc['I: overlapping listing years only']=rep[rep.year.isin(years)].copy()
sc['J: narrow infrastructure interpretation']=rep[~rep.company.isin(['MobileIron','Jamf','Appian','Unity Software'])].copy()
sc['K: exclude EU-only SUSE (US symmetry)']=rep[rep.company.ne('SUSE')].copy()
sc['L: independent Nov23 quotes + USD SUSE']=econ[econ.company.isin(base_names)].copy()
sc['M: raw legal dates, Nov23 quotes, USD SUSE']=legal[legal.company.isin(base_names)].copy()
miss=[]
for co,tick,date,offer in [('Rackspace Technology','RXT','2020-08-05',21),('Kingsoft Cloud','KC','2020-05-08',17)]:
    hist=market[tick]
    miss.append({'company':co,'cohort':'closed','ticker':tick,'listing_date':date,
    'offer_price':offer,'first_day_close':hist.loc[date,'close'],'end_date':'2026-11-23',
    'end_value_per_share':price(hist.close,'2026-11-23'),
    'qqq_multiple':price(market['QQQ'].adjclose,'2026-11-23')/price(market['QQQ'].adjclose,date),
    'igv_multiple':price(market['IGV'].adjclose,'2026-11-23')/price(market['IGV'].adjclose,date),'status':'listed'})
sc['N: independent prices plus Rackspace and Kingsoft Cloud']=metrics(pd.concat([sc['L: independent Nov23 quotes + USD SUSE'],pd.DataFrame(miss)],ignore_index=True))
z=sc['L: independent Nov23 quotes + USD SUSE'].copy();z.loc[z.company.eq('SolarWinds'),'end_value_per_share']=18.5/2+1.5/2+1/2+.5*market['NABL'].loc['2025-04-16','close']
sc['O: hold NABL until SolarWinds cash exit']=metrics(z)
z=rep.copy()
for row in pd.read_csv(ROOT/'first_day_overrides.csv').itertuples():
    z.loc[z.company.eq(row.company),'first_day_close']=row.first_day_close
z=metrics(z);z['multiple']=z.first_multiple;z['pme']=z.first_pme;z['excess']=z.first_excess;z['log_pme']=np.log(z.pme)
sc['P: first-day entry, both missing closes sourced']=z

rng=np.random.default_rng(20261125)
rows=[]
for name,z in sc.items():
    aa=z.loc[z.cohort.eq('open_source'),'excess'].dropna().to_numpy()
    cc=z.loc[z.cohort.eq('closed'),'excess'].dropna().to_numpy()
    boot=np.median(rng.choice(aa,(args.bootstrap,len(aa))),axis=1)-np.median(rng.choice(cc,(args.bootstrap,len(cc))),axis=1)
    low,high=np.quantile(boot,[.025,.975])
    med=z.groupby('cohort')[['multiple','pme','excess']].median()
    zz=z.assign(oss=z.cohort.eq('open_source').astype(int))
    fit=smf.ols('log_pme~oss+C(year)',zz).fit(cov_type='HC3',use_t=True)
    flo,fhi=fit.conf_int().loc['oss']
    rows.append({'scenario':name,'n_open':len(aa),'n_closed':len(cc),
    'open_value_1':med.loc['open_source','multiple'],'closed_value_1':med.loc['closed','multiple'],
    'open_pme':med.loc['open_source','pme'],'closed_pme':med.loc['closed','pme'],
    'open_excess_pp':100*med.loc['open_source','excess'],'closed_excess_pp':100*med.loc['closed','excess'],
    'difference_pp':100*(np.median(aa)-np.median(cc)),
    'bootstrap_95_low_pp':100*low,'bootstrap_95_high_pp':100*high,
    'year_controlled_pme_ratio':np.exp(fit.params['oss']),
    'year_controlled_95_low':np.exp(flo),'year_controlled_95_high':np.exp(fhi),
    'year_controlled_p':fit.pvalues['oss']})
summary=pd.DataFrame(rows)
summary.to_csv(DEST/'h1_sensitivity_results.csv',index=False)
rep.to_csv(DEST/'h1_replication_company.csv',index=False)
econ.to_csv(DEST/'h1_independent_company.csv',index=False)
pd.concat([z.assign(scenario=k) for k,z in sc.items()],ignore_index=True).to_csv(DEST/'h1_all_scenarios_company.csv',index=False)
# Verify against published values while allowing numerical floating-point noise.
published=pd.read_csv(ROOT/'h1_sensitivity_results.csv')
if args.bootstrap==50000:
    assert published.scenario.tolist()==summary.scenario.tolist()
    assert np.allclose(summary.select_dtypes('number'),published.select_dtypes('number'),rtol=1e-9,atol=1e-10)
    print('PASS: all 16 specifications and bootstrap intervals reproduce published values.')
print(summary.to_string(index=False))

# Raw-table-only validation at independently retrieved timestamped Nov24 quotes.
# This does not reuse any computed return/benchmark column from h1_returns.csv.
quotes=pd.read_csv(ROOT/'timestamped_quotes.csv').set_index('ticker').regular_market_price
qind=r.copy()
economic_dates={'Talend':'2021-07-30','SUSE':'2023-10-06','MariaDB':'2024-07-25'}
for i,row in qind.iterrows():
    exited=pd.notna(row.exit_price_per_share)
    end=economic_dates.get(row.company,row.exit_close_date) if exited else '2026-11-24'
    qind.loc[i,'end_date']=end
    tick='HUCK' if row.company=='Domo' else row.ticker
    qind.loc[i,'end_value_per_share']=row.exit_price_per_share if exited else quotes[tick]
    if pd.isna(row.first_day_close) and not exited:
        qind.loc[i,'first_day_close']=market[tick].loc[row.listing_date,'close']
    for bench,col in [('QQQ','qqq_multiple'),('IGV','igv_multiple')]:
        end_bench=price(market[bench].adjclose,end) if exited else quotes[bench]
        qind.loc[i,col]=end_bench/price(market[bench].adjclose,row.listing_date)
qind.loc[qind.company.eq('SolarWinds'),'end_value_per_share']=16.75
qind.loc[qind.company.eq('MuleSoft'),'end_value_per_share']=36+.0711*market['CRM'].loc['2018-05-02','close']
su=qind[qind.company.eq('SUSE')].iloc[0]
qind.loc[qind.company.eq('SUSE'),'end_value_per_share']=16*price(market['EURUSD=X'].close,su.end_date)/price(market['EURUSD=X'].close,su.listing_date)
qind=metrics(qind)
qind.to_csv(DEST/'h1_independent_timestamped_company.csv',index=False)
qcase=qind[qind.company.isin(base_names)].assign(oss=lambda z:z.cohort.eq('open_source').astype(int))
qfit=smf.ols('log_pme~oss+C(year)',qcase).fit(cov_type='HC3',use_t=True)
qlo,qhi=qfit.conf_int().loc['oss']
qmed=qcase.groupby('cohort')[['multiple','pme','excess']].median()
print('Independent raw-only timestamped quote results:\n',qmed)
print('Adjusted wealth ratio/95% CI:',np.exp(qfit.params['oss']),np.exp(qlo),np.exp(qhi))
