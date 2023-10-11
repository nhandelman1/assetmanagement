from decimal import Decimal
import datetime

from ..models import SimpleBillData
from .djangomodeltestcasebase import DjangoModelTestCaseBase
from .test_realestate import RealEstateTests
from .test_serviceprovider import ServiceProviderTests


class SimpleBillDataTests(DjangoModelTestCaseBase):

    def equal(self, model1: SimpleBillData, model2: SimpleBillData):
        RealEstateTests().equal(model1.real_estate, model2.real_estate)
        ServiceProviderTests().equal(model1.service_provider, model2.service_provider)
        self.simple_equal(model1, model2, SimpleBillData, rem_attr_list=["real_estate", "service_provider"])

    def test_modify(self):
        """
            return SimpleBillData.objects.get_or_create(
        real_estate=real_estate_10wl(), service_provider=service_provider_simple(),
        start_date=datetime.date(2021, 9, 1), end_date=datetime.date(2021, 9, 30),
        total_cost=Decimal("224.45"), tax_rel_cost=Decimal(0), paid_date=datetime.date(2021, 9, 14),
        notes=None)[0]

        """
        # modify but with no changes except to notes
        ssbd = SimpleBillDataTests.simple_bill_data()
        ssbd_copy = ssbd.modify()
        ssbd.notes = " This bill is a modification of the original bill."
        ssbd.clean_fields()
        self.equal(ssbd, ssbd_copy)

        # modify but with cost_ratio applied to total_cost and real_estate changed
        ssbd = SimpleBillData.objects.get(pk=ssbd.pk)
        ssbd_copy = ssbd.modify(cost_ratio=Decimal("0.5"), real_estate=RealEstateTests.real_estate_10wlapt1())

        ssbd.real_estate = RealEstateTests.real_estate_10wlapt1()
        ssbd.total_cost = Decimal("112.225")
        ssbd.notes = ' This bill is a modification of the original bill. Ratio of 0.5 applied to total ' \
                     'cost. Real estate changed from original.'

        self.equal(ssbd, ssbd_copy)

        # test ValueError is raised if cost_ratio is invalid value
        with self.assertRaises(ValueError):
            ssbd_copy = ssbd.modify(cost_ratio=Decimal("1.01"))

    def test_process_service_bill(self):
        sbd_test = SimpleBillDataTests.simple_bill_data()
        sbd = SimpleBillData.process_service_bill("testsimplebill1.csv")
        sbd.tax_rel_cost = Decimal(0)
        sbd_test.bill_file = sbd.bill_file
        self.equal(sbd, sbd_test)

    @staticmethod
    def simple_bill_data():
        return SimpleBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_simple(), start_date=datetime.date(2021, 9, 1),
            end_date=datetime.date(2021, 9, 30), total_cost=Decimal("224.45"), tax_rel_cost=Decimal(0),
            paid_date=datetime.date(2021, 9, 14), notes=None)[0]