"""Closed-form entry equilibrium and optimal certificate standards. Synthetic primitives only."""
from dataclasses import dataclass
import numpy as np
from scipy.optimize import brentq

@dataclass(frozen=True)
class Economy:
    alpha: tuple=(.25,.75)
    weights: tuple=(.5,.5)
    pi: float=.5
    R: float=.5
    eta: float=1.
    good: float=10.
    loss: float=1.
    @property
    def nu(self):return self.eta+1
    @property
    def kappa(self):return self.eta/self.nu*self.R
    def check(self):
        assert 0<self.R<=1 and self.eta>0 and 0<self.pi<1
        assert np.all((np.array(self.alpha)>0)&(np.array(self.alpha)<1))
        assert abs(sum(self.weights)-1)<1e-10 and min(self.weights)>0
        assert (self.good-self.kappa)*self.pi > (self.loss+self.kappa)*(1-self.pi)/min(self.alpha)
    def D_x(self,x):
        x=np.asarray(x);b=1/np.array(self.alpha);w=np.array(self.weights)
        G=float(np.sum(w*self.pi*x));B=float(np.sum(w*(1-self.pi)*x**b))
        return G+B,G,B
    def equilibrium(self,e,K):
        e=np.asarray(e,float);a0=np.array(self.alpha);w=np.array(self.weights)
        p=np.exp(-a0*e);q=np.exp(-e)
        D=float(np.sum(w*(self.pi*p**self.nu+(1-self.pi)*q**self.nu)))
        r=min(1.,(K/(self.R**self.eta*D))**(1/self.nu)) if D else 1.
        appG=w*self.pi*(self.R*r*p)**self.eta
        appB=w*(1-self.pi)*(self.R*r*q)**self.eta
        fundedG=appG*r*p;fundedB=appB*r*q
        cost=self.eta/self.nu*self.R**self.nu*r**self.nu*D
        value=self.good*fundedG.sum()-self.loss*fundedB.sum()-cost
        return dict(e=e,p=p,q=q,D=D,ration=r,applications_good=appG,applications_bad=appB,
                    funded_good=fundedG,funded_bad=fundedB,application_cost=cost,
                    funded=float(fundedG.sum()+fundedB.sum()),value=float(value))
    def common(self,K):
        k=K/self.R**self.eta;assert 0<k<1
        def D(e):return self.D_x(np.exp(-self.nu*np.array(self.alpha)*e))[0]
        e=brentq(lambda e:D(e)-k,0, max(100.,-np.log(k)/(self.nu*min(self.alpha))*2),xtol=1e-13)
        return self.equilibrium(np.repeat(e,len(self.alpha)),K)
    def optimal(self,K):
        k=K/self.R**self.eta;beta=1/np.array(self.alpha)
        def xof(rho):return np.minimum(1.,(rho*self.pi/((1-self.pi)*beta))**(1/(beta-1)))
        rho=brentq(lambda z:self.D_x(xof(z))[0]-k,0,max(beta)*(1-self.pi)/self.pi,xtol=1e-13)
        x=xof(rho);e=-np.log(x)/(self.nu*np.array(self.alpha))
        r=self.equilibrium(e,K);r.update(rho=rho,x=x)
        return r
    def crossing(self):
        a,b=self.alpha;assert len(self.alpha)==2 and a<b
        e=np.log(b/a)/(self.nu*(b-a))
        k=self.D_x(np.exp(-self.nu*np.array(self.alpha)*e))[0]
        return dict(e_star=float(e),k_star=k,K_star=self.R**self.eta*k)
