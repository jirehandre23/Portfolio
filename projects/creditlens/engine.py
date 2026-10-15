"""Deterministic educational credit scenarios; no default prediction or lending advice."""
import math


def validate(loan):
    for field in ('principal','annual_rate','remaining_years','revenue','expenses','cash','covenant'):
        value=loan[field]
        if isinstance(value, bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
            raise ValueError(f'{field} must be a finite number')
    if loan['principal']<=0 or loan['revenue']<=0 or loan['expenses']<=0 or loan['cash']<0:
        raise ValueError('Principal, revenue and expenses must be positive; cash cannot be negative')
    if not 0<=loan['annual_rate']<=1 or not 1<=loan['remaining_years']<=50 or loan['covenant']<=0:
        raise ValueError('Invalid rate, remaining term or covenant')
    if loan['remaining_years']*12 != round(loan['remaining_years']*12):
        raise ValueError('Term must be a whole number of months')
    if loan['rate_type'] not in ('fixed','floating'):
        raise ValueError('Unknown rate type')


def annual_debt_service(principal, annual_rate, years):
    if not all(math.isfinite(v) for v in (principal,annual_rate,years)) or principal<=0 or annual_rate<0 or years<1:
        raise ValueError('Invalid amortization inputs')
    monthly=annual_rate/12
    months=round(years*12)
    payment=principal/months if monthly==0 else principal*monthly/(-math.expm1(-months*math.log1p(monthly)))
    return 12*payment


def analyze(loan,revenue_change=0,expense_change=0,rate_shock=0):
    validate(loan)
    if not all(math.isfinite(v) for v in (revenue_change,expense_change,rate_shock)):
        raise ValueError('Scenario must be finite')
    if not -.9<=revenue_change<=1 or not -.9<=expense_change<=1 or not -.5<=rate_shock<=.5:
        raise ValueError('Scenario outside supported range')
    rate=loan['annual_rate']+(rate_shock if loan['rate_type']=='floating' else 0)
    if rate<0: raise ValueError('Scenario produces a negative interest rate')
    revenue=loan['revenue']*(1+revenue_change)
    expenses=loan['expenses']*(1+expense_change)
    cfads=revenue-expenses
    debt=annual_debt_service(loan['principal'],rate,loan['remaining_years'])
    ratio=cfads/debt
    return dict(id=loan['id'],name=loan['name'],sector=loan['sector'],principal=loan['principal'],
                effective_rate=rate,revenue=revenue,expenses=expenses,cfads=cfads,debt_service=debt,
                dscr=ratio,covenant=loan['covenant'],breach=ratio<loan['covenant'],
                cash_days=loan['cash']/(expenses/365),cash_after_year=loan['cash']+cfads-debt,
                covenant_cash_gap=cfads-loan['covenant']*debt,
                revenue_headroom=1-(expenses+loan['covenant']*debt)/revenue)


def portfolio(rows):
    if not rows: raise ValueError('Portfolio cannot be empty')
    total=sum(x['principal'] for x in rows)
    return dict(exposure=total,dscr=sum(x['cfads'] for x in rows)/sum(x['debt_service'] for x in rows),
                breaches=sum(x['breach'] for x in rows),
                breached_exposure=sum(x['principal'] for x in rows if x['breach']),
                breach_share=sum(x['principal'] for x in rows if x['breach'])/total)
