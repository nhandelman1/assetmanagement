from decimal import Decimal
import datetime

from ...models.mysunpowerhourlydata import MySunpowerHourlyData
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class MySunpowerHourlyDataTests(DjangoModelTestCaseBase):

    def equal(self, model1: MySunpowerHourlyData, model2: MySunpowerHourlyData):
        self.simple_equal(model1, model2, MySunpowerHourlyData)

    def test_process_sunpower_hourly_file_fail(self):
        with self.assertRaises(ValueError):
            MySunpowerHourlyData.process_sunpower_hourly_file("testsunpowerhourlydatafail.xlsx")

    def test_calculate_total_kwh_between_dates(self):
        MySunpowerHourlyData.process_save_sunpower_hourly_file("testsunpowerhourlydata.xlsx")
        kwh_dict = MySunpowerHourlyData.calculate_total_kwh_between_dates(
            datetime.date(2022, 8, 16), datetime.date(2022, 9, 15))
        self.assertEqual(kwh_dict["solar_kwh"], Decimal("1035.35"))
        self.assertEqual(kwh_dict["home_kwh"], Decimal("559.42"))
