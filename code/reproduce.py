"""Reproduce R1 analytical tables, theorem checks, independent optimizers and figures.
Run from any directory: python code/reproduce.py. No empirical observations used.
"""
from pathlib import Path
import csv,json,platform,hashlib
import numpy as np
from scipy.optimize import minimize_scalar,brentq,differential_evolution
from scipy.integrate import quad
import scipy,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import Economy
OUT=Path(__file__).resolve().parents[1]/'results';OUT.mkdir(exist_ok=True)
def save(name,rows):
 with (OUT/name).open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
def row(econ,K,policy,r):
 return dict(K=K,k=K/econ.R**econ.eta,policy=policy,e1=r['e'][0],e2=r['e'][1],ration=r['ration'],funded=r['funded'],good1=r['funded_good'][0],good2=r['funded_good'][1],bad1=r['funded_bad'][0],bad2=r['funded_bad'][1],applications_good=float(r['applications_good'].sum()),applications_bad=float(r['applications_bad'].sum()),application_cost=r['application_cost'],value=r['value'])
econ=Economy();econ.check();cross=econ.crossing();rows=[]
for k in [.05,cross['k_star'],.6]:
 K=econ.R**econ.eta*k
 for label,r in [('no_gate',econ.equilibrium([0,0],K)),('common',econ.common(K)),('type_specific',econ.optimal(K))]:rows.append(row(econ,K,label,r))
save('main_table.csv',rows)
# Independent constrained one-dimensional allocation: optimize x1 on the D=k curve.
checks=[];rng=np.random.default_rng(20261017)
for j in range(30):
 alpha=tuple(sorted(rng.uniform(.18,.85,2)));eta=float(rng.uniform(.4,2.5));weights=(float(rng.uniform(.2,.8)),0);weights=(weights[0],1-weights[0])
 E=Economy(alpha=alpha,eta=eta,weights=weights,good=50.);E.check();k=float(rng.uniform(.025,.95));K=E.R**eta*k
 r=E.optimal(K);w=np.array(weights);beta=1/np.array(alpha);pi=E.pi
 def d1(x):return w[0]*(pi*x+(1-pi)*x**beta[0])
 def d2(x):return w[1]*(pi*x+(1-pi)*x**beta[1])
 lo=0 if k<=d2(1) else brentq(lambda x:d1(x)+d2(1)-k,0,1)
 hi=1 if k>=d1(1) else brentq(lambda x:d1(x)-k,0,1)
 def x2(x1):
  rem=np.clip(k-d1(x1),0,d2(1));return brentq(lambda x:d2(x)-rem,0,1,xtol=1e-14)
 def objective(x1):return -(w[0]*pi*x1+w[1]*pi*x2(x1))
 opt=minimize_scalar(objective,bounds=(lo,hi),method='bounded',options={'xatol':1e-13})
 candidates=[lo,hi,opt.x];xx=max(candidates,key=lambda x:-objective(x))
 G=-objective(xx);Ga=float(np.sum(r['funded_good']))/E.R**eta
 err=abs(G-Ga);assert err<2e-8
 assert abs(r['funded']-K)<1e-10 and abs(r['application_cost']-E.kappa*K)<1e-10
 c=E.crossing();rc=E.common(E.R**eta*c['k_star']);ro=E.optimal(E.R**eta*c['k_star'])
 assert np.max(np.abs(rc['e']-ro['e']))<1e-7
 ec=E.common(K);sgn=np.sign(k-c['k_star'])
 assert sgn*(r['e'][0]-ec['e'][0])>=-1e-7 and sgn*(r['e'][1]-ec['e'][1])<=1e-7
 checks.append(dict(case=j,allocation_error=err,budget_error=abs(r['funded']-K),eta=eta,k=k,alpha1=alpha[0],alpha2=alpha[1]))
save('independent_allocation_checks.csv',checks)
# A second independent optimizer solves original thresholds with equilibrium rationing/underfill.
original=[]
for k in [.05,.2,.6]:
 K=econ.R*k;r=econ.optimal(K)
 result=differential_evolution(lambda e:-econ.equilibrium(e,K)['value'],[(0,25),(0,25)],seed=20261017,tol=1e-10,popsize=20,maxiter=800,polish=True)
 err=abs(-result.fun-r['value']);assert err<3e-7
 original.append(dict(k=k,analytic_value=r['value'],direct_value=-result.fun,error=err,e1_direct=result.x[0],e2_direct=result.x[1]))
save('original_policy_optimization.csv',original)
# Independent integration of entry probabilities and actual resource costs.
integ=[]
K=econ.R*.2;r=econ.equilibrium([.5,.7],K)
for t in range(2):
 for quality in ['good','bad']:
  p=r['p'][t] if quality=='good' else r['q'][t];cut=econ.R*r['ration']*p
  prob=quad(lambda c:econ.eta*c**(econ.eta-1),0,cut)[0]
  cost=quad(lambda c:c*econ.eta*c**(econ.eta-1),0,cut)[0]
  assert abs(prob-cut**econ.eta)<1e-12
  integ.append(dict(type=t,quality=quality,cutoff=cut,entry=prob,cost=cost))
