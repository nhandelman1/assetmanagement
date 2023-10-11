from decimal import Decimal
from typing import Optional, Union
import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
import pandas as pd


from .realestate import RealEstate
from .realpropertyvalue import RealPropertyValue
from .serviceprovider import ServiceProvider, ServiceProviderEnum
from .simpleservicebilldatabase import SimpleServiceBillDataBase
from ..taxation import DepreciationTaxation
from util.pythonutil import textwrap_lines


class DepreciationBillDataManager(models.Manager):

    def default_constructor(self):
        """ Instantiate (but don't create) DepreciationBillData instance with None for all attributes

        Returns:
            DepreciationBillData: instance
        """
        return self.full_constructor(None, None, None, None, None, None, None, None, create=False)

    def full_constructor(self, real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost,
                         real_property_value, period_usage_pct, paid_date=None, notes=None, bill_file=None,
                         create=True):
        """ Instantiate DepreciationBillData instance with option to save to database

        Args:
            see DepreciationBillData class docstring
            create (bool): False to create instance only. Default True to also save to database (self.create)

        Returns:
            DepreciationBillData: instance
        """
        return (self.create if create else DepreciationBillData)(
            real_estate=real_estate, service_provider=service_provider, start_date=start_date, end_date=end_date,
            total_cost=total_cost, tax_rel_cost=tax_rel_cost, real_property_value=real_property_value,
            period_usage_pct=period_usage_pct, paid_date=paid_date, notes=notes, bill_file=bill_file)


