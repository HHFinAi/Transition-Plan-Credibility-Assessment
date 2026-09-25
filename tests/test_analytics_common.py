import unittest
from sf_agent.maths import npv,dscr,holding_period_return,scale
from sf_agent.validation import DataError

class CommonArithmetic(unittest.TestCase):
    def test_npv_timing(self): self.assertAlmostEqual(npv([-100,110],.1),0)
    def test_npv_negative_discount(self): self.assertAlmostEqual(npv([0,90],-.1),100)
    def test_npv_reject_minus_one(self):
        with self.assertRaises(DataError): npv([1,2],-1)
    def test_npv_empty(self):
        with self.assertRaises(DataError): npv([],.05)
    def test_dscr(self): self.assertEqual(dscr(100,50),2)
    def test_dscr_zero_denominator(self):
        with self.assertRaises(DataError): dscr(100,0)
    def test_holding_period_return(self): self.assertAlmostEqual(holding_period_return(100,102,5,1,.5),.055)
    def test_holding_period_return_zero_price(self):
        with self.assertRaises(DataError): holding_period_return(0,100,0,0,0)
    def test_conversion(self): self.assertEqual(scale(25,.0001),.0025)
    def test_boolean_rejected(self):
        with self.assertRaises(DataError): dscr(True,1)
    def test_nonfinite_rejected(self):
        with self.assertRaises(DataError): dscr(float('nan'),1)
if __name__=='__main__': unittest.main()
