import datetime

from django.test import TestCase
import pandas as pd

from ...reports.billreport import BillReport
from ..models.test_realestate import RealEstateTests
from ..models.test_depreciationbilldata import DepreciationBillDataTests
from ..models.test_electricbilldata import ElectricBillDataTests
from ..models.test_mortgagebilldata import MortgageBillDataTests
from ..models.test_natgasbilldata import NatGasBillDataTests
from ..models.test_simplebilldata import SimpleBillDataTests
from ..models.test_solarbilldata import SolarBillDataTests


class BillReportTests(TestCase):

    def no_data_detail_df_test(self, type_df, cols):
        test_df = pd.DataFrame(
            data=[], columns=cols + ["Paid Date", "Start Date", "End Date", "Total Cost", "Tax Rel Cost", "Notes"])\
            .astype({"Total Cost": "float64", "Tax Rel Cost": "float64"})
        pd.testing.assert_frame_equal(self.BILL_REPORT_EMPTY.final_df_dict[type_df][0], test_df)

    def no_data_totals_df_test(self, ind, type_df):
        test_df = pd.DataFrame(data=[["Total", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], index=["Total"],
                               columns=[type_df + " Totals", "Total Income", "Total Expense", "Total Cost",
                                        "Tax Rel Income", "Tax Rel Expense", "Tax Rel Cost"])
        pd.testing.assert_frame_equal(self.BILL_REPORT_EMPTY.final_df_dict["Totals"][ind], test_df)

    def test_paid_month_detail_dfs(self):
        with self.subTest():
            self.no_data_detail_df_test("By Paid Month", ["Month", "Tax Category", "Provider"])

        test_df = pd.DataFrame(data=[
            ["February", "Utilities", "YoutubeTV-UTI", datetime.date(2022, 2, 23), datetime.date(2022, 2, 1),
             datetime.date(2022, 2, 28), 32.5, 32.5, None],
            ["June", "MortgageInterest", "MorganStanley-MI", datetime.date(2022, 6, 1), datetime.date(2022, 5, 1),
             datetime.date(2022, 5, 31), 1376.12, 0.0, " statement date is 2022-05-02"],
            ["August", "None", "10WagonLnSunpower", datetime.date(2022, 8, 15), datetime.date(2022, 7, 16),
             datetime.date(2022, 8, 15), 3441.15, 0.0, "basis starts at cost of solar system"],
            ["", "Utilities", "PSEG-UTI", datetime.date(2022, 8, 16), datetime.date(2022, 5, 17),
             datetime.date(2022, 6, 14), 91.47, 91.47, None],
            ["December", "Depreciation", "Depreciation-DEP", datetime.date(2022, 12, 31), datetime.date(2022, 1, 1),
             datetime.date(2022, 12, 31), 3072.0, 3072.0, "Max depreciation possible for full period: 3072."],
            ["", "Utilities", "NationalGrid-UTI", datetime.date(2022, 12, 31), datetime.date(2022, 12, 1),
             datetime.date(2022, 12, 29), 213.68, 0.0, None]],
            columns=["Month", "Tax Category", "Provider", "Paid Date", "Start Date", "End Date", "Total Cost",
                     "Tax Rel Cost", "Notes"]).astype({"Total Cost": "float64", "Tax Rel Cost": "float64"})

        with self.subTest():
            pd.testing.assert_frame_equal(self.BILL_REPORT.final_df_dict["By Paid Month"][0], test_df)

    def test_paid_month_total_dfs(self):
        with self.subTest():
            self.no_data_totals_df_test(1, "Month")

        test_df = pd.DataFrame(data=[
            ["February", 0.0, 32.5, 32.5, 0.0, 32.5, 32.5],
            ["June", 0.0, 1376.12, 1376.12, 0.0, 0.0, 0.0],
            ["August", 0.0, 3532.62, 3532.62, 0.0, 91.47, 91.47],
            ["December", 0.0, 3285.68, 3285.68, 0.0, 3072.0, 3072.0],
            ["Total", 0.0, 8226.92, 8226.92, 0.0, 3195.97, 3195.97]],
            index=[0, 1, 2, 3, "Total"],
            columns=["Month Totals", "Total Income", "Total Expense", "Total Cost", "Tax Rel Income",
                     "Tax Rel Expense", "Tax Rel Cost"])

        with self.subTest():
            pd.testing.assert_frame_equal(self.BILL_REPORT.final_df_dict["Totals"][1], test_df)

    def test_output_directory(self):
        self.assertEqual(BillReport.OUTPUT_DIRECTORY, "files/output/billreport/")

    def test_provider_detail_dfs(self):
        with self.subTest():
            self.no_data_detail_df_test("By Provider", ["Provider", "Tax Category"])

        test_df = pd.DataFrame(data=[
            ["10WagonLnSunpower", "None", datetime.date(2022, 8, 15), datetime.date(2022, 7, 16),
             datetime.date(2022, 8, 15), 3441.15, 0.0, "basis starts at cost of solar system"],
            ["Depreciation-DEP", "Depreciation", datetime.date(2022, 12, 31), datetime.date(2022, 1, 1),
             datetime.date(2022, 12, 31), 3072.0, 3072.0, "Max depreciation possible for full period: 3072."],
            ["MorganStanley-MI", "MortgageInterest", datetime.date(2022, 6, 1), datetime.date(2022, 5, 1),
             datetime.date(2022, 5, 31), 1376.12, 0.0, " statement date is 2022-05-02"],
            ["NationalGrid-UTI", "Utilities", datetime.date(2022, 12, 31), datetime.date(2022, 12, 1),
             datetime.date(2022, 12, 29), 213.68, 0.0, None],
            ["PSEG-UTI", "Utilities", datetime.date(2022, 8, 16), datetime.date(2022, 5, 17),
             datetime.date(2022, 6, 14), 91.47, 91.47, None],
            ["YoutubeTV-UTI", "Utilities", datetime.date(2022, 2, 23), datetime.date(2022, 2, 1),
             datetime.date(2022, 2, 28), 32.5, 32.5, None]],
            columns=["Provider", "Tax Category", "Paid Date", "Start Date", "End Date", "Total Cost",
                     "Tax Rel Cost", "Notes"]).astype({"Total Cost": "float64", "Tax Rel Cost": "float64"})

        with self.subTest():
            pd.testing.assert_frame_equal(self.BILL_REPORT.final_df_dict["By Provider"][0], test_df)

    def test_provider_total_dfs(self):
        with self.subTest():
            self.no_data_totals_df_test(2, "Provider")

        test_df = pd.DataFrame(data=[
            ["10WagonLnSunpower", 0.0, 3441.15, 3441.15, 0.0, 0.0, 0.0],
            ["Depreciation-DEP", 0.0, 3072.0, 3072.0, 0.0, 3072.0, 3072.0],
            ["MorganStanley-MI", 0.0, 1376.12, 1376.12, 0.0, 0.0, 0.0],
            ["NationalGrid-UTI", 0.0, 213.68, 213.68, 0.0, 0.0, 0.0],
            ["PSEG-UTI", 0.0, 91.47, 91.47, 0.0, 91.47, 91.47],
            ["YoutubeTV-UTI", 0.0, 32.5, 32.5, 0.0, 32.5, 32.5],
            ["Total", 0.0, 8226.92, 8226.92, 0.0, 3195.97, 3195.97]],
            index=[0, 1, 2, 3, 4, 5, "Total"],
            columns=["Provider Totals", "Total Income", "Total Expense", "Total Cost", "Tax Rel Income",
                     "Tax Rel Expense", "Tax Rel Cost"])

        with self.subTest():
            pd.testing.assert_frame_equal(self.BILL_REPORT.final_df_dict["Totals"][2], test_df)

    def test_tax_category_detail_dfs(self):
        with self.subTest():
            self.no_data_detail_df_test("By Tax Category", ["Tax Category", "Provider"])

        test_df = pd.DataFrame(data=[
            ["Depreciation", "Depreciation-DEP", datetime.date(2022, 12, 31), datetime.date(2022, 1, 1),
             datetime.date(2022, 12, 31), 3072.0, 3072.0, "Max depreciation possible for full period: 3072."],
            ["MortgageInterest", "MorganStanley-MI", datetime.date(2022, 6, 1), datetime.date(2022, 5, 1),
             datetime.date(2022, 5, 31), 1376.12, 0.0, " statement date is 2022-05-02"],
            ["None", "10WagonLnSunpower", datetime.date(2022, 8, 15), datetime.date(2022, 7, 16),
             datetime.date(2022, 8, 15), 3441.15, 0.0, "basis starts at cost of solar system"],
            ["Utilities", "NationalGrid-UTI", datetime.date(2022, 12, 31), datetime.date(2022, 12, 1),
             datetime.date(2022, 12, 29), 213.68, 0.0, None],
            ["", "PSEG-UTI", datetime.date(2022, 8, 16), datetime.date(2022, 5, 17),
             datetime.date(2022, 6, 14), 91.47, 91.47, None],
            ["", "YoutubeTV-UTI", datetime.date(2022, 2, 23), datetime.date(2022, 2, 1),
             datetime.date(2022, 2, 28), 32.5, 32.5, None]],
            columns=["Tax Category", "Provider", "Paid Date", "Start Date", "End Date", "Total Cost",
                     "Tax Rel Cost", "Notes"]).astype({"Total Cost": "float64", "Tax Rel Cost": "float64"})

        with self.subTest():
            pd.testing.assert_frame_equal(self.BILL_REPORT.final_df_dict["By Tax Category"][0], test_df)

    def test_tax_category_total_dfs(self):
        with self.subTest():
            self.no_data_totals_df_test(0, "Tax Category")

        test_df = pd.DataFrame(data=[
            ["Depreciation", 0.0, 3072.0, 3072.0, 0.0, 3072.0, 3072.0],
            ["MortgageInterest", 0.0, 1376.12, 1376.12, 0.0, 0.0, 0.0],
            ["None", 0.0, 3441.15, 3441.15, 0.0, 0.0, 0.0],
            ["Utilities", 0.0, 337.65, 337.65, 0.0, 123.97, 123.97],
            ["Total", 0.0, 8226.92, 8226.92, 0.0, 3195.97, 3195.97]],
            index=[0, 1, 2, 3, "Total"],
            columns=["Tax Category Totals", "Total Income", "Total Expense", "Total Cost", "Tax Rel Income",
                     "Tax Rel Expense", "Tax Rel Cost"])

        with self.subTest():
            pd.testing.assert_frame_equal(self.BILL_REPORT.final_df_dict["Totals"][0], test_df)

    def test_totals(self):
        def get_srs(ind, srs_type):
            srs = self.BILL_REPORT.final_df_dict["Totals"][ind].loc["Total"]
            return srs.rename(index={srs_type + " Totals": ""})

        pd.testing.assert_series_equal(get_srs(0, "Tax Category"), get_srs(1, "Month"))
        pd.testing.assert_series_equal(get_srs(1, "Month"), get_srs(2, "Provider"))

        def assert_totals_equal(ind, type_df):
            srs1 = self.BILL_REPORT.final_df_dict["Totals"][ind].loc["Total", ["Total Cost", "Tax Rel Cost"]]
            srs2 = self.BILL_REPORT.final_df_dict[type_df][0][["Total Cost", "Tax Rel Cost"]].sum()
            srs2.name = "Total"
            pd.testing.assert_series_equal(srs1.astype("float64"), srs2)

        assert_totals_equal(0, "By Tax Category")
        assert_totals_equal(1, "By Paid Month")
        assert_totals_equal(2, "By Provider")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        re_10wl = RealEstateTests.real_estate_10wl()
        year = 2022

        br = BillReport()
        br.do_process(re_10wl, year, write_to_file=False)
        cls.BILL_REPORT_EMPTY = br

        DepreciationBillDataTests.depreciation_bill_data_3()
        ElectricBillDataTests.electric_bill_data_2(paid_date=datetime.date(2022, 8, 16))
        MortgageBillDataTests.mortgage_bill_data_1(paid_date=datetime.date(2022, 6, 1))
        NatGasBillDataTests.natgas_bill_data_2(paid_date=datetime.date(2022, 12, 31))
        SimpleBillDataTests.simple_bill_data_4()
        SolarBillDataTests.solar_bill_data_1()

        br = BillReport()
        br.do_process(re_10wl, year, write_to_file=False)

        cls.BILL_REPORT = br
