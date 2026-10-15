export function validate(loan) {
  for(const k of ['principal','annual_rate','remaining_years','revenue','expenses','cash','covenant'])
    if(typeof loan[k] !== 'number' || !Number.isFinite(loan[k])) throw new Error(`${k} must be finite`);
  if(loan.principal<=0||loan.revenue<=0||loan.expenses<=0||loan.cash<0) throw new Error('Invalid financial inputs');
  if(loan.annual_rate<0||loan.annual_rate>1||loan.remaining_years<1||loan.remaining_years>50||loan.covenant<=0) throw new Error('Invalid rate, term or covenant');
  if(loan.remaining_years*12!==Math.round(loan.remaining_years*12)) throw new Error('Term must be whole months');
  if(!['fixed','floating'].includes(loan.rate_type)) throw new Error('Unknown rate type');
}
export function annualDebtService(principal,rate,years) {
  if(![principal,rate,years].every(Number.isFinite)||principal<=0||rate<0||years<1) throw new Error('Invalid amortization inputs');
  const r=rate/12,n=Math.round(years*12);
  return 12*(r===0?principal/n:principal*r/(-Math.expm1(-n*Math.log1p(r))));
}
export function analyze(loan,revenueChange=0,expenseChange=0,rateShock=0) {
  validate(loan);
  if(![revenueChange,expenseChange,rateShock].every(Number.isFinite)||revenueChange<-.9||revenueChange>1||expenseChange<-.9||expenseChange>1||rateShock<-.5||rateShock>.5) throw new Error('Invalid scenario');
  const rate=loan.annual_rate+(loan.rate_type==='floating'?rateShock:0);
  if(rate<0) throw new Error('Negative interest rate');
  const revenue=loan.revenue*(1+revenueChange),expenses=loan.expenses*(1+expenseChange),cfads=revenue-expenses;
  const debt=annualDebtService(loan.principal,rate,loan.remaining_years),dscr=cfads/debt;
  return {id:loan.id,name:loan.name,sector:loan.sector,principal:loan.principal,effective_rate:rate,revenue,expenses,cfads,debt_service:debt,dscr,covenant:loan.covenant,breach:dscr<loan.covenant,cash_days:loan.cash/(expenses/365),cash_after_year:loan.cash+cfads-debt,covenant_cash_gap:cfads-loan.covenant*debt,revenue_headroom:1-(expenses+loan.covenant*debt)/revenue};
}
export function portfolio(rows) {
  if(!rows.length) throw new Error('Empty portfolio');
  const sum=k=>rows.reduce((s,x)=>s+x[k],0),exposure=sum('principal');
  const breached=rows.filter(x=>x.breach).reduce((s,x)=>s+x.principal,0);
  return {exposure,dscr:sum('cfads')/sum('debt_service'),breaches:rows.filter(x=>x.breach).length,breached_exposure:breached,breach_share:breached/exposure};
}
