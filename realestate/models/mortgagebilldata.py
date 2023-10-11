from decimal import Decimal
from typing import Union
import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
import pandas as pd
import tabula

from .realestate import Address, RealEstate
from .serviceprovider import ServiceProvider, ServiceProviderEnum
from .simpleservicebilldatabase import SimpleServiceBillDataBase


class MortgageBillDataManager(models.Manager):

    def default_constructor(self):
        """ Instantiate (but don't create) MortgageBillData instance with None for all attributes

        Returns:
            MortgageBillData: instance
        """
        return self.full_constructor(
            None, None, None, None, None, None, None, None, None, None, None, None, create=False)

    def full_constructor(self, real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost, outs_prin,
                         esc_bal, prin_pmt, int_pmt, esc_pmt, other_pmt, paid_date=None, notes=None, bill_file=None,
                         create=True):
        """ Instantiate MortgageBillData instance with option to save to database

        Args:
            see MortgageBillData class docstring
            create (bool): False to create instance only. Default True to also save to database (self.create)

        Returns:
            MortgageBillData: instance
        """
        return (self.create if create else MortgageBillData)(
            real_estate=real_estate, service_provider=service_provider, start_date=start_date, end_date=end_date,
            total_cost=total_cost, tax_rel_cost=tax_rel_cost, outs_prin=outs_prin, esc_bal=esc_bal, prin_pmt=prin_pmt,
            int_pmt=int_pmt, esc_pmt=esc_pmt, other_pmt=other_pmt, paid_date=paid_date, notes=notes,
            bill_file=bill_file)


