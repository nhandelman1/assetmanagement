import datetime
from io import BytesIO
import os

from django.core.files.base import File
from django.core.files.storage import FileSystemStorage
import django_pandas.io
import pandas as pd

from ..models.electricbilldata import ElectricBillData
from ..models.natgasbilldata import NatGasBillData
from ..models.realestate import RealEstate
import util.excelutil as excelutil


class UtilitySavingsReport:
    """ Calculate utility savings and generate an excel report

    This applies to savings due to using solar but if other savings arise they will be added.

    Class Attributes:
        OUTPUT_DIRECTORY (str): media directory /files/output/utilitysavings/

    Attributes:
        real_estate (RealEstate): calculate utility savings for this real estate
        final_df (pd.DataFrame): dataframe holding final utility savings report
        output_file_name (str): name of excel file in OUTPUT_DIRECTORY
    """
    OUTPUT_DIRECTORY = "files/output/utilitysavings/"

    def __init__(self):
        self.real_estate = None
        self.final_df = pd.DataFrame()
        self.output_file_name = None

    def calc_savings(self):
        """ Run process to calculate savings across all utilities

        Initially, this is just for PSEG, NG and Solar but could be expanded to more utilities in the future
        self.final_df holds the final output dataframe with savings by month_year, total and ROI (return on investment)

        Raises:
            ValueError: if no estimated electric or natural gas bills are found
        """
        bill_qs = ElectricBillData.objects.filter(real_estate=self.real_estate)
        pseg_df = django_pandas.io.read_frame(bill_qs)
        pseg_df = pseg_df[["start_date", "end_date", "is_actual", "total_kwh", "eh_kwh", "total_cost"]]
        pseg_df = pseg_df[pseg_df["is_actual"] == True].merge(pseg_df[pseg_df["is_actual"] == False],
                                      on=["start_date", "end_date"], how="left", suffixes=["_act", "_est"])
        pseg_df = pseg_df[~pseg_df["is_actual_est"].isnull()]
        if len(pseg_df) == 0:
            raise ValueError("Unable to generate utility savings report for " + str(self.real_estate) +
                             ". No estimated electric bills found.")
        pseg_df = pseg_df.drop(columns=["is_actual_act", "eh_kwh_act", "is_actual_est"])
        pseg_df["savings"] = pseg_df["total_cost_est"] - pseg_df["total_cost_act"]
        # there may be "savings" due to estimated total cost calculation inaccuracies, but true savings only
        # occur if total_kwh is different for act and est
        pseg_df = pseg_df[pseg_df["total_kwh_act"] != pseg_df["total_kwh_est"]]
        pseg_df = pseg_df.astype({x: "float64" for x in pseg_df.columns if x not in ["start_date", "end_date"]})
        pseg_df.columns = pd.MultiIndex.from_product([["PSEG"], pseg_df.columns])
        pseg_df["month_year"] = pseg_df.apply(
            lambda row: ElectricBillData.calc_bill_month_year(row[("PSEG", "start_date")], row[("PSEG", "end_date")]),
            axis=1)

        bill_qs = NatGasBillData.objects.filter(real_estate=self.real_estate)
        ng_df = django_pandas.io.read_frame(bill_qs)
        ng_df = ng_df[["start_date", "end_date", "is_actual", "total_therms", "saved_therms", "total_cost"]]
        ng_df = ng_df[ng_df["is_actual"] == True].merge(ng_df[ng_df["is_actual"] == False],
                                      on=["start_date", "end_date"], how="left", suffixes=["_act", "_est"])
        ng_df = ng_df[~ng_df["is_actual_est"].isnull()]
        if len(ng_df) == 0:
            raise ValueError("Unable to generate utility savings report for " + str(self.real_estate) +
                             ". No estimated natural gas bills found.")
        ng_df = ng_df.drop(columns=["is_actual_act", "saved_therms_act", "is_actual_est"])
        ng_df["savings"] = ng_df["total_cost_est"] - ng_df["total_cost_act"]
        # there may be "savings" due to estimated total cost calculation inaccuracies, but true savings only
        # occur if total_kwh is different for act and est
        ng_df = ng_df[ng_df["total_therms_act"] != ng_df["total_therms_est"]]
        ng_df = ng_df.astype({x: "float64" for x in ng_df.columns if x not in ["start_date", "end_date"]})
        ng_df.columns = pd.MultiIndex.from_product([["NG"], ng_df.columns])
        ng_df["month_year"] = ng_df.apply(
            lambda row: NatGasBillData.calc_bill_month_year(row[("NG", "start_date")], row[("NG", "end_date")]), axis=1)

        f_df = pseg_df.merge(ng_df, on=["month_year"], how="outer")
        f_df = f_df.sort_values(by=[("month_year", "")]).reset_index(drop=True)
        f_df[("Total", "savings")] = f_df[("PSEG", "savings")].fillna(0) + f_df[("NG", "savings")].fillna(0)
        f_df.insert(0, "month_year", f_df.pop("month_year"))

        flds = [("PSEG", "savings"), ("NG", "savings"), ("Total", "savings")]
        f_df.loc["Total", flds] = f_df[flds].sum()
        # TODO dont hardcode the initial cost after tax credits (17402)
        f_df.loc["ROI", ("month_year", "")] = 17402
        f_df.loc["ROI", flds] = (f_df.loc["Total", flds] / 17402 * 100).astype("float64").round(2)

        self.final_df = f_df

    def to_excel(self):
        """ Write self.final_df to excel file saved in media directory self.OUTPUT_DIRECTORY

        Output file name has format:
            "Utility Savings for (short name of real estate address) as of (datetime now).xlsx"
        self.output_file_name is set in this function

        Returns:
            str: full path to output file
        """
        # write to temp excel file
        temp_file = excelutil.clean_file_name("temp_utility_savings_" + str(datetime.datetime.now()) + ".xlsx")
        writer = pd.ExcelWriter(temp_file, engine="openpyxl")
        self.final_df.to_excel(writer)
        ws = writer.book["Sheet1"]
        excelutil.CellStyle(ws, num_fmt=excelutil.NumFmt.COMMA_0).cols([5, 7, 8, 13, 14, 15]).apply()
        excelutil.CellStyle(ws, num_fmt=excelutil.NumFmt.COMMA_2).cols([6, 9, 10, 14, 17, 18, 19]).apply()
        excelutil.sheet_adj_col_width(ws, right_count=2, comma_fmt=True, neg_fmt="-")

        # stream temp excel file to save to media directory using FileSystemStorage
        re_name = self.real_estate.Address.short_name(self.real_estate.address)
        self.output_file_name = excelutil.clean_file_name(
            "Utility Savings for " + re_name + "  as of " + str(datetime.datetime.now()) + ".xlsx")

        output_file_path = self.OUTPUT_DIRECTORY + self.output_file_name
        file_stream = BytesIO()
        writer.book.save(file_stream)
        FileSystemStorage().save(output_file_path, File(file_stream, name=output_file_path))
        writer.close()

        # delete the temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return output_file_path

    def do_process(self, real_estate, write_to_file=True):
        """ Run process to calculate savings and create report

        Calculate savings: see self.calc_savings()
        Create report: see self.to_excel()

        Args:
            real_estate (RealEstate): generate report for this real estate
            write_to_file (boolean): True to write report to excel file. False to not write report. Default True

        Returns:
            Union[str, None]: full path to output file if write_to_file. None if not write_to_file

        Raises:
            see self.calc_savings() docstring
        """
        self.real_estate = real_estate
        self.calc_savings()
        return self.to_excel() if write_to_file else None