save('entry_integrals.csv',integ)
# Fixed-rule precision improvement: focal good entry rises, all other categories fall under rationing.
E0=Economy(alpha=(.4,.75));E1=Economy(alpha=(.3,.75));K=.02;e=[.5,.5]
r0=E0.equilibrium(e,K);r1=E1.equilibrium(e,K);assert r0['ration']<1 and r1['ration']<1
assert r1['applications_good'][0]>r0['applications_good'][0]
assert r1['funded_good'][0]>r0['funded_good'][0]
for arr in ['applications_good','applications_bad','funded_good','funded_bad']:assert r1[arr][1]<r0[arr][1]
save('precision_spillover.csv',[row(E0,K,'before',r0),row(E1,K,'after',r1)])
# Finite pilot/abandonment example including the reservation envelope.
c0=1.;J=1.;discount=.9;Rg=1+(10+1)/discount;Rb=0
assert discount*(Rg-J)>0 and discount*(Rb-J)<0
vg=-c0+discount*max(0,Rg-J);vb=-c0+discount*max(0,Rb-J)
assert abs(vg-econ.good)<1e-12 and abs(vb+econ.loss)<1e-12
# The finite pilot example is solved by backward induction, not simulated firm data.
curve=[]
for k in np.linspace(.05,.85,250):
 K=econ.R*k;c=econ.common(K);o=econ.optimal(K)
 curve.append(dict(k=k,e_common=c['e'][0],e1=o['e'][0],e2=o['e'][1],value_common=c['value'],value_optimal=o['value'],gap=o['value']-c['value']))
save('policy_curve.csv',curve)
fig,axes=plt.subplots(1,2,figsize=(8.5,3.5))
axes[0].plot([r['k'] for r in curve],[r['e1']-r['e_common'] for r in curve],label='More informative type (alpha=.25)')
axes[0].plot([r['k'] for r in curve],[r['e2']-r['e_common'] for r in curve],label='Less informative type (alpha=.75)')
axes[0].axhline(0,color='gray',lw=.7);axes[0].axvline(cross['k_star'],color='black',ls=':',lw=.8)
axes[0].set(xlabel='Normalized capacity k',ylabel='Optimal cutoff minus common cutoff',title='The direction of adjustment reverses')
axes[0].legend(frameon=False,fontsize=7)
axes[1].plot([r['k'] for r in curve],[r['gap'] for r in curve],color='#a64838');axes[1].axvline(cross['k_star'],color='black',ls=':',lw=.8)
axes[1].set(xlabel='Normalized capacity k',ylabel='Net portfolio value gain',title='Value gain at equal capacity')
fig.tight_layout();fig.savefig(OUT/'policy_reversal.png',dpi=200);plt.close(fig)
validation=dict(synthetic=True,seed=20261017,crossing=cross,independent_allocation_cases=len(checks),max_allocation_error=max(c['allocation_error'] for c in checks),direct_original_optimizations=original,entry_integrals=len(integ),pilot_values=dict(good=vg,bad=vb,cash_reservation_per_start=c0+J),python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__)
(OUT/'validation.json').write_text(json.dumps(validation,indent=2))
# Test the ROC lower bound for nonmonotone randomized score rules, independently of cutoff optimization.
roc_checks=[]
for j in range(200):
 alpha=float(rng.uniform(.15,.9));edges=np.r_[0,np.sort(rng.uniform(.01,12,14)),np.inf]
 delta=rng.uniform(0,1,len(edges)-1)
 zG=float(np.sum(delta*(np.exp(-alpha*edges[:-1])-np.exp(-alpha*edges[1:]))))
 zL=float(np.sum(delta*(np.exp(-edges[:-1])-np.exp(-edges[1:]))))
 slack=zL-zG**(1/alpha);assert slack>=-1e-12
 roc_checks.append(dict(case=j,alpha=alpha,good_probability=zG,bad_probability=zL,frontier_slack=slack))
save('nonmonotone_rule_checks.csv',roc_checks)
validation.update(nonmonotone_rule_checks=len(roc_checks),minimum_ROC_slack=min(r['frontier_slack'] for r in roc_checks))
# Normalized crossing is invariant to eta: only e_star and raw capacity rescale.
invariance=[]
for eta in [.5,1,2]:
 E=Economy(eta=eta);C=E.crossing();assert abs(C['k_star']-cross['k_star'])<1e-12
 invariance.append(dict(eta=eta,**C))
save('entry_elasticity_crossing.csv',invariance)
validation['elasticity_invariance_checks']=len(invariance)
(OUT/'validation.json').write_text(json.dumps(validation,indent=2))
# Proposition 4: independent finite differences of the fully reoptimized policy value.
rentchecks=[]
for K in [.0005,.005,.025,.1]:
 E=Economy();r=E.optimal(K);k=K/E.R**E.eta;G=r['funded_good'].sum()/E.R**E.eta;lam=1/(1+r['rho'])
 analytic=E.eta*E.R**(E.eta-1)*(E.good+E.loss)*(G-k*lam)-E.eta/E.nu*K
 eps=1e-5;lo=Economy(R=E.R-eps).optimal(K);hi=Economy(R=E.R+eps).optimal(K)
 numeric=(hi['value']-lo['value'])/(2*eps);err=abs(analytic-numeric);assert err<3e-8
 assert hi['funded_good'].sum()>lo['funded_good'].sum()
 rentchecks.append(dict(K=K,R=E.R,analytic_value_derivative=analytic,numerical_value_derivative=numeric,error=err,good_share=r['funded_good'].sum()/K))
assert rentchecks[0]['analytic_value_derivative']<0 and rentchecks[-1]['analytic_value_derivative']>0
save('funding_benefit_comparative_static.csv',rentchecks)
validation['rent_derivative_checks']=len(rentchecks);validation['max_rent_derivative_error']=max(r['error'] for r in rentchecks)
(OUT/'validation.json').write_text(json.dumps(validation,indent=2))

print(json.dumps(dict(crossing=cross,main_table=rows,validation=validation),indent=2))
