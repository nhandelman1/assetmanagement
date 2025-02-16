from decimal import Decimal
from typing import Union
import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
import django.core.files.base
from django.db import models
import pandas as pd

from .realestate import Address, RealEstate
from .serviceprovider import ServiceProvider, ServiceProviderEnum
from .simpleservicebilldatabase import SimpleServiceBillDataBase


class SimpleBillDataManager(models.Manager):

    def default_constructor(self):
        """ Instantiate (but don't create) SimpleBillData instance with None for all attributes

        Returns:
            SimpleBillData: instance
        """
        return self.full_constructor(None, None, None, None, None, None, create=False)

    def full_constructor(self, real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost,
                         paid_date=None, notes=None, bill_file=None, create=True):
        """ Instantiate SimpleBillData instance with option to save to database

        Args:
            see SimpleBillData class docstring
            create (bool): False to create instance only. Default True to also save to database (self.create)

        Returns:
            SimpleBillData: instance
        """
        return (self.create if create else SimpleBillData)(
            real_estate=real_estate, service_provider=service_provider, start_date=start_date, end_date=end_date,
            total_cost=total_cost, tax_rel_cost=tax_rel_cost, paid_date=paid_date, notes=notes, bill_file=bill_file)


class SimpleBillData(SimpleServiceBillDataBase):
    """ Simple implementation of SimpleServiceBillDataBase

    Attributes:
        see superclass docstring
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["real_estate", "service_provider", "start_date", "total_cost"],
                                    name="unique_%(app_label)s_%(class)s_re_sp_sd_tc")
        ]
        ordering = ["real_estate", "start_date", "end_date"]

    # noinspection PyMethodParameters
    def file_upload_path(instance, filename):
        return "files/input/simple/" + filename

    # noinspection PyMethodParameters
    def validate_service_provider(service_provider):
        service_provider = ServiceProvider.objects.get(pk=service_provider)
        if service_provider.provider not in SimpleBillData.valid_providers():
            raise ValidationError(str(service_provider) + " is not a valid service provider")

    # noinspection PyMethodParameters
    def valid_service_providers():
        return {"provider__in": SimpleBillData.valid_providers()}

    service_provider = models.ForeignKey(ServiceProvider, models.PROTECT, validators=[validate_service_provider],
                                         limit_choices_to=valid_service_providers)
    bill_file = models.FileField(blank=True, null=True, upload_to=file_upload_path)

    objects = SimpleBillDataManager()

    def modify(self, cost_ratio=None, real_estate=None, **kwargs):
        return super().modify(cost_ratio=cost_ratio, real_estate=real_estate, **kwargs)

    def tax_related_cost_message(self):
        return self.tax_related_cost_message_helper("Simple", "total cost", "0")

    @classmethod
    def process_service_bill(cls, file):
        """ Open, process and return simple service bill in same format as SimpleServiceBillTemplate.csv

        See SimpleServiceBillTemplate.csv in media directory /files/input/simple/
            address: valid values found in model realestate.Address values
            provider: see self.valid_providers() then model serviceprovider.ServiceProviderEnum for valid values
            dates: YYYY-MM-DD format
            total cost: *.XX format
            tax related cost: *.XX format

        Args:
            file (Union[str, django.core.files.base.File]): name of file in media directory /files/input/simple/ or a
                File object.

        Returns:
            SimpleBillData: all attributes are set with bill values except paid_date, which is set to the value
            provided in the bill or None if not provided. Instance is not saved to database.

        Raises:
            ObjectDoesNotExist: if real estate or service provider not found
        """
        if isinstance(file, str):
            file = settings.MEDIA_ROOT + "/files/input/simple/" + file

        df = pd.read_csv(file)

        real_estate = RealEstate.objects.filter(address=Address.to_address(df.loc[0, "address"])).get()
        service_provider = ServiceProvider.objects.filter(provider=ServiceProviderEnum(df.loc[0, "provider"])).get()
        start_date = datetime.datetime.strptime(df.loc[0, "start_date"], "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(df.loc[0, "end_date"], "%Y-%m-%d").date()
        total_cost = Decimal(str(df.loc[0, "total_cost"]))
        try:
            tax_rel_cost = df.loc[0, "tax_rel_cost"]
            tax_rel_cost = total_cost if pd.isnull(tax_rel_cost) else Decimal(tax_rel_cost)
        except KeyError:
            tax_rel_cost = total_cost
        paid_date = df.loc[0, "paid_date"]
        paid_date = None if pd.isnull(paid_date) \
            else datetime.datetime.strptime(df.loc[0, "paid_date"], "%Y-%m-%d").date()
        notes = None if pd.isnull(df.loc[0, "notes"]) else df.loc[0, "notes"]
        ssbd = SimpleBillData.objects.full_constructor(
            real_estate, service_provider, start_date, end_date, total_cost, tax_rel_cost, paid_date=paid_date,
            notes=notes, bill_file=file, create=False)

        return ssbd

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

        SPE = ServiceProviderEnum
        Returns:
            list[ServiceProviderEnum]: [SPE.BCPH_REP, SPE.HD_SUP, SPE.HOAT_REP, SPE.KPC_CM, SPE.MS_MI, SPE.NB_INS,
                SPE.OH_INS, SPE.OC_UTI, SPE.OI_UTI, SPE.SCWA_UTI, SPE.SC_TAX, SPE.TPHS_REP, SPE.WMT_SUP,
                SPE.WL_10_APT_TEN_INC, SPE.WP_REP,  SPE.VI_UTI, SPE.YTV_UTI]
        """
        SPE = ServiceProviderEnum
        return [SPE.BCPH_REP, SPE.DC_CM, SPE.HD_SUP, SPE.HOAT_REP, SPE.KPC_CM, SPE.MTP_REP, SPE.NB_INS, SPE.OH_INS,
                SPE.OC_UTI, SPE.OI_UTI, SPE.SCWA_UTI, SPE.SC_TAX, SPE.TPHS_REP, SPE.WMT_SUP, SPE.WL_10_APT_TEN_INC,
                SPE.WP_REP, SPE.VI_UTI, SPE.YTV_UTI]
