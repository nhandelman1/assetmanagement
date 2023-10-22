from ...models.estimatenote import EstimateNote
from .test_realestate import RealEstateTests
from .test_serviceprovider import ServiceProviderTests
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class EstimateNoteTests(DjangoModelTestCaseBase):

    def equal(self, model1: EstimateNote, model2: EstimateNote):
        RealEstateTests().equal(model1.real_estate, model2.real_estate)
        ServiceProviderTests().equal(model1.service_provider, model2.service_provider)
        self.simple_equal(model1, model2, EstimateNote, rem_attr_list=["real_estate", "service_provider"])

    @staticmethod
    def estimate_note_pseg_1():
        return EstimateNote.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), note_type="first_kwh", note="test note",
            service_provider=ServiceProviderTests.service_provider_pseg(), note_order=1)[0]