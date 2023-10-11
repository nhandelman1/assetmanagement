from decimal import Decimal
from typing import Optional
import datetime

from django.core.exceptions import ValidationError
from django.db import models

from .serviceprovider import ServiceProvider
from .utilitydatabase import UtilityDataBase


class ElectricDataManager(models.Manager):

    def default_constructor(self):
        """ Instantiate (but don't create) ElectricData instance with None for all attributes

        Returns:
            ElectricData: instance
        """
        return self.full_constructor(
            None, None, None, None, None, None, None, mfc_rate=None, psc_rate=None, der_rate=None, dsa_rate=None,
            rda_rate=None, nysa_rate=None, rbp_rate=None, spta_rate=None, create=False)

    def full_constructor(self, real_estate, service_provider, month_date, year_month, first_kwh, first_rate, next_rate,
                         mfc_rate=None, psc_rate=None, der_rate=None, dsa_rate=None, rda_rate=None, nysa_rate=None,
                         rbp_rate=None, spta_rate=None, create=True):
        """ Instantiate ElectricData instance with option to save to database

        Args:
            see ElectricData class docstring
            create (bool): False to create instance only. Default True to also save to database (self.create)

        Returns:
            ElectricData: instance
        """
        return (self.create if create else ElectricData)(
            real_estate=real_estate, service_provider=service_provider, month_date=month_date, year_month=year_month,
            first_kwh=first_kwh, first_rate=first_rate, next_rate=next_rate, mfc_rate=mfc_rate, psc_rate=psc_rate,
            der_rate=der_rate, dsa_rate=dsa_rate, rda_rate=rda_rate, nysa_rate=nysa_rate, rbp_rate=rbp_rate,
            spta_rate=spta_rate)

    def str_dict_constructor(self, str_dict):
        """ Instantiate (but don't create) ElectricData instance using str args converted to correct data type

        Args:
            str_dict (dict): dict with instance variables (str keys) and str values. month_date str format must be
                YYYY-MM-DD. real_estate key must have value RealEstate instance. service_provider key must have value
                ServiceProvider instance

        Returns:
            ElectricData: instance
        """
        return self.full_constructor(
            str_dict["real_estate"], str_dict["service_provider"],
            datetime.datetime.strptime(str_dict["month_date"], "%Y-%m-%d").date(), str_dict["year_month"],
            int(str_dict["first_kwh"]), Decimal(str_dict["first_rate"]), Decimal(str_dict["next_rate"]),
            mfc_rate=self.dec_none(str_dict["mfc_rate"]), psc_rate=self.dec_none(str_dict["psc_rate"]),
            der_rate=self.dec_none(str_dict["der_rate"]), dsa_rate=self.dec_none(str_dict["dsa_rate"]),
            rda_rate=self.dec_none(str_dict["rda_rate"]), nysa_rate=self.dec_none(str_dict["nysa_rate"]),
            rbp_rate=self.dec_none(str_dict["rbp_rate"]), spta_rate=self.dec_none(str_dict["spta_rate"]), create=False)

    @staticmethod
    def dec_none(val):
        return None if val is None else Decimal(val)


class ElectricData(UtilityDataBase):
    """ Monthly data not necessarily provided on monthly electric bill and can be found elsewhere

    Attributes:
        see super class docstring
        first_kwh (int): max kwh used at first rate. will not be in bill if none used
        first_rate (Decimal): first rate. will not be in bill if none used
        next_rate (Decimal): next rate. will not be in bill if none used
        mfc_rate (Optional[Decimal]): merchant function charge rate. Default None
        psc_rate (Optional[Decimal]): power supply charge rate. Default None
        der_rate (Optional[Decimal]): distributed energy resources charge rate. Default None
        dsa_rate (Optional[Decimal]): delivery service adjustment cost. Default None
        rda_rate (Optional[Decimal]): revenue decoupling adjustment rate. Default None
        nysa_rate (Optional[Decimal]): new york state assessment rate. Default None
        rbp_rate (Optional[Decimal]): revenue based pilots rate. Default None
        spta_rate (Optional[Decimal]): suffolk property tax adjustment rate. Default None
    """
    class Meta(UtilityDataBase.Meta):
        ordering = ["real_estate", "year_month"]

    # noinspection PyMethodParameters
    def validate_service_provider(service_provider):
        from .electricbilldata import ElectricBillData  # avoid circular import
        service_provider = ServiceProvider.objects.get(pk=service_provider)
        if service_provider.provider not in ElectricBillData.valid_providers():
            raise ValidationError(str(service_provider) + " is not a valid service provider")

    # noinspection PyMethodParameters
    def valid_service_providers():
        from .electricbilldata import ElectricBillData
        return {"provider__in": ElectricBillData.valid_providers()}

    service_provider = models.ForeignKey(ServiceProvider, models.PROTECT, validators=[validate_service_provider],
                                         limit_choices_to=valid_service_providers)
    first_kwh = models.PositiveSmallIntegerField()
    first_rate = models.DecimalField(max_digits=5, decimal_places=4)
    next_rate = models.DecimalField(max_digits=5, decimal_places=4)
    mfc_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    psc_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    der_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    dsa_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    rda_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    nysa_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    rbp_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    spta_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)

    objects = ElectricDataManager()

    def __repr__(self):
        """ __repr__ override

        Format:
            super().__repr__()
            Delivery & System Charges:
              First: KWH: self.first_kwh, Rate: self.first_rate/kwh
              Next: Rate: self.next_rate/kwh
              Merchant Function Charge: Rate: self.mfc_rate/kwh
            Power Supply Charges:
              Power Supply: Rate: self.psc_rate/kwh
            Taxes & Other Charges: Total Cost: self.toc_total_cost
              Distributed Energy Resources: Rate: self.der_cost/kwh
              Delivery Service Adjustment: Rate: self.dsa_rate
              Revenue Decoupling Adjustment: Rate: self.rda_rate
              New York State Assessment: Rate: self.nysa_rate
              Revenue Based Pilots: Rate: self.rbp_rate
              Suffolk Property Tax Adjustment: Rate: self.spta_rate

        Returns:
            str: as described by Format
        """
        return super().__repr__() + \
            "\nDelivery & System Charges:" + \
            "\n  First: KWH: " + str(self.first_kwh) + ", Rate: " + str(self.first_rate) + "/kwh" + \
            "\n  Next: Rate: " + str(self.next_rate) + "/kwh" + \
            "\n  Merchant Function Charge: Rate: " + str(self.mfc_rate) + "/kwh" + \
            "\nPower Supply Charges: " + \
            "\n  Power Supply: Rate: " + str(self.psc_rate) + "/kwh" + \
            "\nTaxes & Other Charges:" + \
            "\n  Distributed Energy Resources: Rate: " + str(self.der_rate) + "/kwh" + \
            "\n  Delivery Service Adjustment: Rate: " + str(self.dsa_rate) + \
            "\n  Revenue Decoupling Adjustment: Rate: " + str(self.rda_rate) + \
            "\n  New York State Assessment: Rate: " + str(self.nysa_rate) + \
            "\n  Revenue Based Pilots: Rate: " + str(self.rbp_rate) + \
            "\n  Suffolk Property Tax Adjustment: Rate: " + str(self.spta_rate)