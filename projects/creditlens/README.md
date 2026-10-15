# CreditLens — Loan Portfolio Stress Lab

[Open the interactive demo](https://jirehandre23.github.io/Portfolio/projects/creditlens/)

A financial-analytics portfolio project connecting borrower cash flow, amortizing
debt, interest-rate sensitivity and covenant monitoring. It pairs an interactive
browser interface with a reproducible Python engine and SQL analytics.

**All six borrowers and their financial records are fictional.** This project is
independent of Equitable Facilities Fund and contains no employer/client data.

## Business question

Which borrowers have the least room to absorb lower revenue, higher operating costs,
or repricing of floating-rate debt? The tool exposes its assumptions so a reviewer
can follow the calculations rather than accept an unexplained risk score.

## Try it

1. Open the demo and switch between Baseline, Moderate and Severe presets.
2. Adjust revenue, expenses and the floating-rate shock.
3. Select a borrower to inspect its calculation and sensitivity map.
4. Export the current scenario as JSON.

The interface runs entirely in the browser, with no sign-in or backend. A covenant
breach is a review flag, not a prediction of default or a lending recommendation.

## Reproduce the analysis

Python 3.10+ and Node.js 18+; no Python third-party packages required.

```bash
# Run from projects/creditlens:
python run.py
python -m unittest discover -s tests -v
node tests/parity.mjs
python -m http.server 8000
```

Open http://localhost:8000 to use the local interface. `run.py` regenerates the CSV,
JSON summary, cross-language fixtures and an ignored `creditlens.db` SQLite database.
`schema.sql` defines borrowers, scenarios, results and a `sector_risk` reporting view.

```sql
SELECT scenario, sector, exposure, breached_exposure, aggregate_dscr
FROM sector_risk ORDER BY scenario, sector;
```

## Financial definitions

For monthly interest rate `r`, principal `P`, and remaining payment count `n`:

- Monthly payment = `P × r / (1 − (1 + r)^(-n))`; at zero interest, `P / n`.
- Annual debt service = 12 monthly payments.
- Modeled cash available for debt service = stressed revenue − stressed operating expenses.
- DSCR = modeled cash available for debt service / annual debt service.
- Cash days = opening unrestricted cash / (stressed annual expenses / 365).
- Covenant cash headroom = modeled cash available − covenant × annual debt service.
- Revenue headroom = `1 − (expenses + covenant × annual debt service) / revenue`.
- Aggregate DSCR = total modeled cash available / total annual debt service, not a simple average.

Floating loans reprice immediately and are recast over the remaining amortization
term. Fixed loans do not change rate. A negative headroom value means the borrower
already falls below its covenant. Negative modeled cash is shown rather than hidden.

## Reproducible demonstration results

The fictional portfolio has $19.3 million in principal across six borrowers.

| Scenario | Revenue change | Expense change | Floating-rate shock | Aggregate DSCR | Covenant breaches |
|---|---:|---:|---:|---:|---:|
| Baseline | 0% | 0% | 0 bp | 1.599× | 0 / 6 |
| Moderate | −5% | +3% | +200 bp | 0.636× | 6 / 6 |
| Severe | −10% | +7% | +400 bp | −0.341× | 6 / 6 |

These are deterministic scenarios, not forecasts. Even a modest revenue decline can
sharply reduce the cash remaining after operating expenses when margins are thin.
Scenario labels are illustrative, not calibrated economic probabilities.

## Tests and implementation

- Nine Python tests cover zero-rate amortization, fixed/floating behavior, input
  validation, covenant-boundary algebra, negative cash and aggregate ratios.
- A published amortization example independently checks the formula.
- Eighteen borrower/scenario fixtures compare every Python output with JavaScript.
- The HTML interface uses the same financial definitions as the Python engine.
- Outputs: [summary](reports/summary.json), [detailed CSV](reports/scenario_results.csv),
  [parity fixtures](reports/parity_fixtures.json).

## Assumptions and scope

This is a one-year static model with at least one year remaining on every loan.
It omits taxes, capital expenditures, working-capital changes, fees, rate caps,
balloons, guarantees, collateral and borrower-specific covenant adjustments.
Opening cash is assumed unrestricted. Actual cash available for debt service must
be reconciled to the governing loan agreement and financial statements.

Borrowers are not cross-guarantors; aggregate coverage does not imply transfers of
cash between them. Breached exposure is not expected credit loss. There is no trained
ML model here: transparent scenario analysis is appropriate to this question and
complements the machine-learning work in FraudWatch.

## Sources and ownership

- [OTS financial analysis handbook (2009), hosted by OCC](https://www.occ.gov/static/ots/exam-handbook/ots-exam-handbook-210aa.pdf): historical DSCR and amortization examples; used for math, not current regulatory guidance.
- [J.P. Morgan DSCR explanation](https://www.jpmorgan.com/insights/real-estate/commercial-term-lending/what-is-debt-service-coverage-ratio-dscr-in-real-estate): lender perspective on operating income and debt service.

Built for Jireh Andre Bitangila's portfolio. To explain this in an
interview, trace one borrower's revenue to operating cash, debt payment, coverage and
covenant headroom; then explain the assumptions the model leaves out.
