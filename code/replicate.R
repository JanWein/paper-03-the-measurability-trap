# Base-R replication of R1 scalar allocation and exact crossing.
# Not executed in the authoring environment. Run from extracted package root:
# Rscript code/replicate.R
alpha <- c(.25,.75); w <- c(.5,.5); pi <- .5; R <- .5; eta <- 1
nu <- eta+1; beta <- 1/alpha; good <- 10; loss <- 1
D <- function(x) sum(w*(pi*x+(1-pi)*x^beta))
xof <- function(rho) pmin(1,(rho*pi/((1-pi)*beta))^(1/(beta-1)))
ecross <- log(alpha[2]/alpha[1])/(nu*(alpha[2]-alpha[1]))
kcross <- D(exp(-nu*alpha*ecross))
rows <- list();j <- 1
for(k in c(.05,kcross,.6)) {
 rho <- uniroot(function(r) D(xof(r))-k,c(0,max(beta)*(1-pi)/pi),tol=1e-12)$root
 x <- xof(rho);eopt <- -log(x)/(nu*alpha)
 ec <- uniroot(function(e) D(exp(-nu*alpha*e))-k,c(0,100),tol=1e-12)$root
 xc <- exp(-nu*alpha*ec)
 for(rule in c('common','type_specific')) {
  z <- if(rule=='common') xc else x
  ev <- if(rule=='common') rep(ec,2) else eopt
  K <- R^eta*k;G <- sum(w*pi*z)
  value <- R^eta*((good+loss)*G-loss*k)-eta/nu*R*K
  rows[[j]] <- data.frame(k=k,policy=rule,e1=ev[1],e2=ev[2],value=value);j <- j+1
 }
}
result <- do.call(rbind,rows)
stopifnot(abs(ecross-log(3))<1e-12,abs(kcross-.24800564528543081)<1e-12)
print(result,row.names=FALSE)
dir.create('results',showWarnings=FALSE)
write.csv(result,'results/R_replication.csv',row.names=FALSE)
