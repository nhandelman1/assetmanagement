import datetime

from django.test import TestCase
import numpy as np
import pandas as pd

from ...reports.utilitysavingsreport import UtilitySavingsReport
from ..models.test_electricbilldata import ElectricBillDataTests
from ..models.test_natgasbilldata import NatGasBillDataTests
from ..models.test_realestate import RealEstateTests


class UtilitySavingsReportTests(TestCase):
    def test_output_directory(self):
        self.assertEqual(UtilitySavingsReport.OUTPUT_DIRECTORY, "files/output/utilitysavings/")

    def test_no_data(self):
        re_10wl = RealEstateTests.real_estate_10wl()
        us = UtilitySavingsReport()
        with self.assertRaises(ValueError):
            us.do_process(re_10wl, write_to_file=False)

    def test_data(self):
        re_10wl = RealEstateTests.real_estate_10wl()

        ElectricBillDataTests.electric_bill_data_4_act()
        ElectricBillDataTests.electric_bill_data_4_est()
        ElectricBillDataTests.electric_bill_data_5_act()
        ElectricBillDataTests.electric_bill_data_5_est()
        ElectricBillDataTests.electric_bill_data_6_act()
        ElectricBillDataTests.electric_bill_data_6_est()
        ElectricBillDataTests.electric_bill_data_7_act()
        ElectricBillDataTests.electric_bill_data_7_est()

        NatGasBillDataTests.natgas_bill_data_4_act()
        NatGasBillDataTests.natgas_bill_data_4_est()
        NatGasBillDataTests.natgas_bill_data_5_act()
        NatGasBillDataTests.natgas_bill_data_5_est()
        NatGasBillDataTests.natgas_bill_data_6_act()
        NatGasBillDataTests.natgas_bill_data_6_est()
        NatGasBillDataTests.natgas_bill_data_7_act()
        NatGasBillDataTests.natgas_bill_data_7_est()

        us = UtilitySavingsReport()
        us.do_process(re_10wl, write_to_file=False)

        test_df = pd.DataFrame(data=[
            ["2022-08", datetime.date(2022, 8, 16), datetime.date(2022, 9, 15), 0.0, 15.45, 559.0, 0.0, 160.67, 145.22,
             np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 145.22],
            ["2022-09", datetime.date(2022, 9, 16), datetime.date(2022, 10, 14), 0.0, 14.45, 373.0, 0.0, 107.71, 93.26,
             np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 93.26],
            ["2022-12", np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
             datetime.date(2022, 12, 1), datetime.date(2022, 12, 29), 114.0, 213.68, 119.0, 5.0, 221.66, 7.98, 7.98],
            ["2023-01", datetime.date(2023, 1, 18), datetime.date(2023, 2, 14), 107.0, 41.93, 795.0, 100.0, 188.26,
             146.33, datetime.date(2022, 12, 30), datetime.date(2023, 1, 30), 93.0, 200.44, 165.0, 72.0, 291.98, 91.54,
             237.87],
            ["2023-02", datetime.date(2023, 2, 15), datetime.date(2023, 3, 14), 136.0, 46.49, 769.0, 0.0, 172.24,
             125.75, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 125.75],
            [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 510.56, np.nan, np.nan, np.nan, np.nan,
             np.nan, np.nan, np.nan, 99.52, 610.08],
            [17402, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 2.93, np.nan, np.nan, np.nan, np.nan,
             np.nan, np.nan, np.nan, 0.57, 3.51]],
            index=[0, 1, 2, 3, 4, "Total", "ROI"],
            columns=pd.MultiIndex.from_tuples(
                [("month_year", ""), ("PSEG", "start_date"), ("PSEG", "end_date"), ("PSEG", "total_kwh_act"),
                 ("PSEG", "total_cost_act"), ("PSEG", "total_kwh_est"), ("PSEG", "eh_kwh_est"),
                 ("PSEG", "total_cost_est"), ("PSEG", "savings"), ("NG", "start_date"), ("NG", "end_date"),
                 ("NG", "total_therms_act"), ("NG", "total_cost_act"), ("NG", "total_therms_est"),
                 ("NG", "saved_therms_est"), ("NG", "total_cost_est"), ("NG", "savings"), ("Total", "savings")]))

        pd.testing.assert_frame_equal(us.final_df, test_df)