class MortgageBillData(SimpleServiceBillDataBase):
    """ Mortgage implementation of SimpleServiceBillDataBase

    Attributes:
        see superclass docstring
        outs_prin (Decimal): outstanding principal before principal payment is applied
        esc_bal (Decimal): escrow balance
        prin_pmt (Decimal): principal payment
        int_pmt (Decimal): interest payment
        esc_pmt (Decimal): escrow payment
        other_pmt (Decimal): other payment
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["real_estate", "service_provider", "start_date"],
                                    name="unique_%(app_label)s_%(class)s_re_sp_sd"),
        ]
        ordering = ["real_estate", "start_date"]

    # noinspection PyMethodParameters
    def file_upload_path(instance, filename):
        return "files/input/mortgage/" + filename

    # noinspection PyMethodParameters
    def validate_service_provider(service_provider):
        service_provider = ServiceProvider.objects.get(pk=service_provider)
        if service_provider.provider not in MortgageBillData.valid_providers():
            raise ValidationError(str(service_provider) + " is not a valid service provider")

    # noinspection PyMethodParameters
    def valid_service_providers():
        return {"provider__in": MortgageBillData.valid_providers()}

    service_provider = models.ForeignKey(ServiceProvider, models.PROTECT, validators=[validate_service_provider],
                                         limit_choices_to=valid_service_providers)
    bill_file = models.FileField(blank=True, null=True, upload_to=file_upload_path)
    outs_prin = models.DecimalField(max_digits=10, decimal_places=2)
    esc_bal = models.DecimalField(max_digits=8, decimal_places=2)
    prin_pmt = models.DecimalField(max_digits=7, decimal_places=2)
    int_pmt = models.DecimalField(max_digits=7, decimal_places=2)
    esc_pmt = models.DecimalField(max_digits=7, decimal_places=2)
    other_pmt = models.DecimalField(max_digits=7, decimal_places=2)

    objects = MortgageBillDataManager()

    def __repr__(self):
        """ __repr__ override

        Format:
            super().__repr__()
            Balances (before payments applied): Principal: str(self.outs_prin), Escrow: str(self.esc_bal)
            Payments: Principal: str(self.prin_pmt), Interest: str(self.int_pmt), Escrow: str(self.esc_pmt),
                Other: str(self.other_pmt)

        Returns:
            str: as described by Format
        """
        return super().__repr__() + "\nBalances (before payments applied): Principal: " + str(self.outs_prin) + \
            ", Escrow: " + str(self.esc_bal) + "\nPayments: Principal: " + str(self.prin_pmt) + ", Interest: " + \
            str(self.int_pmt) + ", Escrow: " + str(self.esc_pmt) + ", Other: " + str(self.other_pmt)

    def modify(self, cost_ratio=None, real_estate=None, **kwargs):
        """ see superclass docstring

        Ratio applied to all attributes.
        """
        bill_copy = super().modify(cost_ratio=cost_ratio, real_estate=real_estate, **kwargs)

        if cost_ratio is not None:
            bill_copy.outs_prin *= cost_ratio
            bill_copy.esc_bal *= cost_ratio
            bill_copy.prin_pmt *= cost_ratio
            bill_copy.int_pmt *= cost_ratio
            bill_copy.esc_pmt *= cost_ratio
            bill_copy.other_pmt *= cost_ratio

            bill_copy.notes += " Ratio of " + str(cost_ratio) + " applied to all attributes."

        return bill_copy

    def tax_related_cost_message(self):
        return self.tax_related_cost_message_helper("Mortgage", "interest payment cost", "0")

    @classmethod
    def process_service_bill(cls, file):
        """ Open, process and return Morgan Stanley mortgage bill

        Args:
            file (Union[str, django.core.files.base.File]): name of file in media directory /files/input/mortgage/
                or a File object.

        Returns:
            MortgageBillData: with all required fields populated and as many non required fields as available populated.
                Instance is not saved to database.
        """
        if isinstance(file, str):
            file = settings.MEDIA_ROOT + "/files/input/mortgage/" + file

        bill_data = MortgageBillData.objects.default_constructor()
        bill_data.bill_file = file

        def fmt_dec(str_val):
            return Decimal(str_val.replace("$", "").replace(" ", "").replace(",", ""))

        df_list = tabula.read_pdf(file, pages="all", guess=False, silent=True)
        df = df_list[0]
        address = ""
        found_address = False
        for ind, row in df.iterrows():
            str0 = "" if pd.isna(row.iloc[0]) else row.iloc[0]
            str1 = "" if pd.isna(row.iloc[1]) else row.iloc[1]
            str2 = "" if pd.isna(row.iloc[2]) else row.iloc[2]

            # bill start date and end date from statement date
            if any(["Statement Date:" in x for x in [str0, str1]]):
                stmt_date = datetime.datetime.strptime(str2, "%m/%d/%y").date()

                # mortgage is a monthly payment so start date is the first day of the month (even if the statement
                # date isn't the first day of the month)
                bill_data.start_date = stmt_date
                # sometimes the statement date is at the end of the previous month. make it a day in the next month
                if bill_data.start_date.day >= 25:
                    bill_data.start_date += datetime.timedelta(days=7)
                bill_data.start_date = bill_data.start_date.replace(day=1)

                # default end date to last day of month of start date
                bill_data.end_date = bill_data.start_date + datetime.timedelta(days=31)
                bill_data.end_date = bill_data.end_date.replace(day=1) - datetime.timedelta(days=1)

                bill_data.notes = ("" if bill_data.notes is None else bill_data.notes) + " statement date is " + \
                                  str(stmt_date)

            # address
            if "Property Address" in str0:
                # relevant address words are either completely numeric or upper case
                for s in str0.split(" "):
                    if s.isnumeric() or s.isupper():
                        address += (" " + s)
                found_address = True
            elif found_address:
                # 2nd part of address is in the next row
                # relevant address words are either all numeric or all upper case with punctuation
                for s in str0.split(" "):
                    if any([x.islower() for x in s]):
                        continue
                    address += (" " + s)
                found_address = False

            # "Principal" comes in other rows. don't want to overwrite prin_pmt
            if any(["Principal" in x for x in [str0, str1]]) and bill_data.prin_pmt is None:
                bill_data.prin_pmt = fmt_dec(str2)
            # "Interest" is found in later rows
            if any(["Interest" in x for x in [str0, str1]]) and bill_data.int_pmt is None:
                bill_data.int_pmt = fmt_dec(str2)
            # not sure if "Outstanding Principal" appears in later rows but assuming it does
            if "Outstanding Principal" in str0 and bill_data.outs_prin is None:
                bill_data.outs_prin = fmt_dec(str0.split(" ")[2])
            if "Escrow Balance" in str0:
                if bill_data.esc_bal is None:
                    bill_data.esc_bal = fmt_dec(str0.split(" ")[2])
            elif "Escrow" in str0 and bill_data.esc_pmt is None:
                bill_data.esc_pmt = fmt_dec(str2)
            if "Escrow" in str1 and bill_data.esc_pmt is None:
                bill_data.esc_pmt = fmt_dec(str0[:str0.find(".")+2])
            # Other pmt comes immediately after escrow payment
            if any(["Other" in x for x in [str0, str1]]) and bill_data.esc_pmt is not None and \
                    bill_data.other_pmt is None:
                bill_data.other_pmt = fmt_dec(str2)
            if "Current Payment Due" in str0:
                bill_data.total_cost = fmt_dec(str1)
            elif "Current Payment Due" in str1:
                bill_data.total_cost = fmt_dec(str0[:str0.find(".") + 3])

        bill_data.real_estate = RealEstate.objects.filter(address=Address.to_address(address.strip())).get()
        bill_data.service_provider = ServiceProvider.objects.filter(provider=ServiceProviderEnum.MS_MI).get()

        return bill_data

    @classmethod
    def set_default_tax_related_cost(cls, bill_tax_related_cost_list):
        bill_list = []
        for bill, tax_related_cost in bill_tax_related_cost_list:
            if tax_related_cost.is_nan():
                bill.tax_rel_cost = bill.int_pmt if bill.real_estate.bill_tax_related else Decimal(0)
            else:
                bill.tax_rel_cost = tax_related_cost
            bill_list.append(bill)
        return bill_list

    @classmethod
    def valid_providers(cls):
        """ Which service providers are valid for this model

        Returns:
            list[ServiceProviderEnum]: [ServiceProviderEnum.MS_MI]
        """
        return [ServiceProviderEnum.MS_MI]