from decimal import Decimal
from typing import Optional, Union
import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
import tabula

from .complexservicebilldatabase import ComplexServiceBillDataBase
from .electricdata import ElectricData
from .realestate import Address, RealEstate
from .serviceprovider import ServiceProvider, ServiceProviderEnum


class ElectricBillDataManager(models.Manager):

    def default_constructor(self):
        """ Instantiate (but don't create) ElectricBillData instance with None for all attributes

        Returns:
            ElectricBillData: instance
        """
        return self.full_constructor(
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, create=False)

    def full_constructor(self, real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost, is_actual,
                         total_kwh, eh_kwh, bank_kwh, bs_rate, bs_cost, dsc_total_cost, toc_total_cost, first_kwh=None,
                         first_rate=None, first_cost=None, next_kwh=None, next_rate=None, next_cost=None, cbc_rate=None,
                         cbc_cost=None, mfc_rate=None, mfc_cost=None, psc_rate=None, psc_cost=None, psc_total_cost=None,
                         der_rate=None, der_cost=None, dsa_rate=None, dsa_cost=None, rda_rate=None, rda_cost=None,
                         nysa_rate=None, nysa_cost=None, rbp_rate=None, rbp_cost=None, spta_rate=None, spta_cost=None,
                         st_rate=None, st_cost=None, paid_date=None, notes=None, bill_file=None, create=True):
        """ Instantiate ElectricBillData instance with option to save to database

        Args:
            see ElectricBillData class docstring
            create (bool): False to create instance only. Default True to also save to database (self.create)

        Returns:
            ElectricBillData: instance
        """
        return (self.create if create else ElectricBillData)(
            real_estate=real_estate, service_provider=service_provider, start_date=start_date, end_date=end_date,
            total_cost=total_cost, tax_rel_cost=tax_rel_cost, is_actual=is_actual, total_kwh=total_kwh, eh_kwh=eh_kwh,
            bank_kwh=bank_kwh, bs_rate=bs_rate, bs_cost=bs_cost, dsc_total_cost=dsc_total_cost,
            toc_total_cost=toc_total_cost, first_kwh=first_kwh, first_rate=first_rate, first_cost=first_cost,
            next_kwh=next_kwh, next_rate=next_rate, next_cost=next_cost, cbc_rate=cbc_rate, cbc_cost=cbc_cost,
            mfc_rate=mfc_rate, mfc_cost=mfc_cost, psc_rate=psc_rate, psc_cost=psc_cost, psc_total_cost=psc_total_cost,
            der_rate=der_rate, der_cost=der_cost, dsa_rate=dsa_rate, dsa_cost=dsa_cost, rda_rate=rda_rate,
            rda_cost=rda_cost, nysa_rate=nysa_rate, nysa_cost=nysa_cost, rbp_rate=rbp_rate, rbp_cost=rbp_cost,
            spta_rate=spta_rate, spta_cost=spta_cost, st_rate=st_rate, st_cost=st_cost, paid_date=paid_date,
            notes=notes, bill_file=bill_file)


