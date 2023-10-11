from decimal import Decimal
from typing import Optional, Union
import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
import pandas as pd
import tabula

from .complexservicebilldatabase import ComplexServiceBillDataBase
from .natgasdata import NatGasData
from .realestate import Address, RealEstate
from .serviceprovider import ServiceProvider, ServiceProviderEnum


class NatGasBillDataManager(models.Manager):

    def default_constructor(self):
        """ Instantiate (but don't create) NatGasBillData instance with None for all attributes

        Returns:
            NatGasBillData: instance
        """
        return self.full_constructor(
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
            None, create=False)

    def full_constructor(self, real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost, is_actual,
                         total_therms, saved_therms, bsc_therms, bsc_cost, next_therms, next_rate, next_cost,
                         ds_total_cost, gs_rate, gs_cost, ss_total_cost, oca_total_cost, over_therms=None,
                         over_rate=None, over_cost=None, dra_rate=None, dra_cost=None, sbc_rate=None, sbc_cost=None,
                         tac_rate=None, tac_cost=None, bc_cost=None, ds_nysls_rate=None, ds_nysls_cost=None,
                         ds_nysst_rate=None, ds_nysst_cost=None, ss_nysls_rate=None, ss_nysls_cost=None,
                         ss_nysst_rate=None, ss_nysst_cost=None, pbc_cost=None, paid_date=None, notes=None,
                         bill_file=None, create=True):
        """ Instantiate NatGasBillData instance with option to save to database

        Args:
            see NatGasBillData class docstring
            create (bool): False to create instance only. Default True to also save to database (self.create)

        Returns:
            NatGasBillData: instance
        """
        return (self.create if create else NatGasBillData)(
            real_estate=real_estate, service_provider=service_provider, start_date=start_date, end_date=end_date,
            total_cost=total_cost, tax_rel_cost=tax_rel_cost, is_actual=is_actual, total_therms=total_therms,
            saved_therms=saved_therms, bsc_therms=bsc_therms, bsc_cost=bsc_cost, next_therms=next_therms,
            next_rate=next_rate, next_cost=next_cost, ds_total_cost=ds_total_cost, gs_rate=gs_rate, gs_cost=gs_cost,
            ss_total_cost=ss_total_cost, oca_total_cost=oca_total_cost, over_therms=over_therms, over_rate=over_rate,
            over_cost=over_cost, dra_rate=dra_rate, dra_cost=dra_cost, sbc_rate=sbc_rate, sbc_cost=sbc_cost,
            tac_rate=tac_rate, tac_cost=tac_cost, bc_cost=bc_cost, ds_nysls_rate=ds_nysls_rate,
            ds_nysls_cost=ds_nysls_cost, ds_nysst_rate=ds_nysst_rate, ds_nysst_cost=ds_nysst_cost,
            ss_nysls_rate=ss_nysls_rate, ss_nysls_cost=ss_nysls_cost, ss_nysst_rate=ss_nysst_rate,
            ss_nysst_cost=ss_nysst_cost, pbc_cost=pbc_cost, paid_date=paid_date, notes=notes, bill_file=bill_file)


