from decimal import Decimal
from typing import Optional
import datetime

from django.core.exceptions import ValidationError
from django.db import models

from .serviceprovider import ServiceProvider
from .utilitydatabase import UtilityDataBase


class NatGasDataManager(models.Manager):
    def default_constructor(self):
        """ Instantiate (but don't create) NatGasData instance with None for all attributes

        Returns:
            NatGasData: instance
        """
        return self.full_constructor(
            None, None, None, None, None, None, None, None, None, None, dra_rate=None, wna_low_rate=None,
            wna_high_rate=None, sbc_rate=None, tac_rate=None, bc_rate=None, ds_nysls_rate=None, ds_nysst_rate=None,
            ss_nysls_rate=None, ss_nysst_rate=None, pbc_rate=None, create=False)

    def full_constructor(self, real_estate, service_provider, month_date, year_month, bsc_therms, bsc_rate, next_therms,
                         next_rate, over_rate, gs_rate, dra_rate=None,  wna_low_rate=None,  wna_high_rate=None,
                         sbc_rate=None, tac_rate=None, bc_rate=None, ds_nysls_rate=None, ds_nysst_rate=None,
                         ss_nysls_rate=None, ss_nysst_rate=None, pbc_rate=None, create=True):
        """ Instantiate NatGasData instance with option to save to database

        Args:
            see NatGasData class docstring
            create (bool): False to create instance only. Default True to also save to database (self.create)

        Returns:
            NatGasData: instance
        """
        return (self.create if create else NatGasData)(
            real_estate=real_estate, service_provider=service_provider, month_date=month_date, year_month=year_month,
            bsc_therms=bsc_therms, bsc_rate=bsc_rate, next_therms=next_therms, next_rate=next_rate, over_rate=over_rate,
            gs_rate=gs_rate, dra_rate=dra_rate, wna_low_rate=wna_low_rate, wna_high_rate=wna_high_rate,
            sbc_rate=sbc_rate, tac_rate=tac_rate, bc_rate=bc_rate, ds_nysls_rate=ds_nysls_rate,
            ds_nysst_rate=ds_nysst_rate, ss_nysls_rate=ss_nysls_rate, ss_nysst_rate=ss_nysst_rate, pbc_rate=pbc_rate)

    def str_dict_constructor(self, str_dict):
        """ Instantiate (but don't create) NatGasData instance using str args converted to correct data type

        Args:
            str_dict (dict): dict with instance variables (str keys) and str values. month_date str format must be
                YYYY-MM-DD. real_estate key must have value RealEstate instance. service_provider key must have value
                ServiceProvider instance

        Returns:
            NatGasData: instance
        """
        return self.full_constructor(
            str_dict["real_estate"], str_dict["service_provider"],
            datetime.datetime.strptime(str_dict["month_date"], "%Y-%m-%d").date(), str_dict["month_year"],
            Decimal(str_dict["bsc_therms"]), Decimal(str_dict["bsc_rate"]), Decimal(str_dict["next_therms"]),
            Decimal(str_dict["next_rate"]), Decimal(str_dict["over_rate"]), Decimal(str_dict["gs_rate"]),
            dra_rate=self.dec_none(str_dict["dra_rate"]), wna_low_rate=self.dec_none(str_dict["wna_low_rate"]),
            wna_high_rate=self.dec_none(str_dict["wna_high_rate"]), sbc_rate=self.dec_none(str_dict["sbc_rate"]),
            tac_rate=self.dec_none(str_dict["tac_rate"]), bc_rate=self.dec_none(str_dict["bc_rate"]),
            ds_nysls_rate=self.dec_none(str_dict["ds_nysls_rate"]),
            ds_nysst_rate=self.dec_none(str_dict["ds_nysst_rate"]),
            ss_nysls_rate=self.dec_none(str_dict["ss_nysls_rate"]),
            ss_nysst_rate=self.dec_none(str_dict["ss_nysst_rate"]), pbc_rate=self.dec_none(str_dict["pbc_rate"]),
            create=False)

    @staticmethod
    def dec_none(val):
        return None if val is None else Decimal(val)


