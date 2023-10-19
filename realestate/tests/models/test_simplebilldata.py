from decimal import Decimal
import datetime

from django.http import QueryDict

from ...models.simplebilldata import SimpleBillData
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
        ssbd = SimpleBillDataTests.simple_bill_data_1()
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
        sbd_test = SimpleBillDataTests.simple_bill_data_1()
        sbd = SimpleBillData.process_service_bill("testsimplebill1.csv")
        sbd.tax_rel_cost = Decimal(0)
        sbd_test.bill_file = sbd.bill_file
        self.equal(sbd, sbd_test)

    @staticmethod
    def simple_bill_data_1():
        return SimpleBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_simple_nbins(), start_date=datetime.date(2021, 9, 1),
            end_date=datetime.date(2021, 9, 30), total_cost=Decimal("224.45"), tax_rel_cost=Decimal(0),
            paid_date=datetime.date(2021, 9, 14), notes=None)[0]

    @staticmethod
    def simple_bill_data_2():
        return SimpleBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_simple_youtubetv(),
            start_date=datetime.date(2023, 1, 1), end_date=datetime.date(2023, 1, 31), total_cost=Decimal("32.50"),
            tax_rel_cost=Decimal("32.50"), paid_date=datetime.date(2023, 1, 23),
            notes=' This bill is a modification of the original bill. Ratio of 0.5 applied to total cost. Real estate '
                  'changed from original.')[0]

    @staticmethod
    def simple_bill_data_3():
        return SimpleBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_simple_youtubetv(),
            start_date=datetime.date(2023, 2, 1), end_date=datetime.date(2023, 2, 28), total_cost=Decimal("32.50"),
            tax_rel_cost=Decimal("32.50"), paid_date=datetime.date(2023, 2, 23),
            notes=' This bill is a modification of the original bill. Ratio of 0.5 applied to total cost. Real estate '
                  'changed from original.')[0]

    @staticmethod
    def simple_bill_data_4():
        return SimpleBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_simple_youtubetv(),
            start_date=datetime.date(2022, 2, 1), end_date=datetime.date(2022, 2, 28), total_cost=Decimal("32.50"),
            tax_rel_cost=Decimal("32.50"), paid_date=datetime.date(2022, 2, 23), notes=None)[0]

    @staticmethod
    def simple_bill_data_post_data():
        simple_bill_2 = SimpleBillDataTests.simple_bill_data_2()
        simple_bill_3 = SimpleBillDataTests.simple_bill_data_3()

        d = QueryDict(mutable=True)

        d['csrfmiddlewaretoken'] = 'VdTZ70OLMuZqoAtzG7ULoGj50i2Tz4T9t2FEMsdIDjaKfMWwT0rzkF6WQNt9xjw1'
        d['form-TOTAL_FORMS'] = '2'
        d['form-INITIAL_FORMS'] = '2'
        d['form-MIN_NUM_FORMS'] = '0'
        d['form-MAX_NUM_FORMS'] = '1000'

        d['form-0-real_estate'] = str(simple_bill_2.real_estate.pk)
        d['form-0-start_date'] = '2023-01-01'
        d['form-0-end_date'] = '2023-01-31'
        d['form-0-total_cost'] = '32.50'
        d['form-0-tax_rel_cost'] = '32.50'
        d['form-0-paid_date'] = '2023-01-23'
        d['form-0-notes'] = ' This bill is a modification of the original bill. Ratio of 0.5 applied to total cost. ' \
                            'Real estate changed from original.'
        d['form-0-service_provider'] = str(simple_bill_2.service_provider.pk)
        d['form-0-bill_file'] = ''
        d['form-0-id'] = str(simple_bill_2.pk)

        d['form-1-real_estate'] = str(simple_bill_3.real_estate.pk)
        d['form-1-start_date'] = '2023-02-01'
        d['form-1-end_date'] = '2023-02-28'
        d['form-1-total_cost'] = '32.50'
        d['form-1-tax_rel_cost'] = '32.50'
        d['form-1-paid_date'] = '2023-02-23'
        d['form-1-notes'] = ' This bill is a modification of the original bill. Ratio of 0.5 applied to total cost. ' \
                            'Real estate changed from original.'
        d['form-1-service_provider'] = str(simple_bill_3.service_provider.pk)
        d['form-1-bill_file'] = ''
        d['form-1-id'] = str(simple_bill_3.pk)

        return d