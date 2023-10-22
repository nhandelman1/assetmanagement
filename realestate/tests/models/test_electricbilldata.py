from decimal import Decimal
import datetime

from ...models.electricbilldata import ElectricBillData
from .test_realestate import RealEstateTests
from .test_serviceprovider import ServiceProviderTests
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


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
    def electric_bill_data_2(paid_date=None):
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
            st_cost=Decimal("2.23"), paid_date=paid_date, notes=None)[0]

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

    @staticmethod
    def electric_bill_data_4_act():
        return ElectricBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_pseg(), start_date=datetime.date(2022, 8, 16),
            end_date=datetime.date(2022, 9, 15), paid_date=datetime.date(2022, 10, 6), total_cost=Decimal("15.45"),
            tax_rel_cost=Decimal("0"), is_actual=True, total_kwh=0, eh_kwh=0, bank_kwh=965, bs_rate=Decimal("0.46"),
            bs_cost=Decimal("14.26"), dsc_total_cost=Decimal("14.26"), dsa_cost=Decimal("0.61"),
            rda_cost=Decimal("-0.53"), nysa_cost=Decimal("0.05"), rbp_cost=Decimal("0.37"), spta_cost=Decimal("0.31"),
            st_rate=Decimal("0.0250"), st_cost=Decimal("0.38"), toc_total_cost=Decimal("1.19"))[0]

    @staticmethod
    def electric_bill_data_4_est():
        return ElectricBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_pseg(), start_date=datetime.date(2022, 8, 16),
            end_date=datetime.date(2022, 9, 15), paid_date=None, total_cost=Decimal("160.67"),
            tax_rel_cost=Decimal("0"), is_actual=False, total_kwh=559, eh_kwh=0, bank_kwh=0, bs_rate=Decimal("0.46"),
            bs_cost=Decimal("14.26"), first_kwh=275, first_rate=Decimal("0.091"), first_cost=Decimal("25.03"),
            next_kwh=284, next_rate=Decimal("0.1152"), next_cost=Decimal("32.72"), dsc_total_cost=Decimal("72.00"),
            psc_rate=Decimal("0.136126"), psc_cost=Decimal("76.09"), psc_total_cost=Decimal("76.09"),
            der_rate=Decimal("0.003715"), der_cost=Decimal("2.08"), dsa_rate=Decimal("0.042267"),
            dsa_cost=Decimal("3.04"), rda_rate=Decimal("-0.03667"), rda_cost=Decimal("-2.64"),
            nysa_rate=Decimal("0.003772"), nysa_cost=Decimal("0.57"), rbp_rate=Decimal("0.025299"),
            rbp_cost=Decimal("1.82"), spta_rate=Decimal("0.021187"), spta_cost=Decimal("3.20"),
            st_rate=Decimal("0.0250"), st_cost=Decimal("3.90"), toc_total_cost=Decimal("11.98"))[0]

    @staticmethod
    def electric_bill_data_5_act():
        return ElectricBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_pseg(), start_date=datetime.date(2022, 9, 16),
            end_date=datetime.date(2022, 10, 14), paid_date=datetime.date(2022, 11, 8), total_cost=Decimal("14.45"),
            tax_rel_cost=Decimal("0"), is_actual=True, total_kwh=0, eh_kwh=0, bank_kwh=1426, bs_rate=Decimal("0.46"),
            bs_cost=Decimal("13.34"), dsc_total_cost=Decimal("13.34"), dsa_cost=Decimal("0.57"),
            rda_cost=Decimal("-0.5"), nysa_cost=Decimal("0.05"), rbp_cost=Decimal("0.35"), spta_cost=Decimal("0.29"),
            st_rate=Decimal("0.0250"), st_cost=Decimal("0.35"), toc_total_cost=Decimal("1.11"))[0]

    @staticmethod
    def electric_bill_data_5_est():
        return ElectricBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_pseg(), start_date=datetime.date(2022, 9, 16),
            end_date=datetime.date(2022, 10, 14), paid_date=None, total_cost=Decimal("107.71"),
            tax_rel_cost=Decimal("0"), is_actual=False, total_kwh=373, eh_kwh=0, bank_kwh=0, bs_rate=Decimal("0.46"),
            bs_cost=Decimal("13.34"), first_kwh=275, first_rate=Decimal("0.091"), first_cost=Decimal("25.03"),
            next_kwh=98, next_rate=Decimal("0.1152"), next_cost=Decimal("11.29"), dsc_total_cost=Decimal("49.65"),
            psc_rate=Decimal("0.133983"), psc_cost=Decimal("49.98"), psc_total_cost=Decimal("49.98"),
            der_rate=Decimal("0.003715"), der_cost=Decimal("1.39"), dsa_rate=Decimal("0.042267"),
            dsa_cost=Decimal("2.10"), rda_rate=Decimal("-0.03667"), rda_cost=Decimal("-1.82"),
            nysa_rate=Decimal("0.003772"), nysa_cost=Decimal("0.38"), rbp_rate=Decimal("0.025299"),
            rbp_cost=Decimal("1.26"), spta_rate=Decimal("0.021187"), spta_cost=Decimal("2.14"),
            st_rate=Decimal("0.0250"), st_cost=Decimal("2.63"), toc_total_cost=Decimal("8.08"))[0]

    @staticmethod
    def electric_bill_data_6_act():
        return ElectricBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_pseg(), start_date=datetime.date(2023, 1, 18),
            end_date=datetime.date(2023, 2, 14), paid_date=datetime.date(2023, 3, 7), total_cost=Decimal("41.93"),
            tax_rel_cost=Decimal("0"), is_actual=True, total_kwh=107, eh_kwh=0, bank_kwh=0, bs_rate=Decimal("0.48"),
            bs_cost=Decimal("13.44"), first_kwh=107, first_rate=Decimal("0.0916"), first_cost=Decimal("9.8"),
            cbc_rate=Decimal("0.0195"), cbc_cost=Decimal("4.91"), mfc_rate=Decimal("0.002430"),
            mfc_cost=Decimal("0.26"), dsc_total_cost=Decimal("28.41"), psc_rate=Decimal("0.114788"),
            psc_cost=Decimal("12.88"), psc_total_cost=Decimal("12.28"), der_rate=Decimal("0.005228"),
            der_cost=Decimal("0.56"), dsa_cost=Decimal("-0.02"), rda_cost=Decimal("-1.98"), nysa_cost=Decimal("0.15"),
            rbp_cost=Decimal("0.72"), spta_cost=Decimal("0.79"), st_rate=Decimal("0.0250"), st_cost=Decimal("1.02"),
            toc_total_cost=Decimal("1.24"))[0]

    @staticmethod
    def electric_bill_data_6_est():
        return ElectricBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_pseg(), start_date=datetime.date(2023, 1, 18),
            end_date=datetime.date(2023, 2, 14), paid_date=None, total_cost=Decimal("188.26"),
            tax_rel_cost=Decimal("0"), is_actual=False, total_kwh=795, eh_kwh=100, bank_kwh=0, bs_rate=Decimal("0.48"),
            bs_cost=Decimal("13.44"), first_kwh=250, first_rate=Decimal("0.0916"), first_cost=Decimal("22.90"),
            next_kwh=545, next_rate=Decimal("0.0916"), next_cost=Decimal("49.92"), mfc_rate=Decimal("0.002430"),
            mfc_cost=Decimal("1.92"), dsc_total_cost=Decimal("88.18"), psc_rate=Decimal("0.114788"),
            psc_cost=Decimal("91.26"), psc_total_cost=Decimal("91.26"), der_rate=Decimal("0.005228"),
            der_cost=Decimal("4.16"), dsa_rate=Decimal("-0.000740"), dsa_cost=Decimal("-0.07"),
            rda_rate=Decimal("-0.06978"), rda_cost=Decimal("-6.15"), nysa_rate=Decimal("0.00276"),
            nysa_cost=Decimal("0.49"), rbp_rate=Decimal("0.025299"), rbp_cost=Decimal("2.23"),
            spta_rate=Decimal("0.020121"), spta_cost=Decimal("3.58"), st_rate=Decimal("0.0250"),
            st_cost=Decimal("4.59"), toc_total_cost=Decimal("8.83"))[0]

    @staticmethod
    def electric_bill_data_7_act():
        return ElectricBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_pseg(), start_date=datetime.date(2023, 2, 15),
            end_date=datetime.date(2023, 3, 14), paid_date=datetime.date(2023, 4, 6), total_cost=Decimal("46.49"),
            tax_rel_cost=Decimal("0"), is_actual=True, total_kwh=136, eh_kwh=0, bank_kwh=0, bs_rate=Decimal("0.48"),
            bs_cost=Decimal("13.44"), first_kwh=136, first_rate=Decimal("0.0916"), first_cost=Decimal("12.46"),
            cbc_rate=Decimal("0.0195"), cbc_cost=Decimal("4.91"), mfc_rate=Decimal("0.002426"),
            mfc_cost=Decimal("0.33"), dsc_total_cost=Decimal("31.14"), psc_rate=Decimal("0.102002"),
            psc_cost=Decimal("13.87"), psc_total_cost=Decimal("13.87"), der_rate=Decimal("0.005228"),
            der_cost=Decimal("0.71"), dsa_cost=Decimal("-0.02"), rda_cost=Decimal("-2.17"), nysa_cost=Decimal("0.17"),
            rbp_cost=Decimal("0.78"), spta_cost=Decimal("0.88"), st_rate=Decimal("0.0250"), st_cost=Decimal("1.13"),
            toc_total_cost=Decimal("1.24"))[0]

    @staticmethod
    def electric_bill_data_7_est():
        return ElectricBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_pseg(), start_date=datetime.date(2023, 2, 15),
            end_date=datetime.date(2023, 3, 14), paid_date=None, total_cost=Decimal("172.24"),
            tax_rel_cost=Decimal("0"), is_actual=False, total_kwh=769, eh_kwh=0, bank_kwh=0, bs_rate=Decimal("0.48"),
            bs_cost=Decimal("13.44"), first_kwh=250, first_rate=Decimal("0.0916"), first_cost=Decimal("22.90"),
            next_kwh=519, next_rate=Decimal("0.0916"), next_cost=Decimal("47.54"), mfc_rate=Decimal("0.002430"),
            mfc_cost=Decimal("1.85"), dsc_total_cost=Decimal("85.73"), psc_rate=Decimal("0.102002"),
            psc_cost=Decimal("78.44"), psc_total_cost=Decimal("78.44"), der_rate=Decimal("0.005228"),
            der_cost=Decimal("4.02"), dsa_rate=Decimal("-0.000740"), dsa_cost=Decimal("-0.06"),
            rda_rate=Decimal("-0.06978"), rda_cost=Decimal("-5.98"), nysa_rate=Decimal("0.00276"),
            nysa_cost=Decimal("0.45"), rbp_rate=Decimal("0.025299"), rbp_cost=Decimal("2.17"),
            spta_rate=Decimal("0.020121"), spta_cost=Decimal("3.27"), st_rate=Decimal("0.0250"),
            st_cost=Decimal("4.20"), toc_total_cost=Decimal("8.06"))[0]