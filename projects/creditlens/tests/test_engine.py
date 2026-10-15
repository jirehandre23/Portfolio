import unittest
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import annual_debt_service,analyze,portfolio
LOANS=json.loads((Path(__file__).resolve().parents[1]/'data/borrowers.json').read_text())
class FinanceTests(unittest.TestCase):
    def test_zero_rate(self):self.assertAlmostEqual(annual_debt_service(120000,0,10),12000)
    def test_published_example(self):
        # OTS 2009 worked example: 6.3m, 7.5%, 30y; published annual payment rounded.
        self.assertAlmostEqual(annual_debt_service(6300000,.075,30),528606,delta=2)
    def test_fixed_rate_unchanged(self):
        self.assertEqual(analyze(LOANS[0])['debt_service'],analyze(LOANS[0],rate_shock=.03)['debt_service'])
    def test_floating_rate_increases(self):
        self.assertGreater(analyze(LOANS[1],rate_shock=.03)['debt_service'],analyze(LOANS[1])['debt_service'])
    def test_revenue_loss_reduces_dscr(self):self.assertLess(analyze(LOANS[0],-.1)['dscr'],analyze(LOANS[0])['dscr'])
    def test_headroom_identity(self):
        row=analyze(LOANS[0]);at_boundary=analyze(LOANS[0],-row['revenue_headroom'])
        self.assertAlmostEqual(at_boundary['dscr'],LOANS[0]['covenant'])
    def test_aggregate_is_ratio_of_sums(self):
        rows=[analyze(x) for x in LOANS];s=portfolio(rows)
        self.assertAlmostEqual(s['dscr'],sum(x['cfads'] for x in rows)/sum(x['debt_service'] for x in rows))
    def test_invalid_inputs(self):
        for field,value in [('principal',-1),('annual_rate',float('nan')),('remaining_years',0)]:
            with self.assertRaises(ValueError):analyze(LOANS[0]|{field:value})
    def test_negative_cash_is_visible(self):
        self.assertLess(analyze(LOANS[0],-.5)['cash_after_year'],0)
if __name__=='__main__':unittest.main()