class DepreciationBillData(SimpleServiceBillDataBase):
    """ Actual bill data for depreciation items

    Attributes:
        see superclass docstring
        start_date (datetime.date): must be first day of the year (i.e. YYYY-01-01). also enforced by database
        end_date (datetime.date): must be last day of the year (i.e. YYYY-12-31). also enforced by database
        real_property_value (RealPropertyValue): depreciation item associated with this bill
        period_usage_pct (Decimal): should be percent value between 000.00 and 100.00 (inclusive).
            also enforced by database. percent of period item used for business purposes (active or idle). period
            might not be a full year due to purchase date or disposal date probably aren't on Jan 1st
        paid_date (Optional[datetime.date]): must be None or last day of the year (i.e. YYYY-12-31).
            also enforced by database
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["real_property_value", "start_date", "end_date"],
                                    name="unique_%(app_label)s_%(class)s_rpv_sd_ed"),
            models.CheckConstraint(check=models.Q(start_date__iendswith="-01-01"), name="sd_like_pct-01-01"),
            models.CheckConstraint(check=models.Q(end_date__iendswith="-12-31"), name="ed_like_pct-12-31"),
            models.CheckConstraint(check=models.Q(paid_date__iendswith="-12-31"), name="pd_like_pct-12-31"),
            models.CheckConstraint(check=models.Q(period_usage_pct__gte=0) & models.Q(period_usage_pct__lte=100),
                                   name="pup_between_0_100_inclusive"),
        ]
        ordering = ["real_estate", "start_date", "end_date", "real_property_value"]

    # noinspection PyMethodParameters
    def file_upload_path(instance, filename):
        return "files/input/depreciation/" + filename

    # noinspection PyMethodParameters
    def validate_end_date(end_date):
        if end_date.month != 12 or end_date.day != 31:
            raise ValidationError("end_date " + str(end_date) + " is invalid. Must have format YYYY-12-31.")

    # noinspection PyMethodParameters
    def validate_paid_date(paid_date):
        if paid_date.month != 12 or paid_date.day != 31:
            raise ValidationError("paid_date " + str(paid_date) + " is invalid. Must be None or have format YYYY-12-31.")

    # noinspection PyMethodParameters
    def validate_pct_usage_0_100(period_usage_pct):
        if period_usage_pct < Decimal(0) or period_usage_pct > Decimal(100):
            raise ValidationError("period_usage_pct " + str(period_usage_pct) +
                                  " is invalid. Must be between 000.00 and 100.00 (inclusive)")

    # noinspection PyMethodParameters
    def validate_service_provider(service_provider):
        service_provider = ServiceProvider.objects.get(pk=service_provider)
        if service_provider.provider not in DepreciationBillData.valid_providers():
            raise ValidationError(str(service_provider) + " is not a valid service provider")

    # noinspection PyMethodParameters
    def validate_start_date(start_date):
        if start_date.month != 1 or start_date.day != 1:
            raise ValidationError("start_date " + str(start_date) + " is invalid. Must have format YYYY-01-01.")

    # noinspection PyMethodParameters
    def valid_service_providers():
        return {"provider__in": DepreciationBillData.valid_providers()}

    service_provider = models.ForeignKey(ServiceProvider, models.PROTECT, validators=[validate_service_provider],
                                         limit_choices_to=valid_service_providers)
    bill_file = models.FileField(blank=True, null=True, upload_to=file_upload_path)
    start_date = models.DateField(validators=[validate_start_date])
    end_date = models.DateField(validators=[validate_end_date])
    paid_date = models.DateField(blank=True, null=True, validators=[validate_paid_date])
    real_property_value = models.ForeignKey(RealPropertyValue, models.PROTECT)
    period_usage_pct = models.DecimalField(max_digits=5, decimal_places=2, validators=[validate_pct_usage_0_100])

    objects = DepreciationBillDataManager()

    def __repr__(self):
        """ __repr__ override

        Format:
            super().__repr__()
            Period Usage Pct: self.period_usage_pct %
            Real Property Values: str(self.real_property_value)

        Returns:
            str: as described by Format
        """
        return super().__repr__() + "\nPeriod Usage Pct: " + str(self.period_usage_pct) + "%\nReal Property Values:\n" \
            + textwrap_lines(str(self.real_property_value))

    def __str__(self):
        """ __str__ override

        Format:
            super().__str__(), str(self.real_property_value.item)

        Returns:
            str: as described by Format
        """
        return super().__str__() + ", " + str(self.real_property_value.item)

    def modify(self, cost_ratio=None, real_estate=None, **kwargs):
        """ see superclass docstring

        Args:
            cost_ratio: see superclass docstring
            real_estate: see superclass docstring
            **kwargs:
                real_property_value (Optional[RealPropertyValue]): replace self.real_property_value with this value.
                    Update notes to reflect the change. Default None to not replace (or don't send the kwarg)
        """
        bill_copy = super().modify(cost_ratio=cost_ratio, real_estate=real_estate, **kwargs)
        rpv = kwargs.get("real_property_value", None)
        if rpv is not None:
            bill_copy.real_property_value = rpv
            bill_copy.notes = "" if bill_copy.notes is None else bill_copy.notes
            bill_copy.notes += " Real property values changed from original."
        return bill_copy

    def save(self, *args, **kwargs):
        self._validate_real_estate_real_property_value_same_address()
        return super().save(*args, **kwargs)

    def tax_related_cost_message(self):
        return "Depreciation bills are always tax related so tax related cost is set to total cost."

    def _validate_real_estate_real_property_value_same_address(self):
        if self.real_estate.address != self.real_property_value.real_estate.address:
            raise ValidationError("real_estate and real_property_value must have the same address")

    @classmethod
    def apply_period_usage_to_bills(cls, bill_list):
        """ Apply period usage to bills in bill_list

        Call cls.create_bills() to create bills before calling this function.
        bill.total_cost = bill.total_cost * bill.period_usage_pct / 100
        bill.tax_rel_cost *= (bill.period_usage_pct / 100)

        Args:
            bill_list (list[DepreciationBillData]):

        Returns:
            list[DepreciationBillData]: bill_list with period usage applied to total cost for each bill
        """
        for bill in bill_list:
            bill.total_cost *= (bill.period_usage_pct / 100)
            bill.tax_rel_cost *= (bill.period_usage_pct / 100)

        return bill_list

    @classmethod
    def create_bills(cls, real_estate, service_provider, year, save=True):
        """ Create depreciation bills for the provided real_estate and year assuming full period business usage

        Find all real property values for real estate and year, and create depreciation bills where applicable assuming
        full period business usage. Not all real property values for real estate are depreciable for the given year.
        This function finds the depreciable items and creates depreciation bills for them. Non depreciable items are
        also returned (see Returns:). "full period" used here instead of "full year" to indicate that first and last
        years may be partial years. Tax related cost for each bill is set to the default in this function. To apply
        period usage to each depreciation bill, see self.apply_period_usage_to_bills().

        Args:
            real_estate (RealEstate): real estate location of real property values
            service_provider (ServiceProvider): see self.valid_providers()
            year (int): year of purchase date
            save (boolean): False to not save bills to database. Default True to save bills to database.

        Returns:
            (list[DepreciationBillData], list[RealPropertyValues]): (depreciable bill data, non depreciable items)
                1st element: depreciation bills assuming full period usage. empty list if no depreciable items found.
                    Instances are saved to database depending on value of arg 'save'.
                2nd element: depreciation items that are never depreciable or have been fully depreciated. empty list
                    if no items found

        Raises:
            ValueError: if year is greater than or equal to the current year
        """
        if year >= datetime.date.today().year:
            raise ValueError(str(year) + " is not a previous year. Must be a previous year.")

        rpv_list = RealPropertyValue.objects.filter(
            real_estate=real_estate, purchase_date__lte=datetime.date(year, 12, 31))
        bill_list = []
        nd_list = []
        dep_tax = DepreciationTaxation()
        for rpv in rpv_list:
            dep_for_year, remain_dep, max_dep_for_year = dep_tax.calculate_depreciation_for_year(rpv, year)

            if dep_for_year.is_zero():
                nd_list.append(rpv)
            else:
                notes = "Max depreciation possible for full period: " + str(max_dep_for_year) + "."
                if rpv.disposal_date is not None and rpv.disposal_date.year == year:
                    notes += " Partial year depreciation. Item disposed of " + str(rpv.disposal_date) + \
                             ". Full period less than a year."
                elif rpv.purchase_date.year == year:
                    notes += " Partial year depreciation. Item purchased " + str(rpv.purchase_date) + \
                             ". Full period less than a year."
                elif dep_for_year == remain_dep:
                    notes += " Partial year depreciation. Fully depreciated this year." \
                             " Full period probably less than a year."

                bill_list.append(DepreciationBillData.objects.full_constructor(
                    real_estate, service_provider, datetime.date(year, 1, 1), datetime.date(year, 12, 31), dep_for_year,
                    None, rpv, Decimal(100), paid_date=datetime.date(year, 12, 31), notes=notes, create=False))

        bill_list = cls.set_default_tax_related_cost([(bill, Decimal("NaN")) for bill in bill_list])
        if save:
            # bulk_create also an option but it has some caveats that are concerning (e.g. not calling save())
            for bill in bill_list:
                bill.save()

        return bill_list, nd_list

    @classmethod
    def process_service_bill(cls, file):
        """ Open, process and return depreciation bill in same format as DepreciationBillTemplate.csv

        See DepreciationBillTemplate.csv in media directory /files/input/depreciation/
            address: valid values found in model realestate.Address values
            provider: see self.valid_providers() then model serviceprovider.ServiceProviderEnum for valid values
            item: an existing model realpropertyvalue.RealPropertyValue.item value
            dates: YYYY-MM-DD format
            period_usage_pct: 0.00 to 100.00 inclusive
            total cost: *.XX format
            tax related cost: *.XX format

        Args:
            file (Union[str, django.core.files.base.File]): name of file in media directory /files/input/depreciation/
                or a File object.

        Returns:
            DepreciationBillData: all attributes are set with bill values except paid_date, which is set to the value
                provided in the bill or None if not provided. Instance is not saved to database.

        Raises:
            ObjectDoesNotExist: if real estate, service provider or depreciation item not found
        """
        if isinstance(file, str):
            file = settings.MEDIA_ROOT + "/files/input/depreciation/" + file

        df = pd.read_csv(file)

        real_estate = RealEstate.objects.filter(address=df.loc[0, "address"]).get()
        service_provider = ServiceProvider.objects.filter(provider=df.loc[0, "provider"]).get()
        item = df.loc[0, "item"]
        purchase_date = datetime.datetime.strptime(df.loc[0, "purchase_date"], "%Y-%m-%d").date()
        real_property_value = RealPropertyValue.objects.filter(
            real_estate=real_estate, item=item, purchase_date=purchase_date).get()
        start_date = datetime.datetime.strptime(df.loc[0, "start_date"], "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(df.loc[0, "end_date"], "%Y-%m-%d").date()
        period_usage_pct = Decimal(df.loc[0, "period_usage_pct"])
        total_cost = Decimal(df.loc[0, "total_cost"])
        tax_rel_cost = df.loc[0, "tax_rel_cost"]
        tax_rel_cost = total_cost if pd.isnull(tax_rel_cost) else Decimal(tax_rel_cost)
        paid_date = None if pd.isnull(df.loc[0, "paid_date"]) \
            else datetime.datetime.strptime(df.loc[0, "paid_date"], "%Y-%m-%d").date()
        notes = None if pd.isnull(df.loc[0, "notes"]) else df.loc[0, "notes"]

        dbd = DepreciationBillData.objects.full_constructor(
            real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost, real_property_value,
            period_usage_pct, paid_date=paid_date, notes=notes, bill_file=file, create=False)

        return dbd

    @classmethod
    def set_default_tax_related_cost(cls, bill_tax_related_cost_list):
        bill_list = []
        for bill, tax_related_cost in bill_tax_related_cost_list:
            # depreciation is always a tax related cost so default tax related cost is always total cost. no need to
            # consider whether bills for the real estate in bill are typically tax related or not
            bill.tax_rel_cost = bill.total_cost if tax_related_cost.is_nan() else tax_related_cost
            bill_list.append(bill)
        return bill_list

    @classmethod
    def valid_providers(cls):
        """ Which service providers are valid for this model

        Returns:
            list[ServiceProviderEnum]: [ServiceProviderEnum.DEP_DEP]
        """
        return [ServiceProviderEnum.DEP_DEP]
