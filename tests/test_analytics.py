"""Original HHFinAi domain arithmetic tests; all numbers are synthetic."""
import copy, math, random, unittest
from sf_agent.analytics import *
from sf_agent.validation import DataError

class Transition(unittest.TestCase):
    def test_half_target_path(self):
        r=target_path(100,50,2020,2030,2025,80);self.assertAlmostEqual(r['required_compound_annual_reduction'],1-.5**.1)
    def test_midpoint_trajectory(self):self.assertAlmostEqual(target_path(100,50,2020,2030,2025,80)['illustrative_path_emissions'],math.sqrt(5000))
    def test_zero_endpoint_rejected(self):
        with self.assertRaises(DataError):target_path(100,0,2020,2030,2025,80)
    def test_years_order(self):
        with self.assertRaises(DataError):target_path(100,50,2030,2020,2025,80)
    def test_future_observation(self):
        with self.assertRaises(DataError):target_path(100,50,2020,2030,2031,80)
    def test_activity_bridge_reconciles(self):
        r=activity_intensity_bridge(100,2,110,1.5);self.assertAlmostEqual(r['activity_effect']+r['intensity_effect'],r['delta'])
    def test_intensity_improvement_can_raise_emissions(self):self.assertGreater(activity_intensity_bridge(100,2,200,1.5)['delta'],0)
    def test_alignment_bounds(self):
        r=capex_alignment_bounds(20,30,100);self.assertEqual(r['confirmed_aligned_fraction'],.2);self.assertEqual(r['maximum_if_unknown_aligns'],.5)
    def test_alignment_overallocation(self):
        with self.assertRaises(DataError):capex_alignment_bounds(80,30,100)
    def test_funding_gap(self):self.assertEqual(funding_gap(100,60),40)
    def test_funding_surplus_zero(self):self.assertEqual(funding_gap(100,120),0)
    def test_random_bridge_reconciliation(self):
        g=random.Random(19)
        for i in range(100):
            r=activity_intensity_bridge(g.uniform(1,1000),g.uniform(.1,10),g.uniform(1,1000),g.uniform(.1,10))
            self.assertAlmostEqual(r['activity_effect']+r['intensity_effect'],r['end_emissions']-r['start_emissions'],places=8)

if __name__=='__main__':unittest.main()
