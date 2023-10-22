from ...models.serviceprovider import ServiceProvider
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class ServiceProviderTests(DjangoModelTestCaseBase):

    def equal(self, model1: ServiceProvider, model2: ServiceProvider):
        self.simple_equal(model1, model2, ServiceProvider)

    @staticmethod
    def service_provider_dep():
        return ServiceProvider.objects.get_or_create(
            provider=ServiceProvider.ServiceProviderEnum.DEP_DEP, tax_category=ServiceProvider.TaxCategory.DEP)[0]

    @staticmethod
    def service_provider_pseg():
        return ServiceProvider.objects.get_or_create(
            provider=ServiceProvider.ServiceProviderEnum.PSEG_UTI, tax_category=ServiceProvider.TaxCategory.UTI)[0]

    @staticmethod
    def service_provider_ms():
        return ServiceProvider.objects.get_or_create(
            provider=ServiceProvider.ServiceProviderEnum.MS_MI, tax_category=ServiceProvider.TaxCategory.MI)[0]

    @staticmethod
    def service_provider_ng():
        return ServiceProvider.objects.get_or_create(
            provider=ServiceProvider.ServiceProviderEnum.NG_UTI, tax_category=ServiceProvider.TaxCategory.UTI)[0]

    @staticmethod
    def service_provider_simple_nbins():
        return ServiceProvider.objects.get_or_create(
            provider=ServiceProvider.ServiceProviderEnum.NB_INS, tax_category=ServiceProvider.TaxCategory.INS)[0]

    @staticmethod
    def service_provider_simple_youtubetv():
        return ServiceProvider.objects.get_or_create(
            provider=ServiceProvider.ServiceProviderEnum.YTV_UTI, tax_category=ServiceProvider.TaxCategory.UTI)[0]

    @staticmethod
    def service_provider_solar():
        return ServiceProvider.objects.get_or_create(
            provider=ServiceProvider.ServiceProviderEnum.WL_10_SP, tax_category=ServiceProvider.TaxCategory.NONE)[0]