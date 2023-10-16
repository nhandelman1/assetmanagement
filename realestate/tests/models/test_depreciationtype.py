import datetime
from decimal import Decimal

from ...models.realpropertyvalue import RealPropertyValue
from ...taxation.depreciationtaxation import DepreciationType
from ..testcasebase import TestCaseBase


class DepreciationTypeTests(TestCaseBase):

    def equal(self, obj1: object, obj2: object):
        self.simple_equal(obj1, obj2, DepreciationType)

    def test_recovery_period(self):
        DS = DepreciationType.DepreciationSystem
        PC = DepreciationType.PropertyClass

        self.assertEqual(PC.NONE.get_recovery_period(DS.NONE), Decimal("Infinity"))
        self.assertEqual(PC.NONE.get_recovery_period(DS.GDS), Decimal("Infinity"))
        self.assertEqual(PC.RRP.get_recovery_period(DS.GDS), Decimal("27.5"))
        self.assertEqual(PC.YEAR5.get_recovery_period(DS.GDS), Decimal(5))

    def test_from_dep_class(self):
        DT = DepreciationType

        dt = DT.from_dep_class(RealPropertyValue.DepClass.NONE)
        self.equal(dt, DT(DT.DS.NONE, DT.PC.NONE, DT.DM.NONE, DT.DC.NONE))

        dt = DT.from_dep_class(RealPropertyValue.DepClass.GDS_RRP_SL_MM)
        self.equal(dt, DT(DT.DS.GDS, DT.PC.RRP, DT.DM.SL, DT.DC.MM))

        dt = DT.from_dep_class(RealPropertyValue.DepClass.GDS_YEAR5_SL_MM)
        self.equal(dt, DT(DT.DS.GDS, DT.PC.YEAR5, DT.DM.SL, DT.DC.MM))

    def test_depreciation_ratio_for_tax_year(self):
        DT = DepreciationType

        # Case 1: check NONEs return Decimal(0)
        dt = DT(DT.DS.NONE, DT.PC.YEAR5, DT.DM.SL, DT.DC.MM)
        self.assertEqual(dt.depreciation_ratio_for_tax_year(datetime.date(1900, 1, 1), None, 1900), Decimal(0))
        dt = DT(DT.DS.GDS, DT.PC.NONE, DT.DM.SL, DT.DC.MM)
        self.assertEqual(dt.depreciation_ratio_for_tax_year(datetime.date(1900, 1, 1), None, 1900), Decimal(0))
        dt = DT(DT.DS.GDS, DT.PC.YEAR5, DT.DM.NONE, DT.DC.MM)
        self.assertEqual(dt.depreciation_ratio_for_tax_year(datetime.date(1900, 1, 1), None, 1900), Decimal(0))
        dt = DT(DT.DS.GDS, DT.PC.YEAR5, DT.DM.SL, DT.DC.NONE)
        self.assertEqual(dt.depreciation_ratio_for_tax_year(datetime.date(1900, 1, 1), None, 1900), Decimal(0))

        # Case 2: purchase and disposal in same year return Decimal(0)
        dt = DT(DT.DS.GDS, DT.PC.YEAR5, DT.DM.SL, DT.DC.MM)
        self.assertEqual(
            dt.depreciation_ratio_for_tax_year(datetime.date(1900, 1, 1), datetime.date(1900, 2, 1), 1900), Decimal(0))

        # Cases 3 and 4:
        def cases_3_4_test(dt1, pd, dd, ty, exp_res):
            self.assertEqual(
                dt1.depreciation_ratio_for_tax_year(pd, dd, ty), exp_res)

        dt = DT(DT.DS.GDS, DT.PC.RRP, DT.DM.SL, DT.DC.MM)
        cases_3_4_test(dt, datetime.date(1900, 1, 1), None, 1901, Decimal("0.036363636"))
        cases_3_4_test(dt, datetime.date(1900, 7, 15), None, 1900, Decimal("0.016666667"))
        cases_3_4_test(dt, datetime.date(1900, 7, 15), datetime.date(1903, 7, 15), 1903, Decimal("0.019696970"))

        dt = DT(DT.DS.GDS, DT.PC.RRP, DT.DM.SL, DT.DC.FM)
        cases_3_4_test(dt, datetime.date(1900, 1, 1), None, 1901, Decimal("0.036363636"))
        cases_3_4_test(dt, datetime.date(1900, 7, 15), None, 1900, Decimal("0.018181818"))
        cases_3_4_test(dt, datetime.date(1900, 7, 15), datetime.date(1903, 8, 20), 1903, Decimal("0.021212121"))

        dt = DT(DT.DS.GDS, DT.PC.YEAR5, DT.DM.SL, DT.DC.MM)
        cases_3_4_test(dt, datetime.date(1900, 1, 1), None, 1901, Decimal("0.200000000"))
        cases_3_4_test(dt, datetime.date(1900, 7, 15), None, 1900, Decimal("0.091666667"))
        cases_3_4_test(dt, datetime.date(1900, 7, 15), datetime.date(1903, 8, 20), 1903, Decimal("0.125000000"))

        dt = DT(DT.DS.GDS, DT.PC.YEAR5, DT.DM.SL, DT.DC.FM)
        cases_3_4_test(dt, datetime.date(1900, 1, 1), None, 1901, Decimal("0.200000000"))
        cases_3_4_test(dt, datetime.date(1900, 7, 15), None, 1900, Decimal("0.100000000"))
        val = dt.depreciation_ratio_for_tax_year(datetime.date(1900, 7, 15), datetime.date(1903, 8, 20), 1903)
        cases_3_4_test(dt, datetime.date(1900, 7, 15), datetime.date(1903, 8, 20), 1903, Decimal("0.116666667"))