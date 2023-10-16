from decimal import Decimal
import datetime

from ...models.mysunpowerhourlydata import MySunpowerHourlyData
from ...models.solarbilldata import SolarBillData
from .djangomodeltestcasebase import DjangoModelTestCaseBase
from .test_realestate import RealEstateTests
from .test_serviceprovider import ServiceProviderTests


class SolarBillDataTests(DjangoModelTestCaseBase):

    def equal(self, model1: SolarBillData, model2: SolarBillData):
        RealEstateTests().equal(model1.real_estate, model2.real_estate)
        ServiceProviderTests().equal(model1.service_provider, model2.service_provider)
        self.simple_equal(model1, model2, SolarBillData, rem_attr_list=["real_estate", "service_provider"])

    def test_modify(self):
        # modify but with no changes except to notes
        sbd = SolarBillDataTests.solar_bill_data_2()
        sbd_copy = sbd.modify()
        sbd.notes += " This bill is a modification of the original bill."
        sbd.clean_fields()
        self.equal(sbd, sbd_copy)

        # modify but with cost_ratio applied to attributes and real_estate changed
        sbd = SolarBillData.objects.get(pk=sbd.pk)
        sbd_copy = sbd.modify(cost_ratio=Decimal("0.5"), real_estate=RealEstateTests.real_estate_10wlapt1())
        sbd.real_estate = RealEstateTests.real_estate_10wlapt1()
        sbd.total_cost = Decimal("-1523.925")
        sbd.solar_kwh = Decimal("517.675")
        sbd.home_kwh = Decimal("279.71")
        sbd.actual_costs = Decimal(0)
        sbd.oc_bom_basis = Decimal("16857.575")
        sbd.oc_pnl = Decimal("-1523.925")
        sbd.oc_eom_basis = Decimal("15333.65")
        sbd.notes = 'test notes sbd This bill is a modification of the original bill. Ratio of 0.5 applied to total ' \
                    'cost. Real estate changed from original. Ratio of 0.5 applied to all attributes except ' \
                    'opportunity cost pnl percent.'
        self.equal(sbd, sbd_copy)

    def test_process_service_bill(self):
        sbd_test = SolarBillDataTests.solar_bill_data_2()  # do this first to create real_estate and service_provider objects
        MySunpowerHourlyData.process_save_sunpower_hourly_file("testsunpowerhourlydata.xlsx")
        sbd = SolarBillData.process_service_bill("testsolarbill2.csv")
        sbd_test.bill_file = sbd.bill_file
        self.equal(sbd, sbd_test)

    @staticmethod
    def solar_bill_data_1():
        """
        real_estate and service_provider must equal those in solar_bill_data_2() for testing. oc_eom_basis must equal
        oc_bom_basis in solar_bill_data_2() for testing. end_date must be one day before start_date in solar_bill_data_2()
        for testing.

        Returns:
            SolarBillData: created instance
        """
        bill = SolarBillData.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(),
            service_provider=ServiceProviderTests.service_provider_solar(), start_date=datetime.date(2022, 7, 16),
            end_date=datetime.date(2022, 8, 15), total_cost=Decimal("3441.15"), tax_rel_cost=Decimal(0),
            solar_kwh=Decimal("1218.86"), home_kwh=Decimal("697.09"), actual_costs=Decimal(0),
            oc_bom_basis=Decimal(30274), oc_pnl_pct=Decimal("11.37"), oc_pnl=Decimal("3441.15"),
            oc_eom_basis=Decimal("33715.15"), paid_date=datetime.date(2022, 8, 15),
            notes="basis starts at cost of solar system")[0]
        return bill

    @staticmethod
    def solar_bill_data_2():
        """
        See solar_bill_data_1()

        Returns:
            SolarBillData: created instance
        """
        prev_bill = SolarBillDataTests.solar_bill_data_1()
        real_estate = prev_bill.real_estate
        service_provider = prev_bill.service_provider
        oc_bom_basis = prev_bill.oc_eom_basis
        start_date = prev_bill.end_date + datetime.timedelta(days=1)

        oc_pnl_pct = Decimal("-9.04")
        actual_costs = Decimal(0)
        oc_pnl, total_cost, oc_eom_basis = SolarBillData.calc_attributes(oc_bom_basis, oc_pnl_pct, actual_costs)
        bill = SolarBillData.objects.get_or_create(
            real_estate=real_estate, service_provider=service_provider, start_date=start_date,
            end_date=datetime.date(2022, 9, 15), total_cost=total_cost, tax_rel_cost=Decimal(0),
            solar_kwh=Decimal("1035.35"), home_kwh=Decimal("559.42"), actual_costs=actual_costs,
            oc_bom_basis=oc_bom_basis, oc_pnl_pct=oc_pnl_pct, oc_pnl=oc_pnl, oc_eom_basis=oc_eom_basis,
            paid_date=datetime.date(2022, 9, 15), notes="test notes sbd")[0]
        return bill