class NatGasData(UtilityDataBase):
    """ Monthly data not necessarily provided on monthly natural gas bill and can be found elsewhere

    Attributes:
        see super class docstring
        bsc_therms (Decimal): max therms used at basic rate
        bsc_rate (Decimal): basic service charge rate
        next_therms (Decimal): max therms used at next rate
        next_rate (Decimal): next rate.
        over_rate (Decimal): over/last rate.
        gs_rate (Decimal): gas supply rate
        dra_rate (Optional[Decimal]): delivery rate adjustment rate. Default None
        wna_low_rate (Optional[Decimal]): weather normalization adjustment rate for lower therms. Default None
        wna_high_rate (Optional[Decimal]): weather normalization adjustment rate for higher therms. Default None
        sbc_rate (Optional[Decimal]): system benefits charge. Default None
        tac_rate (Optional[Decimal]): transportation adjustment charge rate. Default None
        bc_rate (Optional[Decimal]): billing charge rate
        ds_nysls_rate (Optional[Decimal]): delivery services ny state and local surcharges rate. Default None.
        ds_nysst_rate (Optional[Decimal]): delivery services ny state sales tax. Default None
        ss_nysls_rate (Optional[Decimal]): supply services ny state and local surcharges rate. Default None.
        ss_nysst_rate (Optional[Decimal]): supply services ny state sales tax. Default None
        pbc_rate (Optional[Decimal]): paperless billing credit rate. Default None
    """
    class Meta(UtilityDataBase.Meta):
        ordering = ["real_estate", "year_month"]

    # noinspection PyMethodParameters
    def validate_service_provider(service_provider):
        from .natgasbilldata import NatGasBillData  # avoid circular import
        service_provider = ServiceProvider.objects.get(pk=service_provider)
        if service_provider.provider not in NatGasBillData.valid_providers():
            raise ValidationError(str(service_provider) + " is not a valid service provider")

    # noinspection PyMethodParameters
    def valid_service_providers():
        from .natgasbilldata import NatGasBillData  # avoid circular import
        return {"provider__in": NatGasBillData.valid_providers()}

    service_provider = models.ForeignKey(ServiceProvider, models.PROTECT, validators=[validate_service_provider],
                                         limit_choices_to=valid_service_providers)
    bsc_therms = models.DecimalField(max_digits=3, decimal_places=1)
    bsc_rate = models.DecimalField(max_digits=6, decimal_places=4)
    next_therms = models.DecimalField(max_digits=4, decimal_places=1)
    next_rate = models.DecimalField(max_digits=5, decimal_places=4)
    over_rate = models.DecimalField(max_digits=5, decimal_places=4)
    dra_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    wna_low_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    wna_high_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    sbc_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    tac_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    bc_rate = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    ds_nysls_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    ds_nysst_rate = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    gs_rate = models.DecimalField(max_digits=7, decimal_places=6)
    ss_nysls_rate = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
    ss_nysst_rate = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    pbc_rate = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    objects = NatGasDataManager()

    def __repr__(self):
        """ __repr__ override

        Format:
            super().__repr__()
            Delivery Services:
              Basic: Therms: self.bsc_therms, Rate: self.bsc_rate
              Next: Therms: self.next_therms, Rate: self.next_rate/therm
              Over: Rate: self.over_rate/therm
              Delivery Rate Adjustment: Rate: self.dra_rate/therm
              Weather Normalization Adjustment: Low Rate: self.wna_low_rate/therm, High Rate: self.wna_high_rate/therm
              System Benefits Charge: Rate: self.sbc_rate/therm
              Transportation Adjustment Charge: Rate: self.tac_rate/therm
              Billing Charge: Rate: self.bc_rate/bill
              NY State and Local Surcharges: Rate: self.ds_nysls_rate
              NY State Sales Tax: Rate: self.ds_nysst_rate
            Supply Services:
              Gas Supply: Rate: self.gs_rate/therm
              NY State and Local Surcharges: Rate: self.ss_nysls_rate
              NY State Sales Tax: Rate: self.ss_nysst_rate
            Other Charges/Adjustments:
              Paperless Billing Credit: Cost: self.pbc_rate/bill

        Returns:
            str: as described by Format
        """
        return super().__repr__() + \
            "\nDelivery Services:" + \
            "\n  Basic: Therms: " + str(self.bsc_therms) + ", Rate: " + str(self.bsc_rate) + \
            "\n  Next: Therms: " + str(self.next_therms) + ", Rate: " + str(self.next_rate) + "/therm" \
            "\n  Over: Rate: " + str(self.over_rate) + "/therm" + \
            "\n  Delivery Rate Adjustment: Rate: " + str(self.dra_rate) + "/therm" + \
            "\n  Weather Normalization Adjustment: Low Rate: " + str(self.wna_low_rate) + "/therm, High Rate: " + \
                str(self.wna_high_rate) + "/therm" + \
            "\n  System Benefits Charge: Rate: " + str(self.sbc_rate) + "/therm" + \
            "\n  Transportation Adjustment Charge: Rate: " + str(self.tac_rate) + "/therm" + \
            "\n  Billing Charge: Rate: " + str(self.bc_rate) + "/bill" + \
            "\n  NY State and Local Surcharges: Rate: " + str(self.ds_nysls_rate) + \
            "\n  NY State Sales Tax: Rate: " + str(self.ds_nysst_rate) + \
            "\nSupply Services: " + \
            "\n  Gas Supply: Rate: " + str(self.gs_rate) + "/therm" + \
            "\n  NY State and Local Surcharges: Rate: " + str(self.ss_nysls_rate) + \
            "\n  NY State Sales Tax: Rate: " + str(self.ss_nysst_rate) + \
            "\nOther Charges/Adjustments:" + \
            "\n  Paperless Billing Credit: Rate: " + str(self.pbc_rate) + "/bill"