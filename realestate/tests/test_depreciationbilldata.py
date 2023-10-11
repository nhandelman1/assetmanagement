from decimal import Decimal
import datetime

from django.core.exceptions import ValidationError

from ..models import DepreciationBillData
from .djangomodeltestcasebase import DjangoModelTestCaseBase
from .test_realestate import RealEstateTests
from .test_serviceprovider import ServiceProviderTests
from .test_realpropertyvalue import RealPropertyValueTests


class DepreciationBillDataTests(DjangoModelTestCaseBase):

    def equal(self, model1: DepreciationBillData, model2: DepreciationBillData):
        RealEstateTests().equal(model1.real_estate, model2.real_estate)
        ServiceProviderTests().equal(model1.service_provider, model2.service_provider)
        RealPropertyValueTests().equal(model1.real_property_value, model2.real_property_value)
        self.simple_equal(model1, model2, DepreciationBillData,
                          rem_attr_list=["real_estate", "service_provider", "real_property_value"])

    def test_end_date(self):
        dbd = DepreciationBillDataTests.depreciation_bill_data_1()
        with self.assertRaises(ValidationError):
            dbd.end_date = datetime.date(1900, 7, 29)
            dbd.clean_fields()

    def test_modify(self):
        # modify but with no changes except to notes
        dbd = DepreciationBillDataTests.depreciation_bill_data_1()
        dbd_copy = dbd.modify()
        dbd.notes += " This bill is a modification of the original bill."
        self.equal(dbd, dbd_copy)

        # modify but with cost_ratio applied to total_cost and real_estate and real_property_value changed
        dbd = DepreciationBillData.objects.get(pk=dbd.pk)
        dbd_copy = dbd.modify(cost_ratio=Decimal("0.5"), real_estate=RealEstateTests.real_estate_10wl(),
                              real_property_value=RealPropertyValueTests.real_property_value_car())
        dbd.total_cost = Decimal("704.00")
        dbd.real_estate = RealEstateTests.real_estate_10wl()
        dbd.real_property_value = RealPropertyValueTests.real_property_value_car()
        dbd.notes = "Max depreciation possible for full period: 1408. Partial year depreciation. Item purchased " \
                    "2021-07-14. Full period less than a year. This bill is a modification of the original bill. " \
                    "Ratio of 0.5 applied to total cost. Real estate changed from original. Real property values " \
                    "changed from original."
        self.equal(dbd, dbd_copy)

    def test_paid_date(self):
        dbd = DepreciationBillDataTests.depreciation_bill_data_1()
        with self.assertRaises(ValidationError):
            dbd.paid_date = datetime.date(1900, 3, 16)
            dbd.clean_fields()

    def test_period_usage_pct(self):
        with self.subTest():
            dbd = DepreciationBillDataTests.depreciation_bill_data_1()
            with self.assertRaises(ValidationError):
                dbd.period_usage_pct = Decimal("-0.01")
                dbd.clean_fields()

        with self.subTest():
            dbd = DepreciationBillDataTests.depreciation_bill_data_1()
            with self.assertRaises(ValidationError):
                dbd.period_usage_pct = Decimal("100.01")
                dbd.clean_fields()

    def test_process_service_bill(self):
        dbd_test = DepreciationBillDataTests.depreciation_bill_data_1()
        dbd = DepreciationBillData.process_service_bill("testdepreciationbill.csv")
        dbd_test.bill_file = dbd.bill_file
        self.equal(dbd, dbd_test)

    def test_start_date(self):
        dbd = DepreciationBillDataTests.depreciation_bill_data_1()
        with self.assertRaises(ValidationError):
            dbd.start_date = datetime.date(1900, 2, 5)
            dbd.clean_fields()

    @staticmethod
    def depreciation_bill_data_1():
        return DepreciationBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wlapt1(),
            service_provider=ServiceProviderTests.service_provider_dep(),
            real_property_value=RealPropertyValueTests.real_property_value_house(),
            start_date=datetime.date(2021, 1, 1), end_date=datetime.date(2021, 12, 31), period_usage_pct=Decimal(100),
            total_cost=Decimal("1408.00"), tax_rel_cost=Decimal("1408.00"), paid_date=datetime.date(2021, 12, 31),
            notes="Max depreciation possible for full period: 1408. Partial year depreciation. "
                  "Item purchased 2021-07-14. Full period less than a year.")[0]

    @staticmethod
    def depreciation_bill_data_2():
        return DepreciationBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wlapt1(),
            service_provider=ServiceProviderTests.service_provider_dep(),
            real_property_value=RealPropertyValueTests.real_property_value_house(),
            start_date=datetime.date(2022, 1, 1), end_date=datetime.date(2022, 12, 31), period_usage_pct=Decimal(100),
            total_cost=Decimal("3072.00"), tax_rel_cost=Decimal("3072.00"), paid_date=datetime.date(2022, 12, 31),
            notes="Max depreciation possible for full period: 3072.")[0]
