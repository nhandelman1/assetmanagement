from decimal import Decimal
import datetime
import unittest.mock

from django.conf import settings
from django.core.files import File
from django.db.models import FileField

from realestate.models import MortgageBillData
from .djangomodeltestcasebase import DjangoModelTestCaseBase
from .test_realestate import RealEstateTests
from .test_serviceprovider import ServiceProviderTests


class MortgageBillDataTests(DjangoModelTestCaseBase):

    def equal(self, model1: MortgageBillData, model2: MortgageBillData):
        RealEstateTests().equal(model1.real_estate, model2.real_estate)
        ServiceProviderTests().equal(model1.service_provider, model2.service_provider)
        self.simple_equal(model1, model2, MortgageBillData, rem_attr_list=["real_estate", "service_provider"])

    def test_modify(self):
        # modify but with no changes except to notes
        mbd = MortgageBillDataTests.mortgage_bill_data_1()
        mbd_copy = mbd.modify()
        mbd.notes += " This bill is a modification of the original bill."
        mbd.clean_fields()
        self.equal(mbd, mbd_copy)

        # modify but with cost_ratio applied to attributes and real_estate changed
        mbd = MortgageBillData.objects.get(pk=mbd.pk)
        mbd_copy = mbd.modify(cost_ratio=Decimal("0.5"), real_estate=RealEstateTests.real_estate_10wlapt1())
        mbd.real_estate = RealEstateTests.real_estate_10wlapt1()
        mbd.total_cost = Decimal("688.06")
        mbd.outs_prin = Decimal("161792.685")
        mbd.esc_bal = Decimal(0)
        mbd.prin_pmt = Decimal("283.58")
        mbd.int_pmt = Decimal("404.48")
        mbd.esc_pmt = Decimal(0)
        mbd.other_pmt = Decimal(0)
        mbd.notes = ' statement date is 2022-05-02 This bill is a modification of the original bill. Ratio of 0.5 ' \
                    'applied to total cost. Real estate changed from original. Ratio of 0.5 applied to all attributes.'
        self.equal(mbd, mbd_copy)

    def test_process_service_bill(self):
        ebd_test = MortgageBillDataTests.mortgage_bill_data_1()
        ebd = MortgageBillData.process_service_bill("testmsbill1.pdf")
        ebd.tax_rel_cost = Decimal(0)
        ebd_test.bill_file = ebd.bill_file
        self.equal(ebd, ebd_test)

        ebd_test = MortgageBillDataTests.mortgage_bill_data_2()
        ebd = MortgageBillData.process_service_bill("testmsbill2.pdf")
        ebd.tax_rel_cost = Decimal(0)
        ebd_test.bill_file = ebd.bill_file
        self.equal(ebd, ebd_test)

        ebd_test = MortgageBillDataTests.mortgage_bill_data_3()
        ebd = MortgageBillData.process_service_bill("testmsbill3.pdf")
        ebd.tax_rel_cost = Decimal(0)
        ebd_test.bill_file = ebd.bill_file
        self.equal(ebd, ebd_test)

    @staticmethod
    def mortgage_bill_data_1():
        return MortgageBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ms(),
            start_date=datetime.date(2022, 5, 1), end_date=datetime.date(2022, 5, 31), total_cost=Decimal("1376.12"),
            tax_rel_cost=Decimal(0), outs_prin=Decimal("323585.37"), esc_bal=Decimal(0), prin_pmt=Decimal("567.16"),
            int_pmt=Decimal("808.96"), esc_pmt=Decimal(0), other_pmt=Decimal(0), paid_date=None,
            notes=" statement date is 2022-05-02")[0]

    @staticmethod
    def mortgage_bill_data_2():
        return MortgageBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ms(),
            start_date=datetime.date(2023, 1, 1), end_date=datetime.date(2023, 1, 31), total_cost=Decimal("1376.12"),
            tax_rel_cost=Decimal(0), outs_prin=Decimal("319008.21"), esc_bal=Decimal(0), prin_pmt=Decimal("578.60"),
            int_pmt=Decimal("797.52"), esc_pmt=Decimal(0), other_pmt=Decimal(0), paid_date=None,
            notes=" statement date is 2023-01-03")[0]

    @staticmethod
    def mortgage_bill_data_3():
        return MortgageBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ms(),
            start_date=datetime.date(2023, 7, 1), end_date=datetime.date(2023, 7, 31), total_cost=Decimal("1376.12"),
            tax_rel_cost=Decimal(0), outs_prin=Decimal("315514.83"), esc_bal=Decimal(0), prin_pmt=Decimal("587.33"),
            int_pmt=Decimal("788.79"), esc_pmt=Decimal(0), other_pmt=Decimal(0), paid_date=None,
            notes=" statement date is 2023-07-03")[0]