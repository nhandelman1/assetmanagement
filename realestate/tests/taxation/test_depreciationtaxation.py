from decimal import Decimal
import datetime

from ...taxation.depreciationtaxation import DepreciationTaxation
from ..models.test_depreciationbilldata import DepreciationBillDataTests
from ..models.test_realpropertyvalue import RealPropertyValueTests
from ..testcasebase import TestCaseBase


class DepreciationTaxationTests(TestCaseBase):

    def equal(self, obj1: object, obj2: object):
        self.simple_equal(obj1, obj2, DepreciationTaxation)

    def test_calculate_accumulated_depreciation(self):
        dep_tax = DepreciationTaxation()
        rpv = RealPropertyValueTests.real_property_value_house_apt()
        DepreciationBillDataTests.depreciation_bill_data_1()
        DepreciationBillDataTests.depreciation_bill_data_2()

        with self.assertRaises(ValueError):
            dep_tax.calculate_accumulated_depreciation(rpv, datetime.date.today().year)

        # TODO change tax year from 2022 to 2023 and use Decimal("4480.00") so calculate_accumulated_depreciation() has
        # TODO more than one bill to use. do this in 2024
        self.assertEqual(dep_tax.calculate_accumulated_depreciation(rpv, 2022), Decimal("1408.00"))

    def test_calculate_depreciation_for_year(self):
        dep_tax = DepreciationTaxation()
        rpv = RealPropertyValueTests.real_property_value_house_apt()
        DepreciationBillDataTests.depreciation_bill_data_1()
        DepreciationBillDataTests.depreciation_bill_data_2()

        with self.assertRaises(ValueError):
            dep_tax.calculate_depreciation_for_year(rpv, datetime.date.today().year)

        # TODO change tax year from 2022 to 2023 and use Decimal("4480.00") so calculate_accumulated_depreciation() has
        # TODO more than one bill to use. do this in 2024
        year_dep, remain_dep, max_year_dep = dep_tax.calculate_depreciation_for_year(rpv, 2022)
        self.assertEqual(year_dep, Decimal("3072.00"))
        self.assertEqual(remain_dep, Decimal("83085.00"))
        self.assertEqual(max_year_dep, Decimal("3072.00"))
