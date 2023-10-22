from decimal import Decimal
import datetime

from ...models.natgasbilldata import NatGasBillData
from .test_realestate import RealEstateTests
from .test_serviceprovider import ServiceProviderTests
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class NatGasBillDataTests(DjangoModelTestCaseBase):

    def equal(self, model1: NatGasBillData, model2: NatGasBillData):
        RealEstateTests().equal(model1.real_estate, model2.real_estate)
        ServiceProviderTests().equal(model1.service_provider, model2.service_provider)
        self.simple_equal(model1, model2, NatGasBillData,
                          rem_attr_list=["real_estate", "service_provider"])

    def test_modify(self):
        # modify but with no changes except to notes
        nbd = NatGasBillDataTests.natgas_bill_data_1()
        nbd_copy = nbd.modify()
        nbd.notes = " This bill is a modification of the original bill."
        nbd.clean_fields()
        self.equal(nbd, nbd_copy)

        # modify but with cost_ratio applied to attributes and real_estate changed
        nbd = NatGasBillData.objects.get(pk=nbd.pk)
        nbd.saved_therms = 10
        nbd_copy = nbd.modify(cost_ratio=Decimal("0.5"), real_estate=RealEstateTests.real_estate_10wlapt1())
        nbd.real_estate = RealEstateTests.real_estate_10wlapt1()
        nbd.total_cost = Decimal("8.79")
        nbd.notes = ' This bill is a modification of the original bill. Ratio of 0.5 applied to total ' \
                    'cost. Real estate changed from original. Ratio of 0.5 applied to therms and cost attributes.'

        nbd.total_therms = 2
        nbd.saved_therms = 5
        nbd.bsc_therms = Decimal("0.75")
        nbd.bsc_cost = Decimal("5.415")
        nbd.next_therms = Decimal("1.25")
        nbd.next_cost = Decimal("1.605")
        nbd.over_therms = None
        nbd.over_cost = None
        nbd.dra_cost = Decimal("-0.09")
        nbd.sbc_cost = Decimal("0.03")
        nbd.tac_cost = None
        nbd.bc_cost = Decimal("0.66")
        nbd.ds_nysls_cost = Decimal("0.165")
        nbd.ds_nysst_cost = Decimal("0.19")
        nbd.ds_total_cost = Decimal("7.975")
        nbd.gs_cost = Decimal("0.965")
        nbd.ss_nysls_cost = None
        nbd.ss_nysst_cost = Decimal("0.025")
        nbd.ss_total_cost = Decimal("0.99")
        nbd.pbc_cost = Decimal("-0.175")
        nbd.oca_total_cost = Decimal("-0.175")

        self.equal(nbd, nbd_copy)

    def test_process_service_bill(self):
        ebd_test = NatGasBillDataTests.natgas_bill_data_1()
        ebd = NatGasBillData.process_service_bill("testnatgasbill1.pdf")
        ebd.tax_rel_cost = Decimal(0)
        ebd_test.bill_file = ebd.bill_file
        self.equal(ebd, ebd_test)

        ebd_test = NatGasBillDataTests.natgas_bill_data_2()
        ebd = NatGasBillData.process_service_bill("testnatgasbill2.pdf")
        ebd.tax_rel_cost = Decimal(0)
        ebd_test.bill_file = ebd.bill_file
        self.equal(ebd, ebd_test)

        ebd_test = NatGasBillDataTests.natgas_bill_data_3()
        ebd = NatGasBillData.process_service_bill("testnatgasbill3.pdf")
        ebd.tax_rel_cost = Decimal(0)
        ebd_test.bill_file = ebd.bill_file
        self.equal(ebd, ebd_test)

    @staticmethod
    def natgas_bill_data_1():
        return NatGasBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ng(),
            start_date=datetime.date(2021, 7, 16), end_date=datetime.date(2021, 7, 30), total_cost=Decimal("17.58"),
            tax_rel_cost=Decimal(0), is_actual=True, total_therms=4, saved_therms=0, bsc_therms=Decimal("1.5"),
            bsc_cost=Decimal("10.83"), next_therms=Decimal("2.5"), next_rate=Decimal("1.2839"),
            next_cost=Decimal("3.21"), ds_total_cost=Decimal("15.95"), gs_rate=Decimal("0.479610"),
            gs_cost=Decimal("1.93"), ss_total_cost=Decimal("1.98"), oca_total_cost=Decimal("-0.35"), over_therms=None,
            over_rate=None, over_cost=None, dra_rate=Decimal("-0.047480"), dra_cost=Decimal("-0.18"),
            sbc_rate=Decimal("0.01552"), sbc_cost=Decimal("0.06"), tac_rate=None, tac_cost=None,
            bc_cost=Decimal("1.32"), ds_nysls_rate=None, ds_nysls_cost=Decimal("0.33"), ds_nysst_rate=Decimal("0.0250"),
            ds_nysst_cost=Decimal("0.38"), ss_nysls_rate=None, ss_nysls_cost=None, ss_nysst_rate=Decimal("0.0250"),
            ss_nysst_cost=Decimal("0.05"), pbc_cost=Decimal("-0.35"), paid_date=None, notes=None)[0]

    @staticmethod
    def natgas_bill_data_2(paid_date=None):
        return NatGasBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ng(),
            start_date=datetime.date(2022, 12, 1), end_date=datetime.date(2022, 12, 29), total_cost=Decimal("213.68"),
            tax_rel_cost=Decimal(0), is_actual=True, total_therms=114, saved_therms=0, bsc_therms=Decimal("2.9"),
            bsc_cost=Decimal("20.94"), next_therms=Decimal("45.4"), next_rate=Decimal("1.3435"),
            next_cost=Decimal("60.99"), ds_total_cost=Decimal("111.32"), gs_rate=Decimal("0.879265"),
            gs_cost=Decimal("100.24"), ss_total_cost=Decimal("102.77"), oca_total_cost=Decimal("-0.41"),
            over_therms=Decimal("65.7"), over_rate=Decimal("0.3163"), over_cost=Decimal("20.78"),
            dra_rate=Decimal("0.020924"), dra_cost=Decimal("2.40"), sbc_rate=None, sbc_cost=None, tac_rate=None,
            tac_cost=None, bc_cost=Decimal("1.32"), ds_nysls_rate=None, ds_nysls_cost=Decimal("2.18"),
            ds_nysst_rate=Decimal("0.0250"), ds_nysst_cost=Decimal("2.71"), ss_nysls_rate=None,
            ss_nysls_cost=Decimal("0.02"), ss_nysst_rate=Decimal("0.0250"), ss_nysst_cost=Decimal("2.51"),
            pbc_cost=Decimal("-0.41"), paid_date=paid_date, notes=None)[0]

    @staticmethod
    def natgas_bill_data_3():
        return NatGasBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ng(),
            start_date=datetime.date(2023, 6, 1), end_date=datetime.date(2023, 6, 29), total_cost=Decimal("75.56"),
            tax_rel_cost=Decimal(0), is_actual=True, total_therms=27, saved_therms=0, bsc_therms=Decimal("2.9"),
            bsc_cost=Decimal("20.94"), next_therms=Decimal("24.1"), next_rate=Decimal("1.3528"),
            next_cost=Decimal("32.60"), ds_total_cost=Decimal("56.73"), gs_rate=Decimal("0.695"),
            gs_cost=Decimal("18.77"), ss_total_cost=Decimal("19.24"), oca_total_cost=Decimal("-0.41"), over_therms=None,
            over_rate=None, over_cost=None, dra_rate=Decimal("0.03591"), dra_cost=Decimal("0.97"), sbc_rate=None,
            sbc_cost=None, tac_rate=Decimal("-0.010797"), tac_cost=Decimal("-0.29"), bc_cost=None, ds_nysls_rate=None,
            ds_nysls_cost=Decimal("1.14"), ds_nysst_rate=Decimal("0.0250"), ds_nysst_cost=Decimal("1.37"),
            ss_nysls_rate=None, ss_nysls_cost=None, ss_nysst_rate=Decimal("0.0250"), ss_nysst_cost=Decimal("0.47"),
            pbc_cost=Decimal("-0.41"), paid_date=None,
            notes="No supply services sales tax provided. Assumed to be 0.025.")[0]

    @staticmethod
    def natgas_bill_data_4_act():
        return NatGasBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ng(),
            start_date=datetime.date(2022, 12, 1), end_date=datetime.date(2022, 12, 29),
            paid_date=datetime.date(2023, 1, 23), total_cost=Decimal("213.68"), tax_rel_cost=Decimal(0), is_actual=True,
            total_therms=114, saved_therms=0, bsc_therms=Decimal("2.9"), bsc_cost=Decimal("20.94"),
            next_therms=Decimal("45.40"), next_rate=Decimal("1.3435"), next_cost=Decimal("60.99"),
            over_therms=Decimal("65.7"), over_rate=Decimal("0.3163"), over_cost=Decimal("20.78"),
            dra_rate=Decimal("0.020924"), dra_cost=Decimal("2.40"), bc_cost=Decimal("1.32"),
            ds_nysls_cost=Decimal("2.18"), ds_nysst_rate=Decimal("0.0250"), ds_nysst_cost=Decimal("2.71"),
            ds_total_cost=Decimal("111.32"), gs_rate=Decimal("0.879265"), gs_cost=Decimal("100.24"),
            ss_nysls_cost=Decimal("0.02"), ss_nysst_rate=Decimal("0.0250"), ss_nysst_cost=Decimal("2.51"),
            ss_total_cost=Decimal("102.77"), pbc_cost=Decimal("-0.41"), oca_total_cost=Decimal("-0.41"))[0]

    @staticmethod
    def natgas_bill_data_4_est():
        return NatGasBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ng(),
            start_date=datetime.date(2022, 12, 1), end_date=datetime.date(2022, 12, 29), paid_date=None,
            total_cost=Decimal("221.66"), tax_rel_cost=Decimal(0), is_actual=False, total_therms=119, saved_therms=5,
            bsc_therms=Decimal("2.9"), bsc_cost=Decimal("20.94"), next_therms=Decimal("47.00"),
            next_rate=Decimal("1.3435"), next_cost=Decimal("63.14"), over_therms=Decimal("69.1"),
            over_rate=Decimal("0.3163"), over_cost=Decimal("21.68"), dra_rate=Decimal("0.020924"),
            dra_cost=Decimal("2.49"), bc_cost=Decimal("1.32"), ds_nysls_rate=Decimal("0.020483"),
            ds_nysls_cost=Decimal("2.25"), ds_nysst_rate=Decimal("0.0250"), ds_nysst_cost=Decimal("2.80"),
            ds_total_cost=Decimal("114.80"), gs_rate=Decimal("0.879265"), gs_cost=Decimal("104.63"),
            ss_nysls_rate=Decimal("0.000200"), ss_nysls_cost=Decimal("0.02"), ss_nysst_rate=Decimal("0.0250"),
            ss_nysst_cost=Decimal("2.62"), ss_total_cost=Decimal("107.27"), pbc_cost=Decimal("-0.41"),
            oca_total_cost=Decimal("-0.41"))[0]

    @staticmethod
    def natgas_bill_data_5_act():
        return NatGasBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ng(),
            start_date=datetime.date(2022, 12, 30), end_date=datetime.date(2023, 1, 30),
            paid_date=datetime.date(2023, 2, 24), total_cost=Decimal("200.44"), tax_rel_cost=Decimal(0), is_actual=True,
            total_therms=93, saved_therms=0, bsc_therms=Decimal("3.2"), bsc_cost=Decimal("23.10"),
            next_therms=Decimal("50.1"), next_rate=Decimal("1.3435"), next_cost=Decimal("67.31"),
            over_therms=Decimal("39.7"), over_rate=Decimal("0.3163"), over_cost=Decimal("12.56"),
            dra_rate=Decimal("0.162585"), dra_cost=Decimal("15.11"), bc_cost=Decimal("1.32"),
            ds_nysls_cost=Decimal("2.45"), ds_nysst_rate=Decimal("0.0250"), ds_nysst_cost=Decimal("3.04"),
            ds_total_cost=Decimal("124.89"), gs_rate=Decimal("0.796640"), gs_cost=Decimal("74.10"),
            ss_nysls_cost=Decimal("0.01"), ss_nysst_rate=Decimal("0.0250"), ss_nysst_cost=Decimal("1.85"),
            ss_total_cost=Decimal("75.96"), pbc_cost=Decimal("-0.41"), oca_total_cost=Decimal("-0.41"))[0]

    @staticmethod
    def natgas_bill_data_5_est():
        return NatGasBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ng(),
            start_date=datetime.date(2022, 12, 30), end_date=datetime.date(2023, 1, 30), paid_date=None,
            total_cost=Decimal("291.98"), tax_rel_cost=Decimal(0), is_actual=False, total_therms=165, saved_therms=72,
            bsc_therms=Decimal("3.2"), bsc_cost=Decimal("23.10"), next_therms=Decimal("47.00"),
            next_rate=Decimal("1.3435"), next_cost=Decimal("63.14"), over_therms=Decimal("114.8"),
            over_rate=Decimal("0.3163"), over_cost=Decimal("36.31"), dra_rate=Decimal("0.162585"),
            dra_cost=Decimal("26.83"), bc_cost=Decimal("1.32"), ds_nysls_rate=Decimal("0.020519"),
            ds_nysls_cost=Decimal("3.09"), ds_nysst_rate=Decimal("0.0250"), ds_nysst_cost=Decimal("3.84"),
            ds_total_cost=Decimal("157.64"), gs_rate=Decimal("0.796640"), gs_cost=Decimal("131.45"),
            ss_nysls_rate=Decimal("0.000135"), ss_nysls_cost=Decimal("0.02"), ss_nysst_rate=Decimal("0.0250"),
            ss_nysst_cost=Decimal("3.29"), ss_total_cost=Decimal("134.75"), pbc_cost=Decimal("-0.41"),
            oca_total_cost=Decimal("-0.41"))[0]

    @staticmethod
    def natgas_bill_data_6_act():
        return NatGasBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ng(),
            start_date=datetime.date(2023, 3, 1), end_date=datetime.date(2023, 3, 30),
            paid_date=datetime.date(2023, 4, 26), total_cost=Decimal("172.99"), tax_rel_cost=Decimal(0), is_actual=True,
            total_therms=99, saved_therms=0, bsc_therms=Decimal("3.0"), bsc_cost=Decimal("21.66"),
            next_therms=Decimal("47.0"), next_rate=Decimal("1.3435"), next_cost=Decimal("63.14"),
            over_therms=Decimal("49.0"), over_rate=Decimal("0.3163"), over_cost=Decimal("15.50"),
            dra_rate=Decimal("0.072849"), dra_cost=Decimal("7.22"), bc_cost=Decimal("1.32"),
            ds_nysls_cost=Decimal("2.29"), ds_nysst_rate=Decimal("0.0250"), ds_nysst_cost=Decimal("2.77"),
            ds_total_cost=Decimal("113.90"), gs_rate=Decimal("0.585963"), gs_cost=Decimal("58.01"),
            ss_nysls_cost=Decimal("0.04"), ss_nysst_rate=Decimal("0.0250"), ss_nysst_cost=Decimal("1.45"),
            ss_total_cost=Decimal("59.50"), pbc_cost=Decimal("-0.41"), oca_total_cost=Decimal("-0.41"))[0]

    @staticmethod
    def natgas_bill_data_6_est():
        return NatGasBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ng(),
            start_date=datetime.date(2023, 3, 1), end_date=datetime.date(2023, 3, 30), paid_date=None,
            total_cost=Decimal("172.99"), tax_rel_cost=Decimal(0), is_actual=False, total_therms=99, saved_therms=0,
            bsc_therms=Decimal("3.0"), bsc_cost=Decimal("21.66"), next_therms=Decimal("47.0"),
            next_rate=Decimal("1.3435"), next_cost=Decimal("63.14"), over_therms=Decimal("49.0"),
            over_rate=Decimal("0.3163"), over_cost=Decimal("15.50"), dra_rate=Decimal("0.072849"),
            dra_cost=Decimal("7.22"), bc_cost=Decimal("1.32"), ds_nysls_rate=Decimal("0.021040"),
            ds_nysls_cost=Decimal("2.29"), ds_nysst_rate=Decimal("0.0250"), ds_nysst_cost=Decimal("2.77"),
            ds_total_cost=Decimal("113.90"), gs_rate=Decimal("0.585963"), gs_cost=Decimal("58.01"),
            ss_nysls_rate=Decimal("0.000690"), ss_nysls_cost=Decimal("0.04"), ss_nysst_rate=Decimal("0.0250"),
            ss_nysst_cost=Decimal("1.45"), ss_total_cost=Decimal("59.50"), pbc_cost=Decimal("-0.41"),
            oca_total_cost=Decimal("-0.41"))[0]

    @staticmethod
    def natgas_bill_data_7_act():
        return NatGasBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ng(),
            start_date=datetime.date(2023, 3, 31), end_date=datetime.date(2023, 4, 30),
            paid_date=datetime.date(2023, 5, 31), total_cost=Decimal("103.15"), tax_rel_cost=Decimal(0), is_actual=True,
            total_therms=39, saved_therms=0, bsc_therms=Decimal("3.1"), bsc_cost=Decimal("22.38"),
            next_therms=Decimal("35.9"), next_rate=Decimal("1.3521"), next_cost=Decimal("48.54"),
            dra_rate=Decimal("0.320998"), dra_cost=Decimal("12.54"), bc_cost=Decimal("1.32"),
            ds_nysls_cost=Decimal("1.78"), ds_nysst_rate=Decimal("0.0250"), ds_nysst_cost=Decimal("2.15"),
            ds_total_cost=Decimal("88.71"), gs_rate=Decimal("0.370998"), gs_cost=Decimal("14.48"),
            ss_nysls_cost=Decimal("0.01"), ss_nysst_rate=Decimal("0.0250"), ss_nysst_cost=Decimal("0.36"),
            ss_total_cost=Decimal("14.85"), pbc_cost=Decimal("-0.41"), oca_total_cost=Decimal("-0.41"))[0]

    @staticmethod
    def natgas_bill_data_7_est():
        return NatGasBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), service_provider=ServiceProviderTests.service_provider_ng(),
            start_date=datetime.date(2023, 3, 31), end_date=datetime.date(2023, 4, 30), paid_date=None,
            total_cost=Decimal("103.13"), tax_rel_cost=Decimal(0), is_actual=False, total_therms=39, saved_therms=0,
            bsc_therms=Decimal("3.1"), bsc_cost=Decimal("22.38"), next_therms=Decimal("35.9"),
            next_rate=Decimal("1.3521"), next_cost=Decimal("48.54"), dra_rate=Decimal("0.320998"),
            dra_cost=Decimal("12.52"), bc_cost=Decimal("1.32"), ds_nysls_rate=Decimal("0.020996"),
            ds_nysls_cost=Decimal("1.78"), ds_nysst_rate=Decimal("0.0250"), ds_nysst_cost=Decimal("2.16"),
            ds_total_cost=Decimal("88.70"), gs_rate=Decimal("0.370998"), gs_cost=Decimal("14.47"),
            ss_nysls_cost=Decimal("0.01"), ss_nysst_rate=Decimal("0.0250"), ss_nysst_cost=Decimal("0.36"),
            ss_total_cost=Decimal("14.84"), pbc_cost=Decimal("-0.41"), oca_total_cost=Decimal("-0.41"))[0]