class ElectricBillData(ComplexServiceBillDataBase):
    """ Actual or estimated data provided on monthly electric bill or relevant to monthly bill

    Attributes:
        see super class docstring
        total_kwh (int): nonnegative total kwh used from provider
        eh_kwh (int): electric heater kwh usage
        bank_kwh (int): nonnegative banked kwh
        bs_rate (Decimal): basic service charge rate
        bs_cost (Decimal): basic service charge cost
        dsc_total_cost (Decimal): delivery and service charge total cost
        toc_total_cost (Decimal): taxes and other charges total cost
        first_kwh (Optional[int]): kwh used at first rate. will not be in bill if none used. Default None
        first_rate (Optional[Decimal]): first rate. will not be in bill if none used. Default None
        first_cost (Optional[Decimal]): first cost. will not be in bill if none used. Default None
        next_kwh (Optional[int]): kwh used at next rate. will not be in bill if none used. Default None
        next_rate (Optional[Decimal]): next rate. will not be in bill if none used. Default None
        next_cost (Optional[Decimal]): next cost. will not be in bill if none used. Default None
        cbc_rate (Optional[Decimal]): customer benefit contribution charge rate. Default None
        cbc_cost (Optional[Decimal]): customer benefit contribution charge cost. Default None
        mfc_rate (Optional[Decimal]): merchant function charge rate. Default None
        mfc_cost (Optional[Decimal]): merchant function charge cost. Default None
        psc_rate (Optional[Decimal]): power supply charge rate. Default None
        psc_cost (Optional[Decimal]): power supply charge cost. Default None
        psc_total_cost (Optional[Decimal]): power supply charge total cost. Default None
        der_rate (Optional[Decimal]): distributed energy resources charge rate. Default None
        der_cost (Optional[Decimal]): distributed energy resources charge cost. Default None
        dsa_rate (Optional[Decimal]): delivery service adjustment rate. Default None
        dsa_cost (Optional[Decimal]): delivery service adjustment cost. Default None
        rda_rate (Optional[Decimal]): revenue decoupling adjustment rate. Default None
        rda_cost (Optional[Decimal]): revenue decoupling adjustment cost. Default None
        nysa_rate (Optional[Decimal]): new york state assessment rate. Default None
        nysa_cost (Optional[Decimal]): new york state assessment cost. Default None
        rbp_rate (Optional[Decimal]): revenue based pilots rate. Default None
        rbp_cost (Optional[Decimal]): revenue based pilots cost. Default None
        spta_rate (Optional[Decimal]): suffolk property tax adjustment rate. Default None
        spta_cost (Optional[Decimal]): suffolk property tax adjustment cost. Default None
        st_rate (Optional[Decimal]): sales tax rate. Default None
        st_cost (Optional[Decimal]): sales tax cost. Default None
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
        return "files/input/electric/" + filename

    def validate_service_provider(service_provider):
        service_provider = ServiceProvider.objects.get(pk=service_provider)
        if service_provider.provider not in ElectricBillData.valid_providers():
            raise ValidationError(str(service_provider) + " is not a valid service provider")

    # noinspection PyMethodParameters
    def valid_service_providers():
        return {"provider__in": ElectricBillData.valid_providers()}

    service_provider = models.ForeignKey(ServiceProvider, models.PROTECT, validators=[validate_service_provider],
                                         limit_choices_to=valid_service_providers)
    bill_file = models.FileField(blank=True, null=True, upload_to=file_upload_path)
    total_kwh = models.PositiveSmallIntegerField()
    eh_kwh = models.PositiveSmallIntegerField()
    bank_kwh = models.PositiveIntegerField()
    bs_rate = models.DecimalField(max_digits=6, decimal_places=4)
    bs_cost = models.DecimalField(max_digits=6, decimal_places=2)
    first_kwh = models.PositiveSmallIntegerField(blank=True, null=True)
    first_rate = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    first_cost = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    next_kwh = models.PositiveSmallIntegerField(blank=True, null=True)
    next_rate = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    next_cost = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    cbc_rate = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    cbc_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    mfc_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    mfc_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    dsc_total_cost = models.DecimalField(max_digits=6, decimal_places=2)
    psc_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    psc_cost = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    psc_total_cost = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    der_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    der_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    dsa_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    dsa_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    rda_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    rda_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    nysa_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    nysa_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    rbp_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    rbp_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    spta_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    spta_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    st_rate = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    st_cost = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    toc_total_cost = models.DecimalField(max_digits=5, decimal_places=2)

    objects = ElectricBillDataManager()

    def __repr__(self):
        """ __repr__ override

        Format:
            super().__repr__()
            Total KWH: self.total_kwh, Electric Heater KWH: self.eh_kwh, Bank KWH: self.bank_kwh
            Delivery & System Charges: Total Cost: self.dsc_total_cost
              Basic: Rate: self.bs_rate/day, Cost: self.bs_cost
              First: KWH: self.first_kwh, Rate: self.first_rate/kwh, Cost: self.first_cost
              Next: KWH: self.next_kwh, Rate: self.next_rate/kwh, Cost: self.next_cost
              Customer Benefit Contribution: Rate: self.cbc_rate/day, Cost: self.cbc_cost
              Merchant Function Charge: Rate: self.mfc_rate/kwh, Cost: self.mfc_cost
            Power Supply Charges: Total Cost: self.psc_total_cost
              Power Supply: Rate: self.psc_rate/kwh, Cost: self.psc_cost
            Taxes & Other Charges: Total Cost: self.toc_total_cost
              Distributed Energy Resources: Rate: self.der_cost/kwh, Cost: self.der_cost
              Delivery Service Adjustment: Rate: self.dsa_rate, Cost: self.dsa_cost
              Revenue Decoupling Adjustment: Rate: self.rda_rate, Cost: self.rda_cost
              New York State Assessment: Rate: self.nysa_rate, Cost: self.nysa_cost
              Revenue Based Pilots: Rate: self.rbp_rate, Cost: self.rbp_cost
              Suffolk Property Tax Adjustment: Rate: self.spta_rate, Cost: self.spta_cost
              Sales Tax: Rate: self.st_rate, Cost: self.st_cost

        Returns:
            str: as described by Format
        """
        return super().__repr__() + \
            "\nTotal KWH: " + str(self.total_kwh) + ", Electric Heater KWH: " + str(self.eh_kwh) + ", Bank KWH: " + \
            str(self.bank_kwh) + \
            "\nDelivery & System Charges: Total Cost: " + str(self.dsc_total_cost) + \
            "\n  Basic: Rate: " + str(self.bs_rate) + "/day, Cost: " + str(self.bs_cost) + \
            "\n  First: KWH: " + str(self.first_kwh) + ", Rate: " + str(self.first_rate) + "/kwh, Cost: " + \
                str(self.first_cost) + \
            "\n  Next: KWH: " + str(self.next_kwh) + ", Rate: " + str(self.next_rate) + "/kwh, Cost: " + \
                str(self.next_cost) + \
            "\n  Customer Benefit Contribution: Rate: " + str(self.cbc_rate) + "/day, Cost: " + str(self.cbc_cost) + \
            "\n  Merchant Function Charge: Rate: " + str(self.mfc_rate) + "/kwh, Cost: " + str(self.mfc_cost) + \
            "\nPower Supply Charges: Total Cost: " + str(self.psc_total_cost) + \
            "\n  Power Supply: Rate: " + str(self.psc_rate) + "/kwh, Cost: " + str(self.psc_cost) + \
            "\nTaxes & Other Charges: Total Cost: " + str(self.toc_total_cost) + \
            "\n  Distributed Energy Resources: Rate: " + str(self.der_rate) + "/kwh, Cost: " + str(self.der_cost) + \
            "\n  Delivery Service Adjustment: Rate: " + str(self.dsa_rate) + ", Cost: " + str(self.dsa_cost) + \
            "\n  Revenue Decoupling Adjustment: Rate: " + str(self.rda_rate) + ", Cost: " + str(self.rda_cost) + \
            "\n  New York State Assessment: Rate: " + str(self.nysa_rate) + ", Cost: " + str(self.nysa_cost) + \
            "\n  Revenue Based Pilots: Rate: " + str(self.rbp_rate) + ", Cost: " + str(self.rbp_cost) + \
            "\n  Suffolk Property Tax Adjustment: Rate: " + str(self.spta_rate) + ", Cost: " + str(self.spta_cost) + \
            "\n  Sales Tax: Rate: " + str(self.st_rate) + ", Cost: " + str(self.st_cost)

    def modify(self, cost_ratio=None, real_estate=None, **kwargs):
        """ see superclass docstring

        Ratio applied to KWH, cost and BS Rate attributes.
        """
        bill_copy = super().modify(cost_ratio=cost_ratio, real_estate=real_estate, **kwargs)

        if cost_ratio is not None:
            def dec_mult_none(left):
                return None if left is None else left * cost_ratio

            def int_mult_none(left):
                return None if left is None else int(left * cost_ratio)

            bill_copy.total_kwh = int_mult_none(bill_copy.total_kwh)
            bill_copy.eh_kwh = int_mult_none(bill_copy.eh_kwh)
            bill_copy.bank_kwh = int_mult_none(bill_copy.bank_kwh)

            bill_copy.bs_rate *= cost_ratio
            bill_copy.bs_cost *= cost_ratio
            bill_copy.first_kwh = int_mult_none(bill_copy.first_kwh)
            bill_copy.first_cost = dec_mult_none(bill_copy.first_cost)
            bill_copy.next_kwh = int_mult_none(bill_copy.next_kwh)
            bill_copy.next_cost = dec_mult_none(bill_copy.next_cost)
            bill_copy.cbc_cost = dec_mult_none(bill_copy.cbc_cost)
            bill_copy.mfc_cost = dec_mult_none(bill_copy.mfc_cost)
            bill_copy.dsc_total_cost *= cost_ratio

            bill_copy.psc_cost = dec_mult_none(bill_copy.psc_cost)
            bill_copy.psc_total_cost = dec_mult_none(bill_copy.psc_total_cost)
            bill_copy.der_cost = dec_mult_none(bill_copy.der_cost)
            bill_copy.dsa_cost = dec_mult_none(bill_copy.dsa_cost)
            bill_copy.rda_cost = dec_mult_none(bill_copy.rda_cost)
            bill_copy.nysa_cost = dec_mult_none(bill_copy.nysa_cost)
            bill_copy.rbp_cost = dec_mult_none(bill_copy.rbp_cost)
            bill_copy.spta_cost = dec_mult_none(bill_copy.spta_cost)
            bill_copy.st_cost = dec_mult_none(bill_copy.st_cost)
            bill_copy.toc_total_cost *= cost_ratio

            bill_copy.notes += " Ratio of " + str(cost_ratio) + " applied to KWH, cost and BS Rate attributes."

        return bill_copy

    def tax_related_cost_message(self):
        return self.tax_related_cost_message_helper("Electric", "total cost", "0")

    @classmethod
    def estimate_total_kwh(cls, emb):
        """ Estimate what total kwh usage would have been without solar

        Remove the electric heater kwh usage from the total, since the electric heater would not have been used if no
        solar bank was available.

        Args:
            emb (ElectricBillData): estimate electric bill data

        Returns:
            ElectricBillData: emb with total_kwh set appropriately
        """
        emb.total_kwh -= emb.eh_kwh

        return emb

    # noinspection PyTypeChecker
    @classmethod
    def estimate_dsc(cls, emb, ed_start, ed_end):
        """ Estimate delivery and system charges

        The bill can span over two months, so have to determine the ratio of the bill for each month. This function
        uses days to calculate the ratio, but this is only estimate since the kwh usage in each day varies.

        Args:
            emb (ElectricBillData): estimate electric bill data
            ed_start (ElectricData): for the earlier month
            ed_end (ElectricData): for the later month

        Returns:
            ElectricBillData: emb with delivery and system charges estimated
        """
        e_rat = Decimal(emb.end_date.day / ((emb.end_date - emb.start_date).days + 1))
        s_rat = 1 - e_rat

        emb.first_kwh = min(emb.total_kwh, int(ed_start.first_kwh * s_rat + ed_end.first_kwh * e_rat))
        emb.first_rate = ed_start.first_rate * s_rat + ed_end.first_rate * e_rat
        emb.first_cost = emb.first_kwh * emb.first_rate
        emb.next_kwh = emb.total_kwh - emb.first_kwh
        emb.next_rate = ed_start.next_rate * s_rat + ed_end.next_rate * e_rat
        emb.next_cost = emb.next_kwh * emb.next_rate
        emb.mfc_rate = ed_start.mfc_rate * s_rat + ed_end.mfc_rate * e_rat
        emb.mfc_cost = emb.total_kwh * emb.mfc_rate
        emb.dsc_total_cost = emb.bs_cost + emb.first_cost + emb.next_cost + emb.mfc_cost

        return emb

    # noinspection PyTypeChecker
    @classmethod
    def estimate_psc(cls, emb, ed_start, ed_end):
        """ Estimate power supply charges

        The bill can span over two months, so have to determine the ratio of the bill for each month. This function
        uses days to calculate the ratio, but this is only estimate since the kwh usage in each day varies.

        Args:
            emb (ElectricBillData): estimate electric bill data
            ed_start (ElectricData): for the earlier month
            ed_end (ElectricData): for the later month

        Returns:
            ElectricBillData: emb with power supply charges estimated
        """
        e_rat = Decimal(emb.end_date.day / ((emb.end_date - emb.start_date).days + 1))
        s_rat = 1 - e_rat

        emb.psc_rate = ed_start.psc_rate * s_rat + ed_end.psc_rate * e_rat
        emb.psc_cost = emb.total_kwh * emb.psc_rate
        emb.psc_total_cost = emb.psc_cost

        return emb

    # noinspection PyTypeChecker
    @classmethod
    def estimate_toc(cls, emb, ed_start, ed_end, amb):
        """ Estimate taxes and other charges

        The bill can span over two months, so have to determine the ratio of the bill for each month. This function
        uses days to calculate the ratio, but this is only estimate since the kwh usage in each day varies.

        Args:
            emb (ElectricBillData): estimate electric bill data
            ed_start (ElectricData): for the earlier month
            ed_end (ElectricData): for the later month
            amb (ElectricBillData): actual electric bill data

        Returns:
            ElectricBillData: emb with taxes and other charges estimated
        """
        e_rat = Decimal(emb.end_date.day / ((emb.end_date - emb.start_date).days + 1))
        s_rat = 1 - e_rat

        # cost dependent on total kwh
        emb.der_rate = ed_start.der_rate * s_rat + ed_end.der_rate * e_rat
        emb.der_cost = emb.total_kwh * emb.der_rate

        # cost dependent on delivery and system charges
        emb.dsa_rate = ed_start.dsa_rate * s_rat + ed_end.dsa_rate * e_rat
        emb.dsa_cost = emb.dsc_total_cost * emb.dsa_rate
        emb.rda_rate = ed_start.rda_rate * s_rat + ed_end.rda_rate * e_rat
        emb.rda_cost = emb.dsc_total_cost * emb.rda_rate
        emb.rbp_rate = ed_start.rbp_rate * s_rat + ed_end.rbp_rate * e_rat
        emb.rbp_cost = emb.dsc_total_cost * emb.rbp_rate

        # cost dependent on subtotal up to this point minus rbp_cost
        subtotal = (emb.dsc_total_cost + emb.psc_total_cost + emb.der_cost + emb.dsa_cost + emb.rda_cost)
        emb.nysa_rate = ed_start.nysa_rate * s_rat + ed_end.nysa_rate * e_rat
        emb.nysa_cost = subtotal * emb.nysa_rate

        # cost dependent on subtotal up to this point minus rbp_cost
        subtotal = (emb.dsc_total_cost + emb.psc_total_cost + emb.der_cost + emb.dsa_cost + emb.rda_cost
                    + emb.nysa_cost)
        emb.spta_rate = ed_start.spta_rate * s_rat + ed_end.spta_rate * e_rat
        emb.spta_cost = subtotal * emb.spta_rate

        # cost dependent on subtotal up to this point
        subtotal = (emb.dsc_total_cost + emb.psc_total_cost + emb.der_cost + emb.dsa_cost + emb.rda_cost + emb.nysa_cost
                    + emb.rbp_cost + emb.spta_cost)
        emb.st_rate = amb.st_rate
        emb.st_cost = emb.st_rate * subtotal

        emb.toc_total_cost = (emb.der_cost + emb.dsa_cost + emb.rda_cost + emb.nysa_cost + emb.rbp_cost + emb.spta_cost
                              + emb.st_cost)

        return emb

    # noinspection PyTypeChecker
    @classmethod
    def estimate_total_cost(cls, emb):
        """ Estimate bill total cost

        Args:
            emb (ElectricBillData): estimate electric bill data

        Returns:
            ElectricBillData: emb with total cost estimated
        """
        emb.total_cost = emb.dsc_total_cost + emb.psc_total_cost + emb.toc_total_cost
        emb = cls.set_default_tax_related_cost([(emb, Decimal("NaN"))])[0]

        return emb

    @classmethod
    def estimate_monthly_bill(cls, amb, emb, ud_start, ud_end):
        """ Run the process of estimating the monthly bill if solar were not used

        Args:
            amb (ElectricBillData): actual electric bill data
            emb (ElectricBillData): estimated electric bill data
            ud_start (ElectricData): electric data for the start month of the electric bill
            ud_end (ElectricData): electric data for the end month of the electric bill

        Returns:
            ElectricBillData: estimated monthly bill with all applicable estimate fields set
        """
        emb = cls.estimate_total_kwh(emb)
        emb = cls.estimate_dsc(emb, ud_start, ud_end)
        emb = cls.estimate_psc(emb, ud_start, ud_end)
        emb = cls.estimate_toc(emb, ud_start, ud_end, amb)
        emb = cls.estimate_total_cost(emb)
        emb.round_fields()

        return emb

    @classmethod
    def initialize_complex_service_bill_estimate(cls, amb):
        """ Initialize monthly bill estimate using data from actual bill

        Returned instance is not saved to database

        Args:
            amb (ElectricBillData): actual electric bill data

        Returns:
            ElectricBillData: with real_estate, provider, start_date and end_date set with same values as in actual bill
        """
        return ElectricBillData.objects.full_constructor(
            amb.real_estate, amb.service_provider, amb.start_date, amb.end_date, None, None, False, None, 0, 0,
            amb.bs_rate, amb.bs_cost, None, None, create=False)

    @classmethod
    def process_service_bill(cls, file):
        """ Open, process and return pseg monthly bill

        Args:
            file (Union[str, django.core.files.base.File]): name of file in media directory /files/input/electric/ or a
                File object.

        Returns:
            ElectricBillData: with all required fields populated and as many non required fields as available populated.
                Instance is not saved to database.

        Raises:
            ObjectDoesNotExist: if real estate or service provider not found
        """
        if isinstance(file, str):
            file = settings.MEDIA_ROOT + "/files/input/electric/" + file

        df_list = tabula.read_pdf(file, pages="all", password="11720", guess=False)
        bill_data = ElectricBillData.objects.default_constructor()
        bill_data.eh_kwh = 0
        bill_data.bank_kwh = 0
        bill_data.is_actual = True
        bill_data.bill_file = file

        # get start date and end date from 1st page
        srs = df_list[0]
        srs = srs[srs.columns[1]]
        service_to_found = False
        address = None
        for row in srs.values:
            if not isinstance(row, str):
                continue
            if "Service To" in row:
                # address is the next row
                service_to_found = True
            elif service_to_found:
                address = Address.to_address(row)
                service_to_found = False
            elif "Service From" in row:
                row = row.split(" ")
                bill_data.start_date = datetime.datetime.strptime("".join(row[-7:-4]), "%b%d,%Y").date()
                bill_data.start_date = bill_data.start_date + datetime.timedelta(days=1)
                bill_data.end_date = datetime.datetime.strptime("".join(row[-3:]), "%b%d,%Y").date()
                break

        # get total kwh from 2nd page third column if it is there. it might be in the first column
        srs = df_list[1]
        srs = srs[srs.columns[2]]
        for row in srs.values:
            if not isinstance(row, str):
                continue
            if "Billed KWH" in row:
                bill_data.total_kwh = int(row.split()[-1].strip())

        # get remaining data from 2nd page first column. get total kwh from here if it is here
        srs = df_list[1]
        srs = srs[srs.columns[0]]
        in_psc = False

        def fmt_int(rs, ind):
            return int(rs[ind].replace(",", "").strip())

        def fmt_dec(rs, ind):
            return Decimal(rs[ind].replace(",", "").strip())

        for row in srs.values:
            if not isinstance(row, str):
                continue

            row_split = row.split(" ")

            if "Electricity used in" in row:
                bill_data.total_kwh = fmt_int(row_split, -2)
            elif "Energy Credit Balance" in row:
                bill_data.bank_kwh = fmt_int(row_split, -1)
            elif "Delivery & System Charges" in row:
                bill_data.dsc_total_cost = fmt_dec(row_split, -1)
            elif "Basic Service" in row:
                bill_data.bs_rate = fmt_dec(row_split, -3)
                bill_data.bs_cost = fmt_dec(row_split, -1)
            elif "CBC" in row:
                bill_data.cbc_rate = fmt_dec(row_split, -3)
                bill_data.cbc_cost = fmt_dec(row_split, -1)
            elif "MFC" in row:
                bill_data.mfc_rate = fmt_dec(row_split, -3)
                bill_data.mfc_cost = fmt_dec(row_split, -1)
            elif all(x in row for x in ["First", "@"]):
                bill_data.first_kwh = fmt_int(row_split, 1)
                bill_data.first_rate = fmt_dec(row_split, 5)
                bill_data.first_cost = fmt_dec(row_split, -1)
            elif all(x in row for x in ["Next", "@"]):
                bill_data.next_kwh = fmt_int(row_split, 1)
                bill_data.next_rate = fmt_dec(row_split, 5)
                bill_data.next_cost = fmt_dec(row_split, -1)
            elif "Power Supply Charges" in row:
                bill_data.psc_total_cost = fmt_dec(row_split, -1)
                in_psc = True
            elif in_psc and all(x in row for x in ["KWH", "@", "="]):
                bill_data.psc_rate = fmt_dec(row_split, -3)
                bill_data.psc_cost = fmt_dec(row_split, -1)
                in_psc = False
            elif "Taxes & Other Charges" in row:
                bill_data.toc_total_cost = fmt_dec(row_split, -1)
            elif "DER Charge" in row:
                bill_data.der_rate = fmt_dec(row_split, -3)
                bill_data.der_cost = fmt_dec(row_split, -1)
            elif "Delivery Service Adjustment" in row:
                bill_data.dsa_cost = fmt_dec(row_split, -1)
            elif "Revenue Decoupling Adjustment" in row and len(row_split) == 4:
                bill_data.rda_cost = fmt_dec(row_split, -1)
            elif "NY State Assessment" in row:
                bill_data.nysa_cost = fmt_dec(row_split, -1)
            elif "Revenue-Based PILOTS" in row:
                bill_data.rbp_cost = fmt_dec(row_split, -1)
            elif "Suffolk Property Tax Adjustment" in row:
                bill_data.spta_cost = fmt_dec(row_split, -1)
            elif "Sales Tax" in row:
                bill_data.st_rate = fmt_dec(row_split, -3) / 100
                bill_data.st_cost = fmt_dec(row_split, -1)
            elif "Total Charges" in row:
                bill_data.total_cost = fmt_dec(row_split, -1)

        bill_data.real_estate = RealEstate.objects.filter(address=address).get()
        bill_data.service_provider = ServiceProvider.objects.filter(provider=ServiceProviderEnum.PSEG_UTI).get()
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
            list[ServiceProviderEnum]: [ServiceProviderEnum.PSEG_UTI]
        """
        return [ServiceProviderEnum.PSEG_UTI]
