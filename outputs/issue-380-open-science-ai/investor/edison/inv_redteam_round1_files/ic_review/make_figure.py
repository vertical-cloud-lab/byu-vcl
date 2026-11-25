from pathlib import Path
import numpy as np
import pandas as pd
out=Path(__file__).resolve().parent
c=pd.read_csv(out/'companies_analysis.csv')
contr=pd.read_csv(out/'contrasts_sensitivity.csv')
valid_types=['market_cap','private_valuation','acquisition_price']
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
trace_id='95ddb5a0-c3c5-438f-8083-cacf439a71f0';print('Original execution ID',trace_id)
figdir=out/'figures';figdir.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':0.7,'xtick.major.width':0.7,'ytick.major.width':0.7,'savefig.dpi':350})
fig,axs=plt.subplots(2,2,figsize=(10,8.5),layout='constrained',gridspec_kw={'height_ratios':[1,1]})
colors={'private_valuation':'#4878A8','market_cap':'#666666','acquisition_price':'#C07848'}
marks={'private_valuation':'o','market_cap':'s','acquisition_price':'^'}
plotrng=np.random.default_rng(380)
d=c[c.eligible_commercial]
for ax,ycol,scale,label in [(axs[0,0],'value_usd',1e9,'Reported company value (USD billion)'),(axs[0,1],'multiple',1,'Reported value / cumulative funding (×)')]:
 for vt in valid_types:
  z=d[d.latest_value_type.eq(vt)&d[ycol].notna()]
  ax.scatter(z.openness_current+plotrng.uniform(-.13,.13,len(z)),z[ycol]/scale,s=24,color=colors[vt],marker=marks[vt],alpha=.8,edgecolors='white',linewidths=.35,label=vt.replace('_',' ').capitalize())
 for k,g in d.groupby('openness_current'):
  x=g[ycol].dropna()/scale
  if len(x):
   ax.plot([k-.24,k+.24],[x.median()]*2,color='black',lw=1.8)
   ax.text(k,1.02,f'n={len(x)}',transform=ax.get_xaxis_transform(),ha='center',fontsize=8)
 ax.set_yscale('log');ax.set_xticks([0,1,2,3,4]);ax.set_xlim(-.5,4.5);ax.set_xlabel('Current openness score');ax.set_ylabel(label);ax.grid(axis='y',color='#e4e4e4',lw=.5)
 ax.text(4,.5,'No eligible\nlevel-4 cases',transform=ax.get_xaxis_transform(),ha='center',va='center',fontsize=8,color='#666666')
axs[0,0].legend(fontsize=7,loc='upper left',frameon=False)
ax=axs[1,0]
for j,ev in enumerate(['acquisition','take_private','failure']):
 for score,offset,color,label in [('openness_current',-.12,'#4878A8','Current score'),('openness_initial',.12,'#C07848','Founding score')]:
  r=contr.query("sample=='commercial' & open_threshold==2 & outcome==@ev & score_basis==@score").iloc[0]
  ax.errorbar(r.risk_difference*100,j+offset,xerr=[[100*(r.risk_difference-r.rd_lo)],[100*(r.rd_hi-r.risk_difference)]],fmt='o',color=color,capsize=3,label=label if j==0 else None,ms=4)
ax.axvline(0,color='#999999',lw=.8,ls='--');ax.set_yticks(range(3),['Acquired (ever)','Taken private (ever)','Shutdown / bankruptcy']);ax.invert_yaxis();ax.set_xlabel('Rate difference: scores 2–4 minus 0–1 (percentage points)');ax.legend(frameon=False,fontsize=8,loc='lower right');ax.grid(axis='x',color='#e4e4e4',lw=.5)
ax=axs[1,1]
for i,k in enumerate([0,1,2,3]):
 g=d[d.openness_current.eq(k)];nv=g.value_usd.notna().sum();nm=g.multiple.notna().sum()
 ax.bar(i-.18,nv/len(g)*100,width=.34,color='#4878A8',label='Value observed' if i==0 else None)
 ax.bar(i+.18,nm/len(g)*100,width=.34,color='#A7B9C6',label='Value and funding observed' if i==0 else None)
 ax.text(i-.18,nv/len(g)*100+2,f'{nv}/{len(g)}',ha='center',fontsize=8)
 ax.text(i+.18,nm/len(g)*100+2,f'{nm}/{len(g)}',ha='center',fontsize=8)
ax.set_xticks([0,1,2,3]);ax.set_ylim(0,100);ax.set_xlabel('Current openness score');ax.set_ylabel('Commercial cases with observed data (%)');ax.legend(frameon=False,fontsize=8,loc='upper right');ax.grid(axis='y',color='#e4e4e4',lw=.5);ax.set_axisbelow(True)
for ax,letter,title in zip(axs.flat,'abcd',['Value distributions','Capital-efficiency proxy','Historical event contrasts (95% CI)','Missingness is substantial']):
 ax.set_title(title,loc='left',pad=20,fontsize=10,fontweight='bold');ax.text(-.16,1.10,letter,transform=ax.transAxes,fontweight='bold',fontsize=13)
fig.savefig(figdir/'investment_evidence.png',bbox_inches='tight');fig.savefig(figdir/'investment_evidence.pdf',bbox_inches='tight');plt.show()
