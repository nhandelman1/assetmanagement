from django.db import models
from django.utils.translation import gettext_lazy


class ServiceProviderManager(models.Manager):
    def create_service_provider(self, provider, tax_category):
        """ See ServiceProvider class docstring """
        return self.create(provider=provider, tax_category=tax_category)


class ServiceProvider(models.Model):
    """ Service provider data

    Attributes:
        provider (ServiceProviderEnum):
        tax_category (TaxCategory):
    """
    class Meta:
        ordering = ["provider"]

    class ServiceProviderEnum(models.TextChoices):
        """
        Appending tax category is not required and should not be assumed by any users of this class
        """
        BCPH_REP = "BigCityPlumbingHeating-REP", gettext_lazy("BigCityPlumbingHeating-REP")
        DC_CM = "DiscountCesspool-CM", gettext_lazy("DiscountCesspool-CM")
        DEP_DEP = "Depreciation-DEP", gettext_lazy("Depreciation-DEP")
        HD_SUP = "HomeDepot-SUP", gettext_lazy("HomeDepot-SUP")
        HOAT_REP = "HandymenOfAllTrades-REP", gettext_lazy("HandymenOfAllTrades-REP")
        KPC_CM = "KnockoutPestControl-CM", gettext_lazy("KnockoutPestControl-CM")
        MS_MI = "MorganStanley-MI", gettext_lazy("MorganStanley-MI")
        MTP_REP = "MikeThePlumber-REP", gettext_lazy("MikeThePlumber-REP")
        NB_INS = "NarragansettBay-INS", gettext_lazy("NarragansettBay-INS")
        NG_UTI = "NationalGrid-UTI", gettext_lazy("NationalGrid-UTI")
        NH = "NicholasHandelman", gettext_lazy("NicholasHandelman")
        OH_INS = "OceanHarbor-INS", gettext_lazy("OceanHarbor-INS")
        OC_UTI = "OptimumCable-UTI", gettext_lazy("OptimumCable-UTI")
        OI_UTI = "OptimumInternet-UTI", gettext_lazy("OptimumInternet-UTI")
        PSEG_UTI = "PSEG-UTI", gettext_lazy("PSEG-UTI")
        SCWA_UTI = "SCWA-UTI", gettext_lazy("SCWA-UTI")
        SC_TAX = "SuffolkCounty-TAX", gettext_lazy("SuffolkCounty-TAX")
        TPHS_REP = "TaylorProsHomeServices-REP", gettext_lazy("TaylorProsHomeServices-REP")
        WMT_SUP = "Walmart-SUP", gettext_lazy("Walmart-SUP")
        WL_10_APT_TEN_INC = "10WagonLnAptTenant-INC", gettext_lazy("10WagonLnAptTenant-INC")
        WL_10_SP = "10WagonLnSunpower", gettext_lazy("10WagonLnSunpower")
        WP_REP = "WolfPlumbing-REP", gettext_lazy("WolfPlumbing-REP")
        VI_UTI = "VerizonInternet-UTI", gettext_lazy("VerizonInternet-UTI")
        YTV_UTI = "YoutubeTV-UTI", gettext_lazy("YoutubeTV-UTI")

    class TaxCategory(models.TextChoices):
        DEP = "Depreciation", gettext_lazy("Depreciation")
        CM = "CleaningMaintenance", gettext_lazy("CleaningMaintenance")
        INC = "Income", gettext_lazy("Income")
        INS = "Insurance", gettext_lazy("Insurance")
        MI = "MortgageInterest", gettext_lazy("MortgageInterest")
        NONE = "None", gettext_lazy("None")
        REP = "Repairs", gettext_lazy("Repairs")
        SUP = "Supplies", gettext_lazy("Supplies")
        TAX = "Taxes", gettext_lazy("Taxes")
        UTI = "Utilities", gettext_lazy("Utilities")

    provider = models.CharField(max_length=100, choices=ServiceProviderEnum.choices, unique=True)
    tax_category = models.CharField(max_length=100, choices=TaxCategory.choices)

    objects = ServiceProviderManager()

    def __repr__(self):
        return "Provider: " + self.provider + ", Tax Category: " + self.tax_category

    def __str__(self):
        return self.provider


ServiceProviderEnum = ServiceProvider.ServiceProviderEnum
TaxCategory = ServiceProvider.TaxCategory
