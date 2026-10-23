"""Five-year K12 readiness tests; outputs are not official ROI."""
import unittest
from tools.arge_block01_k12_tco_v1 import five_year_cost, compare_five_year_tco, REQUIRED
def fixture(n):
    return {"years":[{name:{"value":str(n),"unit":"TRY_2026_CONSTANT","source_ref":"TEST_ONLY"} for name in REQUIRED} for _ in range(5)]}
class K12Tests(unittest.TestCase):
    def test_missing_input_holds(self):
        self.assertEqual(five_year_cost({})["state"],"HOLD_INPUT_SCOPE")
    def test_unverified_field_holds(self):
        x=fixture(10);x["years"][0]["license"]["source_ref"]=""
        self.assertEqual(five_year_cost(x)["state"],"HOLD_SOURCE_OR_UNIT")
    def test_mixed_units_hold(self):
        x=fixture(10);x["years"][0]["license"]["unit"]="USD"
        self.assertEqual(five_year_cost(x)["state"],"HOLD_UNIT_COMPARABILITY")
    def test_negative_cost_hold(self):
        x=fixture(10);x["years"][1]["risk"]["value"]=-1
        self.assertEqual(five_year_cost(x)["state"],"HOLD_COST_VALUE")
    def test_malformed_year_holds(self):
        x=fixture(10);x["years"][1]=None
        self.assertEqual(five_year_cost(x)["state"],"HOLD_COST_FIELDS")
    def test_malformed_cost_item_holds(self):
        x=fixture(10);x["years"][1]["license"]="bad"
        self.assertEqual(five_year_cost(x)["state"],"HOLD_SOURCE_OR_UNIT")
    def test_comparison_mismatched_currency_holds(self):
        a=fixture(10);b=fixture(9)
        for x in (a,b):x.update(workload_ref="w1",measurement_period="2026",price_basis="fixed")
        for year in b["years"]:
            for item in year.values():item["unit"]="USD"
        self.assertEqual(compare_five_year_tco(a,b)["state"],"HOLD_CURRENCY_MISMATCH")
    def test_comparison_workload_mismatch_holds(self):
        a=fixture(10);b=fixture(9)
        for x in (a,b):x.update(workload_ref="w1",measurement_period="2026",price_basis="fixed")
        b["workload_ref"]="w2"
        self.assertEqual(compare_five_year_tco(a,b)["state"],"HOLD_COMPARABILITY_WORKLOAD_REF")
    def test_comparison_valid_cost_delta(self):
        a=fixture(10);b=fixture(9)
        for x in (a,b):x.update(workload_ref="w1",measurement_period="2026",price_basis="fixed")
        z=compare_five_year_tco(a,b)
        self.assertEqual(z["state"],"CALCULATION_ONLY_NEEDS_INDEPENDENT_REVIEW")
        self.assertEqual(z["absolute_five_year_saving"],"30")
    def test_sensitivity_calculation_only(self):
        y=five_year_cost(fixture(10))
        self.assertEqual(y["state"],"CALCULATION_ONLY_NEEDS_INDEPENDENT_REVIEW")
        self.assertEqual(y["total"],"300")
        self.assertEqual(y["sensitivity_minus_20pct"],"240.0")
        self.assertEqual(y["sensitivity_plus_20pct"],"360.0")
if __name__=="__main__":unittest.main()
