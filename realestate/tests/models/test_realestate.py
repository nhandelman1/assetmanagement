from ...models.realestate import RealEstate
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class RealEstateTests(DjangoModelTestCaseBase):

    def equal(self, model1: RealEstate, model2: RealEstate):
        self.simple_equal(model1, model2, RealEstate)

    def test_to_address(self):
        address = RealEstate.Address.to_address("10 Wagon Ln Centereach NY 11720")
        self.assertEqual(address, RealEstate.Address.WAGON_LN_10)

        address = RealEstate.Address.to_address("10 Wagon Ln Apt 1 Centereach NY 11720")
        self.assertEqual(address, RealEstate.Address.WAGON_LN_10_APT_1)

        with self.assertRaises(ValueError):
            RealEstate.Address.to_address("test address")

    @staticmethod
    def real_estate_10wl():
        return RealEstate.objects.get_or_create(
            address=RealEstate.Address.WAGON_LN_10, street_num="10", street_name="Wagon Ln", city="Centereach",
            state="NY", zip_code="11720", bill_tax_related=True, apt=None)[0]

    @staticmethod
    def real_estate_10wlapt1():
        return RealEstate.objects.get_or_create(
            address=RealEstate.Address.WAGON_LN_10_APT_1, street_num="10", street_name="Wagon Ln", city="Centereach",
            state="NY", zip_code="11720", bill_tax_related=True, apt="Apt 1")[0]