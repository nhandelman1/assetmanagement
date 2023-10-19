from io import BytesIO
from typing import Union
import calendar
import datetime
import os

from django.apps import apps
from django.core.files.base import File
from django.core.files.storage import FileSystemStorage
import django_pandas.io
import numpy as np
import pandas as pd

from ..models.realestate import RealEstate
from ..models.simpleservicebilldatabase import SimpleServiceBillDataBase
import util.excelutil as excelutil


class BillReport:
    """ Create Excel report of yearly bills

    The report has 4 sheets: Totals (total_sheet()), By Tax Category (tax_category_sheet()), By Paid Month
    (paid_date_month_sheet()) and By Provider (provider_sheet()). See to_excel() docstring for output file name format
    Report includes taxable values

    Class Attributes:
        OUTPUT_DIRECTORY (str): media directory files/output/billreport/

    Attributes:
        real_estate (RealEstate): calculate bill report for this real estate
        year (int): calculate bill report for this year
        final_df_dict (dict[str, list[pd.DataFrame]]): dict of report name to list of dataframes for that report
        output_file_name (str): name of excel file in OUTPUT_DIRECTORY
    """
    OUTPUT_DIRECTORY = "files/output/billreport/"

    def __init__(self):
        self.real_estate = None
        self.year = None
        self.final_df_dict = {}
        self.output_file_name = None

    def total_sheet(self, df):
        """ Create three dataframes of totals by tax category, month and provider

        Args:
            df (pd.DataFrame): must have columns "Paid Date", "Total Cost", "Tax Rel Cost", "Tax Category", "Provider"

        Returns:
            list[pd.DataFrame]: three dataframes. first column is "Tax Category Totals", "Month Totals",
                "Provider Totals", respectively. Columns 2-7 are "Total Income", "Total Expense", "Total Cost",
                "Tax Rel Income", "Tax Rel Expense", "Tax Rel Cost". Last row is "Total" with sum of each column
        """
        df = df.copy()
        df.insert(0, "Month", pd.to_datetime(df["Paid Date"]).dt.month)
        df["Total Income"] = df["Total Cost"].mask(df["Total Cost"].gt(0), np.nan).abs()
        df["Total Expense"] = df["Total Cost"].mask(df["Total Cost"].lt(0), np.nan)
        df["Tax Rel Income"] = df["Tax Rel Cost"].mask(df["Tax Rel Cost"].gt(0), np.nan).abs()
        df["Tax Rel Expense"] = df["Tax Rel Cost"].mask(df["Tax Rel Cost"].lt(0), np.nan)

        df_list = []
        for col in ["Tax Category", "Month", "Provider"]:
            df1 = df.groupby(by=col, as_index=False).agg(
                {"Total Income": "sum", "Total Expense": "sum", "Total Cost": "sum",
                 "Tax Rel Income": "sum", "Tax Rel Expense": "sum", "Tax Rel Cost": "sum"})
            df1 = df1.astype({df1.columns[0]: object})
            df1.loc["Total"] = df1.sum()
            df1.loc["Total", col] = "Total"
            df_list.append(df1.rename(columns={col: col + " Totals"}).astype({x: "float64" for x in df1.columns[1:]}))

        df_list[1]["Month Totals"] = df_list[1]["Month Totals"].map(
            lambda x: x if x == "Total" else calendar.month_name[int(x)])

        return df_list

    def tax_category_sheet(self, df):
        """ Create dataframe of bills ordered by Tax Category, Provider and Paid Date

        Args:
            df (pd.DataFrame): must have columns "Tax Category", "Provider", "Paid Date". other columns are optional

        Returns:
            pd.DataFrame: columns are in the same order as in df. Repeated values in sequential rows in the Tax Category
                and Provider columns are replaced with ""
        """
        df = df.copy()
        df = df.sort_values(by=["Tax Category", "Provider", "Paid Date"])

        df.loc[df["Tax Category"] == df["Tax Category"].shift(1), "Tax Category"] = ""
        df.loc[df["Provider"] == df["Provider"].shift(1), "Provider"] = ""

        return df.reset_index(drop=True)

    def paid_date_month_sheet(self, df):
        """ Create dataframe of bills ordered by Month, Tax Category, Provider and Paid Date

        Args:
            df (pd.DataFrame): must have columns "Paid Date", "Tax Category", "Provider". "Month" column created in this
                function

        Returns:
            pd.DataFrame: columns are in the same order as in df with "Month" at column 0. Repeated values in sequential
                rows in the Month and Tax Category columns are replaced with ""
        """
        df = df.copy()
        df.insert(0, "Month", pd.to_datetime(df["Paid Date"]).dt.month)

        df = df.sort_values(by=["Month", "Tax Category", "Provider", "Paid Date"]).astype({"Month": object})
        df.loc[df["Month"] == df["Month"].shift(1), "Month"] = ""
        df["Month"] = df["Month"].map(lambda x: x if x == "" else calendar.month_name[int(x)])
        df.loc[df["Tax Category"] == df["Tax Category"].shift(1), "Tax Category"] = ""

        return df.reset_index(drop=True)

    def provider_sheet(self, df):
        """ Create dataframe of bills ordered by Provider and Paid Date

        Args:
            df (pd.DataFrame): must have columns "Paid Date", "Tax Category", "Provider"

        Returns:
            pd.DataFrame: columns are in the same order as in df with "Provider" moved to column 0. Repeated values in
                sequential rows in the Provider and Tax Category columns are replaced with ""
        """
        df = df.copy().sort_values(by=["Provider", "Paid Date"])
        df.insert(0, "Provider", df.pop("Provider"))
        df.loc[df["Provider"] == df["Provider"].shift(1), ["Provider", "Tax Category"]] = ["", ""]

        return df.reset_index(drop=True)

    def to_excel(self):
        """ Write data to Excel file in specified sheets

        Output file name format:
            "Yearly Bill Report for (short name of real estate address) - (year) - (datetime now).xlsx"
        self.output_file_name is set in this function

        Returns:
            str: full path to output file
        """
        # write to temp excel file
        temp_file = excelutil.clean_file_name("temp_bill_report_" + str(datetime.datetime.now()) + ".xlsx")
        writer = pd.ExcelWriter(temp_file, engine="openpyxl")
        for sheet, df_list in self.final_df_dict.items():
            row = 0
            rnd_col_set = set()
            for df in df_list:
                df.to_excel(writer, sheet_name=sheet, startrow=row, index=False)
                rnd_col_set.update([df.columns.get_loc(x) + 1 for x in df.select_dtypes(include="float64").columns])
                row += (len(df) + 2)
            ws = writer.book[sheet]
            excelutil.CellStyle(ws, num_fmt=excelutil.NumFmt.COMMA_2).cols(list(rnd_col_set)).apply()
            excelutil.sheet_adj_col_width(ws, right_count=2, comma_fmt=True, neg_fmt="-")

        re_name = self.real_estate.Address.short_name(self.real_estate.address)
        self.output_file_name = excelutil.clean_file_name(
            "Yearly Bill Report for " + re_name + " - " + str(self.year) + " - " +str(datetime.datetime.now()) +".xlsx")
        output_file_path = self.OUTPUT_DIRECTORY + self.output_file_name

        # stream temp excel file to save to media directory using FileSystemStorage
        file_stream = BytesIO()
        writer.book.save(file_stream)
        FileSystemStorage().save(output_file_path, File(file_stream, name=output_file_path))
        writer.close()

        # delete the temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return output_file_path

    def do_process(self, real_estate, year, write_to_file=True):
        """ Run process to gather data and write to Excel file

        Args:
            real_estate (RealEstate): generate report for this real estate
            year (int): generate report for this year
            write_to_file (boolean): True to write report to excel file. False to not write report. Default True

        Returns:
            Union[str, None]: full path to output file if write_to_file. None if not write_to_file
        """
        self.real_estate = real_estate
        self.year = year

        flds = ("service_provider__tax_category", "service_provider__provider", "paid_date", "start_date", "end_date",
                "total_cost", "tax_rel_cost", "notes")
        bill_df = pd.DataFrame()
        app_models = apps.get_app_config('realestate').get_models()
        for model_type in app_models:
            if issubclass(model_type, SimpleServiceBillDataBase):
                bill_qs = model_type.objects.filter(real_estate=real_estate, paid_date__gte=datetime.date(year, 1, 1),
                                                    paid_date__lte=datetime.date(year, 12, 31))
                df = django_pandas.io.read_frame(bill_qs, fieldnames=flds, verbose=False)
                bill_df = pd.concat([bill_df, df], ignore_index=True)

        bill_df = bill_df.rename(columns={col: col.replace("service_provider__", "").replace("_", " ").title()
                                          for col in bill_df.columns})
        bill_df = bill_df.astype({"Total Cost": "float64", "Tax Rel Cost": "float64"})

        tct_df, mt_df, pt_df = self.total_sheet(bill_df)
        tc_df = self.tax_category_sheet(bill_df)
        m_df = self.paid_date_month_sheet(bill_df)
        p_df = self.provider_sheet(bill_df)

        self.final_df_dict = {"Totals": [tct_df, mt_df, pt_df], "By Tax Category": [tc_df], "By Paid Month": [m_df],
                              "By Provider": [p_df]}

        return self.to_excel() if write_to_file else None
