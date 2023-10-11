from decimal import Decimal
from typing import Union
import datetime

from django.conf import settings
from django.db import models
from import_export import resources
from tablib import Dataset
import pandas as pd


class MySunpowerHourlyData(models.Model):
    """ sunpower hourly data

    Attributes:
        dt (datetime.datetime): data for this hour
        solar_kwh (Decimal): solar kwh generation in this hour
        home_kwh (Decimal): home kwh usage in this hour
    """
    class Meta:
        ordering = ["dt"]

    dt = models.DateTimeField(unique=True)
    solar_kwh = models.DecimalField(max_digits=5, decimal_places=2)
    home_kwh = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return str(self.dt) + ", Solar KWH: " + str(self.solar_kwh) + ", Home KWH: " + str(self.home_kwh)

    @classmethod
    def calculate_total_kwh_between_dates(cls, start_date, end_date):
        """ Calculate total kwh generation and usage over period that must have all requested hourly data available

        Args:
            start_date (datetime.date): calculate total starting on this date (inclusive)
            end_date (datetime.date): calculate total  ending on this date (inclusive)

        Returns:
            dict: {solar_kwh: total solar kwh generated Decimal, home_kwh: total home kwh usage Decimal}

        Raises:
            ValueError: see self.read_sunpower_hourly_data_from_db_between_dates()
        """
        data_qs = cls.read_sunpower_hourly_data_from_db_between_dates(start_date, end_date, must_have_all_data=True)
        return data_qs.aggregate(solar_kwh=models.Sum("solar_kwh"), home_kwh=models.Sum("home_kwh"))

    @classmethod
    def process_save_sunpower_hourly_file(cls, file):
        """ Open, process and save mySunpower hourly file

        see process_sunpower_hourly_file(). Args and Raises are the same but this function does has no return.
        """
        dataset = Dataset().load(cls.process_sunpower_hourly_file(file))
        mshd_resource = MySunpowerHourlyDataResource()
        result = mshd_resource.import_data(dataset, dry_run=True, raise_errors=True)
        if not result.has_errors():
            mshd_resource.import_data(dataset)

    @classmethod
    def process_sunpower_hourly_file(cls, file):
        """ Open, process and return mySunpower hourly file

        Args:
            file (Union[str, django.core.files.base.File]): name of file in media directory /files/input/solar/ or a
                File object.

        Returns:
            pd.DataFrame: with columns dt (datetime64), solar_kwh (float64) and home_kwh (float64)

        Raises:
            ValueError: if a date does not have 24 entries (1 per hour)
        """
        if isinstance(file, str):
            filename = file
            file = settings.MEDIA_ROOT + "/files/input/solar/" + file
        else:
            filename = file.name

        df = pd.read_excel(file)
        df = df.rename(columns={"Period": "dt", "Solar Production (kWh)": "solar_kwh", "Home Usage (kWh)": "home_kwh"})
        df["dt"] = df["dt"].str.split(" ").map(lambda x: x[1] + " " + x[3])
        df["dt"] = pd.to_datetime(df["dt"], format="%m/%d/%Y %I:%M%p")
        df["date"] = df["dt"].dt.date

        v_df = df.groupby(by=["date"], as_index=False).agg({"dt": "count"})
        v_df = v_df[v_df["dt"] != 24]
        if len(v_df) > 0:
            msg = "mySunpower file '" + filename + "' has issues: "
            for ind, row in v_df.iterrows():
                msg += str(row["date"]) + " has " + str(row["dt"]) + " entries "
            raise ValueError(msg)

        return df[["dt", "solar_kwh", "home_kwh"]]

    @classmethod
    def read_sunpower_hourly_data_from_db_between_dates(cls, start_date, end_date, must_have_all_data=False):
        """ Read sunpower hourly data from mysunpower_hourly_data table

        This function checks that there is no missing data between the dates.

        Args:
            start_date (datetime.date): read data starting on this date (inclusive)
            end_date (datetime.date): read data ending on this date (inclusive)
            must_have_all_data (boolean): True for this function to check that there is no missing data between the
                dates. Default False for no checks

        Returns:
            models.QuerySet: of hourly data with keys matching table columns

        Raises:
            ValueError: if any hourly data is missing and must_have_all_data is True
        """
        end_date = datetime.datetime.combine(end_date, datetime.time(23, 59, 59))
        data_qs = MySunpowerHourlyData.objects.filter(dt__gte=start_date, dt__lte=end_date)

        if must_have_all_data:
            end_date = end_date.date()
            days = (end_date - start_date).days + 1
            exp_records = days * 24
            act_records = len(data_qs)

            if exp_records != act_records:
                raise ValueError(
                    "Missing hourly data: " + str(start_date) + " - " + str(end_date) + " has " + str(days)
                    + " days and should have " + str(exp_records) + " hourly records but only has "
                    + str(act_records) + " records.")

        return data_qs


class MySunpowerHourlyDataResource(resources.ModelResource):

    class Meta:
        model = MySunpowerHourlyData
        import_id_fields = ["id", "dt"]
        skip_unchanged = True
        use_bulk = True