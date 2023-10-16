from decimal import Decimal
import datetime

from ...models.electricbilldata import ElectricBillData
from .djangomodeltestcasebase import DjangoModelTestCaseBase
from .test_realestate import RealEstateTests
from .test_serviceprovider import ServiceProviderTests


class ElectricBillDataTests(DjangoModelTestCaseBase):

    def equal(self, model1: ElectricBillData, model2: ElectricBillData):
        RealEstateTests().equal(model1.real_estate, model2.real_estate)
        ServiceProviderTests().equal(model1.service_provider, model2.service_provider)
        self.simple_equal(model1, model2, ElectricBillData, rem_attr_list=["real_estate", "service_provider"])

    def test_modify(self):
        # modify but with no changes except to notes
        ebd = ElectricBillDataTests.electric_bill_data_1()
        ebd_copy = ebd.modify()
        ebd.notes = " This bill is a modification of the original bill."
        ebd.clean_fields()
        self.equal(ebd, ebd_copy)

        # modify but with cost_ratio applied to attributes and real_estate changed
        ebd = ElectricBillData.objects.get(pk=ebd.pk)
        ebd_copy = ebd.modify(cost_ratio=Decimal("0.5"), real_estate=RealEstateTests.real_estate_10wlapt1())
        ebd.real_estate = RealEstateTests.real_estate_10wlapt1()
        ebd.total_cost = Decimal("67.125")
        ebd.notes = ' This bill is a modification of the original bill. Ratio of 0.5 applied to total cost. ' \
                    'Real estate changed from original. Ratio of 0.5 applied to KWH, cost and BS Rate attributes.'

        ebd.total_kwh = 273
        ebd.eh_kwh = 0
        ebd.bank_kwh = 0
        ebd.bs_rate = Decimal("0.22")
        ebd.bs_cost = Decimal("6.82")
        ebd.first_kwh = 129
        ebd.first_cost = Decimal("11.235")
        ebd.next_kwh = 144
        ebd.next_cost = Decimal("15.855")
        ebd.cbc_cost = None
        ebd.mfc_cost = None
        ebd.dsc_total_cost = Decimal("33.91")
        ebd.psc_cost = Decimal("29.475")
        ebd.psc_total_cost = Decimal("29.475")
        ebd.der_cost = Decimal("0.96")
        ebd.dsa_cost = Decimal("0.745")
        ebd.rda_cost = Decimal("-2.10")
        ebd.nysa_cost = Decimal("0.165")
        ebd.rbp_cost = Decimal("0.825")
        ebd.spta_cost = Decimal("1.51")
        ebd.st_cost = Decimal("1.635")
        ebd.toc_total_cost = Decimal("3.74")
        self.equal(ebd, ebd_copy)

    def test_process_service_bill(self):
        ebd_test = ElectricBillDataTests.electric_bill_data_1()
        ebd = ElectricBillData.process_service_bill("testpsegbill1.pdf")
        ebd.tax_rel_cost = Decimal("134.25")
        ebd_test.bill_file = ebd.bill_file
        self.equal(ebd, ebd_test)

        ebd_test = ElectricBillDataTests.electric_bill_data_2()
        ebd = ElectricBillData.process_service_bill("testpsegbill2.pdf")
        ebd.tax_rel_cost = Decimal("91.47")
        ebd_test.bill_file = ebd.bill_file
        self.equal(ebd, ebd_test)

        ebd_test = ElectricBillDataTests.electric_bill_data_3()
        ebd = ElectricBillData.process_service_bill("testpsegbill3.pdf")
        ebd.tax_rel_cost = Decimal("46.49")
        ebd_test.bill_file = ebd.bill_file
        self.equal(ebd, ebd_test)

    @staticmethod
    def electric_bill_data_1():
        return ElectricBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_pseg(), start_date=datetime.date(2021, 7, 17),
            end_date=datetime.date(2021, 8, 16), total_cost=Decimal("134.25"), tax_rel_cost=Decimal("134.25"),
            is_actual=True, total_kwh=546, eh_kwh=0, bank_kwh=0, bs_rate=Decimal("0.44"), bs_cost=Decimal("13.64"),
            dsc_total_cost=Decimal("67.82"), toc_total_cost=Decimal("7.48"), first_kwh=258,
            first_rate=Decimal("0.0871"), first_cost=Decimal("22.47"), next_kwh=288, next_rate=Decimal("0.1101"),
            next_cost=Decimal("31.71"), cbc_rate=None, cbc_cost=None, mfc_rate=None, mfc_cost=None,
            psc_rate=Decimal("0.107960"), psc_cost=Decimal("58.95"), psc_total_cost=Decimal("58.95"),
            der_rate=Decimal("0.003521"), der_cost=Decimal("1.92"), dsa_rate=None, dsa_cost=Decimal("1.49"),
            rda_rate=None, rda_cost=Decimal("-4.20"), nysa_rate=None, nysa_cost=Decimal("0.33"), rbp_rate=None,
            rbp_cost=Decimal("1.65"), spta_rate=None, spta_cost=Decimal("3.02"), st_rate=Decimal("0.0250"),
            st_cost=Decimal("3.27"), paid_date=None, notes=None)[0]

    @staticmethod
    def electric_bill_data_2():
        return ElectricBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_pseg(), start_date=datetime.date(2022, 5, 17),
            end_date=datetime.date(2022, 6, 14), total_cost=Decimal("91.47"), tax_rel_cost=Decimal("91.47"),
            is_actual=True, total_kwh=317, eh_kwh=0, bank_kwh=0, bs_rate=Decimal("0.46"), bs_cost=Decimal("13.34"),
            dsc_total_cost=Decimal("43.06"), toc_total_cost=Decimal("7.04"), first_kwh=242,
            first_rate=Decimal("0.0910"), first_cost=Decimal("22.02"), next_kwh=75, next_rate=Decimal("0.1027"),
            next_cost=Decimal("7.70"), cbc_rate=None, cbc_cost=None, mfc_rate=None, mfc_cost=None,
            psc_rate=Decimal("0.130505"), psc_cost=Decimal("41.37"), psc_total_cost=Decimal("41.37"),
            der_rate=Decimal("0.003715"), der_cost=Decimal("1.18"), dsa_rate=None, dsa_cost=Decimal("1.85"),
            rda_rate=None, rda_cost=Decimal("-1.61"), nysa_rate=None, nysa_cost=Decimal("0.33"), rbp_rate=None,
            rbp_cost=Decimal("1.22"), spta_rate=None, spta_cost=Decimal("1.84"), st_rate=Decimal("0.0250"),
            st_cost=Decimal("2.23"), paid_date=None, notes=None)[0]

    @staticmethod
    def electric_bill_data_3():
        return ElectricBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_pseg(), start_date=datetime.date(2023, 2, 15),
            end_date=datetime.date(2023, 3, 14), total_cost=Decimal("46.49"), tax_rel_cost=Decimal("46.49"),
            is_actual=True, total_kwh=136, eh_kwh=0, bank_kwh=0, bs_rate=Decimal("0.48"), bs_cost=Decimal("13.44"),
            dsc_total_cost=Decimal("31.14"), toc_total_cost=Decimal("1.48"), first_kwh=136,
            first_rate=Decimal("0.0916"), first_cost=Decimal("12.46"), next_kwh=None, next_rate=None, next_cost=None,
            cbc_rate=Decimal("0.0195"), cbc_cost=Decimal("4.91"), mfc_rate=Decimal("0.002426"),
            mfc_cost=Decimal("0.33"), psc_rate=Decimal("0.102002"), psc_cost=Decimal("13.87"),
            psc_total_cost=Decimal("13.87"), der_rate=Decimal("0.005228"), der_cost=Decimal("0.71"), dsa_rate=None,
            dsa_cost=Decimal("-0.02"), rda_rate=None, rda_cost=Decimal("-2.17"), nysa_rate=None,
            nysa_cost=Decimal("0.17"), rbp_rate=None, rbp_cost=Decimal("0.78"), spta_rate=None,
            spta_cost=Decimal("0.88"), st_rate=Decimal("0.0250"), st_cost=Decimal("1.13"), paid_date=None,
            notes=None)[0]