class NatGasBillData(ComplexServiceBillDataBase):
    """ Actual or estimated data provided on monthly natural gas bill or relevant to monthly bill

    Attributes:
        see super class docstring
        total_therms (int): nonnegative total therms used from provider
        saved_therms (int): nonnegative therms saved by using non nat gas sources (probably electric)
        bsc_therms (Decimal): therms used at basic service charge cost
        bsc_cost (Decimal): basic service charge cost
        next_therms (Decimal): therms used at next rate
            In the bill, either by "Next Therms" or "Over/Last Therms" (if "Next Therms" is not in the bill)
        next_rate (Decimal): next rate
            In the bill, either by "Next Therms" or "Over/Last Therms" (if "Next Therms" is not in the bill)
        next_cost (Decimal): next cost
            In the bill, either by "Next Therms" or "Over/Last Therms" (if "Next Therms" is not in the bill)
        ds_total_cost (Decimal): delivery service total cost
        gs_rate (Decimal): gas supply rate
        gs_cost (Decimal): gas supply cost
        ss_total_cost (Decimal): supply service total cost
        oca_total_cost (Decimal): other charges/adjustments total cost
        over_therms (Optional[Decimal]): therms used at over/last rate.
            If "Next Therms" is in the bill, by "Over/Last Therms", otherwise not used. Default None
        over_rate (Optional[Decimal]): over/last rate.
            If "Next Therms" is in the bill, by "Over/Last Therms", otherwise not used. Default None
        over_cost (Optional[Decimal]): over/last cost.
            If "Next Therms" is in the bill, by "Over/Last Therms", otherwise not used. Default None
        dra_rate (Optional[Decimal]): delivery rate adjustment rate. Default None
        dra_cost (Optional[Decimal]): delivery rate adjustment cost. Default None
        sbc_rate (Optional[Decimal]): system benefits charge rate. Default None
        sbc_cost (Optional[Decimal]): system benefits charge cost. Default None
        tac_rate (Optional[Decimal]): transportation adjustment charge rate. Default None
        tac_cost (Optional[Decimal]): transportation adjustment charge cost. Default None
        bc_cost (Optional[Decimal]): billing charge cost. Default None
        ds_nysls_rate (Optional[Decimal]): delivery services ny state and local surcharges rate. Default None
        ds_nysls_cost (Optional[Decimal]): delivery services ny state and local surcharges cost. Default None
        ds_nysst_rate (Optional[Decimal]): delivery services ny state sales tax rate. Default None
        ds_nysst_cost (Optional[Decimal]): delivery services ny state sales tax cost. Default None
        ss_nysls_rate (Optional[Decimal]): supply services ny state and local surcharges rate. Default None
        ss_nysls_cost (Optional[Decimal]): supply services ny state and local surcharges cost. Default None
        ss_nysst_rate (Optional[Decimal]): supply services ny state sales tax rate. Default None
        ss_nysst_cost (Optional[Decimal]): supply services ny state sales tax cost. Default None
        pbc_cost (Optional[Decimal]): paperless billing credit cost. Default None
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["real_estate", "start_date", "is_actual"],
                                    name="unique_%(app_label)s_%(class)s_re_sd_ia"),
            models.UniqueConstraint(fields=["real_estate", "end_date", "is_actual"],
                                    name="unique_%(app_label)s_%(class)s_re_ed_ia")
        ]
        ordering = ["real_estate", "start_date", "-is_actual"]

    # noinspection PyMethodParameters
    def file_upload_path(instance, filename):
        return "files/input/natgas/" + filename

    # noinspection PyMethodParameters
    def validate_service_provider(service_provider):
        service_provider = ServiceProvider.objects.get(pk=service_provider)
        if service_provider.provider not in NatGasBillData.valid_providers():
            raise ValidationError(str(service_provider) + " is not a valid service provider")

    # noinspection PyMethodParameters
    def valid_service_providers():
        return {"provider__in": NatGasBillData.valid_providers()}

    service_provider = models.ForeignKey(ServiceProvider, models.PROTECT, validators=[validate_service_provider],
                                         limit_choices_to=valid_service_providers)
    bill_file = models.FileField(blank=True, null=True, upload_to=file_upload_path)
    total_therms = models.PositiveSmallIntegerField()
    saved_therms = models.PositiveSmallIntegerField()
    bsc_therms = models.DecimalField(max_digits=3, decimal_places=1)
    bsc_cost = models.DecimalField(max_digits=5, decimal_places=2)
    next_therms = models.DecimalField(max_digits=4, decimal_places=1)
    next_rate = models.DecimalField(max_digits=5, decimal_places=4)
    next_cost = models.DecimalField(max_digits=5, decimal_places=2)
    over_therms = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    over_rate = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    over_cost = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    dra_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    dra_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    sbc_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    sbc_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    tac_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    tac_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    bc_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    ds_nysls_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    ds_nysls_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    ds_nysst_rate = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    ds_nysst_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    ds_total_cost = models.DecimalField(max_digits=6, decimal_places=2)
    gs_rate = models.DecimalField(max_digits=7, decimal_places=6)
    gs_cost = models.DecimalField(max_digits=6, decimal_places=2)
    ss_nysls_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    ss_nysls_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    ss_nysst_rate = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    ss_nysst_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    ss_total_cost = models.DecimalField(max_digits=6, decimal_places=2)
    pbc_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    oca_total_cost = models.DecimalField(max_digits=5, decimal_places=2)

    objects = NatGasBillDataManager()

    def __repr__(self):
        """ __repr__ override

        Format:
            super().__repr__()
            Total Therms: self.total_therms, Saved Therms: self.saved_therms, Bank KWH: self.bank_kwh
            Delivery Services: Total Cost: self.ds_total_cost
              Basic: Therms: self.bsc_therms, Cost: self.bsc_cost
              Next: Therms: self.next_therms, Rate: self.next_rate/therm, Cost: self.next_cost
              Over: Therms: self.over_therms, Rate: self.over_rate/therm, Cost: self.over_cost
              Delivery Rate Adjustment: Rate: self.dra_rate/therm, Cost: self.dra_cost
              System Benefits Charge: Rate: self.sbc_rate/therm, Cost: self.sbc_cost
              Transportation Adjustment Charge: Rate: self.tac_rate/therm, Cost: self.tac_cost
              Billing Charge: Cost: self.bc_cost
              NY State and Local Surcharges: Rate: self.ds_nysls_rate, Cost: self.ds_nysls_cost
              NY State Sales Tax: Rate: self.ds_nysst_rate, Cost: self.ds_nysst_cost
            Supply Services: Total Cost: self.ss_total_cost
              Gas Supply: Rate: self.gs_rate/therm, Cost: self.gs_cost
              NY State and Local Surcharges: Rate: self.ss_nysls_rate, Cost: self.ss_nysls_cost
              NY State Sales Tax: Rate: self.ss_nysst_rate, Cost: self.ss_nysst_cost
            Other Charges/Adjustments: Total Cost: self.oca_total_cost
                Paperless Billing Credit: Cost: self.pbc_cost

        Returns:
            str: as described by Format
        """
        return super().__repr__() + \
            "\nTotal Therms: " + str(self.total_therms) + ", Saved Therms: " + str(self.saved_therms) + \
            "\nDelivery Services: Total Cost: " + str(self.ds_total_cost) + \
            "\n  Basic: Therms: " + str(self.bsc_therms) + ", Cost: " + str(self.bsc_cost) + \
            "\n  Next: Therms: " + str(self.next_therms) + ", Rate: " + str(self.next_rate) + "/therm, Cost: " + \
                str(self.next_cost) + \
            "\n  Over: Therms: " + str(self.over_therms) + ", Rate: " + str(self.over_rate) + "/therm, Cost: " + \
                str(self.over_cost) + \
            "\n  Delivery Rate Adjustment: Rate: " + str(self.dra_rate) + "/therm, Cost: " + str(self.dra_cost) + \
            "\n  System Benefits Charge: Rate: " + str(self.sbc_rate) + "/kwh, Cost: " + str(self.sbc_cost) + \
            "\n  Transportation Adjustment Charge: Rate: " + str(self.tac_rate) + "/therm, Cost: "+str(self.tac_cost)+\
            "\n  Billing Charge: Cost: " + str(self.bc_cost) + \
            "\n  NY State and Local Surcharges: Rate: " + str(self.ds_nysls_rate) + ", Cost: "+str(self.ds_nysls_cost)+\
            "\n  NY State Sales Tax: Rate: " + str(self.ds_nysst_rate) + ", Cost: " + str(self.ds_nysst_cost) + \
            "\nSupply Services: Total Cost: " + str(self.ss_total_cost) + \
            "\n  Gas Supply: Rate: " + str(self.gs_rate) + "/therm, Cost: " + str(self.gs_cost) + \
            "\n  NY State and Local Surcharges: Rate: " + str(self.ss_nysls_rate) + ", Cost: "+str(self.ss_nysls_cost)+\
            "\n  NY State Sales Tax: Rate: " + str(self.ss_nysst_rate) + ", Cost: " + str(self.ss_nysst_cost) + \
            "\nOther Charges/Adjustments: Total Cost: " + str(self.oca_total_cost) + \
            "\n  Paperless Billing Credit: Cost: " + str(self.pbc_cost)

    def modify(self, cost_ratio=None, real_estate=None, **kwargs):
        """ see superclass docstring

        Ratio applied to therms and cost attributes.
        """
        bill_copy = super().modify(cost_ratio=cost_ratio, real_estate=real_estate, **kwargs)

        if cost_ratio is not None:
            def dec_mult_none(left):
                return None if left is None else left * cost_ratio

            def int_mult_none(left):
                return None if left is None else int(left * cost_ratio)

            bill_copy.total_therms = int_mult_none(bill_copy.total_therms)
            bill_copy.saved_therms = int_mult_none(bill_copy.saved_therms)
            bill_copy.bsc_therms *= cost_ratio
            bill_copy.bsc_cost *= cost_ratio
            bill_copy.next_therms *= cost_ratio
            bill_copy.next_cost *= cost_ratio
            bill_copy.over_therms = dec_mult_none(bill_copy.over_therms)
            bill_copy.over_cost = dec_mult_none(bill_copy.over_cost)
            bill_copy.dra_cost = dec_mult_none(bill_copy.dra_cost)
            bill_copy.sbc_cost = dec_mult_none(bill_copy.sbc_cost)
            bill_copy.tac_cost = dec_mult_none(bill_copy.tac_cost)
            bill_copy.bc_cost = dec_mult_none(bill_copy.bc_cost)
            bill_copy.ds_nysls_cost = dec_mult_none(bill_copy.ds_nysls_cost)
            bill_copy.ds_nysst_cost = dec_mult_none(bill_copy.ds_nysst_cost)
            bill_copy.ds_total_cost *= cost_ratio
            bill_copy.gs_cost *= cost_ratio
            bill_copy.ss_nysls_cost = dec_mult_none(bill_copy.ss_nysls_cost)
            bill_copy.ss_nysst_cost = dec_mult_none(bill_copy.ss_nysst_cost)
            bill_copy.ss_total_cost *= cost_ratio
            bill_copy.pbc_cost = dec_mult_none(bill_copy.pbc_cost)
            bill_copy.oca_total_cost *= cost_ratio

            bill_copy.notes += " Ratio of " + str(cost_ratio) + " applied to therms and cost attributes."

        return bill_copy

    def tax_related_cost_message(self):
        return self.tax_related_cost_message_helper("Natural Gas", "total cost", "0")

    @classmethod
    def estimate_ds(cls, emb, ngd_start, ngd_end, amb):
        """ Estimate delivery services charges

        Args:
            emb (NatGasBillData): estimate natural gas bill data
            ngd_start (NatGasData): for the earlier month
            ngd_end (NatGasData): for the later month
            amb (NatGasBillData): actual natural gas bill data

        Returns:
            NatGasBillData: emb with delivery services charges estimated
        """
        def sum_none(*nums):
            return sum(filter(None, nums))

        e_rat = Decimal(emb.end_date.day / ((emb.end_date - emb.start_date).days + 1))
        s_rat = 1 - e_rat

        emb.next_therms = min(emb.total_therms - emb.bsc_therms,
                              ngd_start.next_therms * s_rat + ngd_end.next_therms * e_rat)
        emb.next_cost = emb.next_therms * emb.next_rate
        emb.over_therms = emb.total_therms - emb.bsc_therms - emb.next_therms
        # over rate may not be in the bill
        emb.over_rate = ngd_start.over_rate * s_rat + ngd_end.over_rate * e_rat if amb.over_rate is None \
            else amb.over_rate
        emb.over_cost = emb.over_therms * emb.over_rate
        emb.dra_cost = sum_none(emb.dra_rate) * emb.total_therms
        emb.sbc_rate = sum_none(emb.sbc_rate)
        emb.sbc_cost = emb.sbc_rate * emb.total_therms
        emb.tac_rate = sum_none(emb.tac_rate)
        emb.tac_cost = emb.tac_rate * emb.total_therms
        emb.ds_nysls_rate = sum_none(amb.ds_nysls_cost) / sum_none(amb.bsc_cost, amb.next_cost, amb.over_cost,
                                                                   amb.dra_cost, amb.sbc_cost, amb.bc_cost)
        subtotal = sum_none(emb.bsc_cost, emb.next_cost, emb.over_cost, emb.dra_cost, emb.sbc_cost, emb.tac_cost,
                            emb.bc_cost)
        emb.ds_nysls_cost = emb.ds_nysls_rate * subtotal
        emb.ds_nysst_rate = amb.ds_nysst_rate
        emb.ds_nysst_cost = emb.ds_nysst_rate * (subtotal + emb.ds_nysls_cost)
        emb.ds_total_cost = subtotal + emb.ds_nysls_cost + emb.ds_nysst_cost
        return emb

    @classmethod
    def estimate_oca(cls, emb, ed_start, ed_end, amb):
        """ Estimate other charges/adjustments

        paperless billing credit is the only other charges/adjustments item

        Args:
            emb (NatGasBillData): estimate natural gas bill data
            ed_start (NatGasData): for the earlier month
            ed_end (NatGasData): for the later month
            amb (NatGasBillData): actual natural gas bill data

        Returns:
            NatGasBillData: emb with other charges/adjustments estimated
        """
        emb.oca_total_cost = emb.pbc_cost

        return emb

    # noinspection PyTypeChecker
    @classmethod
    def estimate_ss(cls, emb, ed_start, ed_end, amb):
        """ Estimate supply services charges

        The bill can span over two months, but I can't determine how the ratio is determined (it's not as simple as a
        ratio of days in each month). For gas supply rate (gs_rate), use the value in the actual bill. For ny state and
        local surcharges rate (ss_nysls_rate) use the ratio of the supply service nysls cost in the actual bill to the
        subtotal of all previous supply service charges (e.g. dont include supply service sales tax in the subtotal)

        Args:
            emb (NatGasBillData): estimate natural gas bill data
            ed_start (NatGasData): for the earlier month
            ed_end (NatGasData): for the later month
            amb (NatGasBillData): actual natural gas bill data

        Returns:
            NatGasBillData: emb with supply services charges estimated
        """
        def sum_none(*nums):
            return sum(filter(None, nums))

        emb.gs_cost = emb.gs_rate * emb.total_therms
        emb.ss_nysls_rate = sum_none(amb.ss_nysls_cost) / amb.gs_cost
        emb.ss_nysls_cost = emb.ss_nysls_rate * emb.gs_cost
        emb.ss_nysst_rate = amb.ss_nysst_rate
        emb.ss_nysst_cost = amb.ss_nysst_rate * emb.gs_cost
        emb.ss_total_cost = emb.gs_cost + emb.ss_nysls_cost + emb.ss_nysst_cost

        return emb

    @classmethod
    def estimate_total_cost(cls, emb):
        """ Estimate bill total cost

        Args:
            emb (NatGasBillData): estimate natural gas bill data

        Returns:
            NatGasBillData: emb with total cost estimated
        """
        emb.total_cost = emb.ds_total_cost + emb.ss_total_cost + emb.oca_total_cost
        emb = cls.set_default_tax_related_cost([(emb, Decimal("NaN"))])[0]

        return emb

    @classmethod
    def estimate_total_therms(cls, emb):
        """ Estimate what total natural gas therms would have been without solar

        Add the saved therms to the total, since the furnace would have been used if no solar bank was available.

        Args:
            emb (NatGasBillData): estimate natural gas bill data

        Returns:
            NatGasBillData: emb with total_therms set appropriately
        """
        emb.total_therms += emb.saved_therms

        return emb

    @classmethod
    def estimate_monthly_bill(cls, amb, emb, ud_start, ud_end):
        """ Run the process of estimating the monthly bill if solar were not used

        Nat gas bill is lowered due to using kwh bank for electric heating instead of nat gas heating

        Args:
            amb (NatGasBillData): actual bill data
            emb (NatGasBillData): estimated bill data
            ud_start (NatGasData): utility data for the start month of the actual bill
            ud_end (NatGasData): utility data for the end month of the actual bill

        Returns:
            NatGasBillData: emb with all applicable estimate fields set
        """
        emb = cls.estimate_total_therms(emb)
        emb = cls.estimate_ds(emb, ud_start, ud_end, amb)
        emb = cls.estimate_ss(emb, ud_start, ud_end, amb)
        emb = cls.estimate_oca(emb, ud_start, ud_end, amb)
        emb = cls.estimate_total_cost(emb)
        emb.round_fields()

        return emb

    @classmethod
    def initialize_complex_service_bill_estimate(cls, amb):
        """ Initialize monthly bill estimate using data from actual bill

        Args:
            amb (NatGasBillData): actual natural gas bill data

        Returns:
            NatGasBillData: with real_estate, service_provider, start_date, end_date, total_therms, bsc_therms,
            bsc_cost, gs_rate, dra_rate, sbc_rate, tac_rate, bc_cost, ds_nysst_rate, ss_nysst_rate, pbc_cost set with
            same values as in actual bill
        """
        return NatGasBillData.objects.full_constructor(
            amb.real_estate, amb.service_provider, amb.start_date, amb.end_date, None, None, False, amb.total_therms,
            None, amb.bsc_therms, amb.bsc_cost, None, amb.next_rate, None, None, amb.gs_rate, None, None, None,
            dra_rate=amb.dra_rate, sbc_rate=amb.sbc_rate, tac_rate=amb.tac_rate, bc_cost=amb.bc_cost,
            ds_nysst_rate=amb.ds_nysst_rate, ss_nysst_rate=amb.ss_nysst_rate, pbc_cost=amb.pbc_cost, create=False)

    @classmethod
    def process_service_bill(cls, file):
        """ Open, process and return national grid monthly bill

        Args:
            file (Union[str, django.core.files.base.File]): name of file in media directory /files/input/natgas/ or a
                File object.

        Returns:
            NatGasBillData: with all required fields populated and as many non required fields as available populated

        Raises:
            ValueError: unable to read relevant data in bill
        """
        if isinstance(file, str):
            file = settings.MEDIA_ROOT + "/files/input/natgas/" + file

        df_list = tabula.read_pdf(file, pages="all", password="11720", guess=False)
        bill_data = NatGasBillData.objects.default_constructor()
        bill_data.saved_therms = 0
        bill_data.is_actual = True
        bill_data.bill_file = file

        df = None
        for df_1 in df_list:
            if "page2of3" in [x.replace(" ", "").lower() for x in df_1.columns]:
                df = df_1
                break
        if df is None:
            raise ValueError("Unable to read relevant data in bill: " + str(file))
        keep_cols = [c for c in df.columns if any([x in c.lower() for x in ["service", "page"]])]
        df = df[keep_cols]
        df.columns = [1, 2]

        def fmt_dec(str_val):
            return Decimal(str_val.replace("$", "").replace(" ", ""))

        date_found = False
        total_found = False
        total_therms_found = False
        next_found = False
        in_delivery_services = True
        for ind, row in df.iterrows():
            str1 = row[1]
            str2 = row[2]
            if isinstance(str1, str):
                row_split = str1.split(" ")

                if " to " in str1 and not date_found:
                    bill_data.start_date = datetime.datetime.strptime(" ".join(row_split[0:3]), "%b %d, %Y").date()
                    bill_data.start_date = bill_data.start_date + datetime.timedelta(days=1)
                    bill_data.end_date = datetime.datetime.strptime(" ".join(row_split[-3:]), "%b %d, %Y").date()
                    date_found = True
                elif "Basic Service Charge" in str1:
                    bill_data.bsc_therms = Decimal(row_split[-2])
                    bill_data.bsc_cost = Decimal(str2)
                elif "Next" in str1:
                    bill_data.next_therms = Decimal(row_split[1])
                    bill_data.next_rate = Decimal(row_split[3])
                    bill_data.next_cost = Decimal(str2)
                    next_found = True
                elif "Over/Last" in str1:
                    if next_found:
                        bill_data.over_therms = Decimal(row_split[1])
                        bill_data.over_rate = Decimal(row_split[3])
                        bill_data.over_cost = round(bill_data.over_therms * bill_data.over_rate, 2)
                    else:
                        bill_data.next_therms = Decimal(row_split[1])
                        bill_data.next_rate = Decimal(row_split[3])
                        bill_data.next_cost = round(bill_data.next_therms * bill_data.next_rate, 2)
                elif "Delivery Rate Adj" in str1:
                    bill_data.dra_rate = round(Decimal(row_split[3]), 6)
                    # stupid formatting in pdf might push the cost from the expected column to another column
                    bill_data.dra_cost = round(bill_data.total_therms * bill_data.dra_rate, 2) if pd.isna(str2) \
                        else Decimal(str2)
                elif "System Benefits Charge" in str1:
                    bill_data.sbc_rate = Decimal(row_split[3])
                    bill_data.sbc_cost = Decimal(str2)
                elif "Transp Adj Chg" in str1:
                    bill_data.tac_rate = Decimal(row_split[3])
                    bill_data.tac_cost = Decimal(str2)
                elif "Billing Charge" in str1:
                    bill_data.bc_cost = Decimal(str2)
                elif "NY State and Local Surcharges" in str1 and in_delivery_services:
                    bill_data.ds_nysls_cost = Decimal(str2)
                elif "NY State Sales Tax" in str1 and in_delivery_services:
                    bill_data.ds_nysst_rate = Decimal(row_split[4]) / 100
                    bill_data.ds_nysst_cost = Decimal(str2)
                elif "Total Delivery Services" in str1:
                    bill_data.ds_total_cost = fmt_dec(str2)
                    in_delivery_services = False
                elif "Gas Supply" in str1:
                    bill_data.gs_rate = Decimal(row_split[2])
                    bill_data.gs_cost = Decimal(str2)
                elif "NY State and Local Surcharges" in str1 and not in_delivery_services:
                    bill_data.ss_nysls_cost = Decimal(str2)
                elif "Sales Tax" in str1 and not in_delivery_services:
                    if "NY State Sales Tax" in str1:
                        bill_data.ss_nysst_rate = Decimal(row_split[4]) / 100
                    else:
                        bill_data.ss_nysst_rate = Decimal("0.025")
                        bill_data.notes = "No supply services sales tax provided. Assumed to be 0.025."
                    bill_data.ss_nysst_cost = Decimal(str2)
                elif "Total Supply Services" in str1:
                    bill_data.ss_total_cost = fmt_dec(str2)
                elif "Paperless Billing Credit" in str1:
                    bill_data.pbc_cost = Decimal(str2)
                elif "Total Other Charges/Adjustments" in str1:
                    bill_data.oca_total_cost = fmt_dec(str2)

            if isinstance(str2, str):
                if not total_found:
                    # total should be the first string in column 2
                    bill_data.total_cost = fmt_dec(str2)
                    total_found = True
                elif "=  Used" in str2 and not total_therms_found:
                    total_therms_found = True
                elif total_therms_found:
                    bill_data.total_therms = int(str2)
                    total_therms_found = False

        bill_data.real_estate = RealEstate.objects.filter(address=Address.to_address(df.at[2, 1] + df.at[3, 1])).get()
        bill_data.service_provider = ServiceProvider.objects.filter(provider=ServiceProviderEnum.NG_UTI).get()
        bill_data.round_fields()

        return bill_data

    @classmethod
    def set_default_tax_related_cost(cls, bill_tax_related_cost_list):
        bill_list = []
        for bill, tax_related_cost in bill_tax_related_cost_list:
            if tax_related_cost.is_nan():
                bill.tax_rel_cost = bill.total_cost if bill.real_estate.bill_tax_related else Decimal(0)
            else:
                bill.tax_rel_cost = tax_related_cost
            bill_list.append(bill)
        return bill_list

    @classmethod
    def valid_providers(cls):
        """ Which service providers are valid for this model

        Returns:
            list[ServiceProviderEnum]: [ServiceProviderEnum.NG_UTI]
        """
        return [ServiceProviderEnum.NG_UTI]