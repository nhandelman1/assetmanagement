from decimal import Decimal
import datetime

from ...models.realpropertyvalue import RealPropertyValue
from .test_realestate import RealEstateTests
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class RealPropertyValueTests(DjangoModelTestCaseBase):

    def equal(self, model1: RealPropertyValue, model2: RealPropertyValue):
        RealEstateTests().equal(model1.real_estate, model2.real_estate)
        self.simple_equal(model1, model2, RealPropertyValue, rem_attr_list=["real_estate"])

    @staticmethod
    def real_property_value_car():
        return RealPropertyValue.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wlapt1(), item="test car",
            purchase_date=datetime.date(1905, 4, 10), cost_basis=Decimal("5.64"),
            dep_class=RealPropertyValue.DepClass.GDS_YEAR5_SL_HY, disposal_date=None, notes="test notes rpv car")[0]

    @staticmethod
    def real_property_value_house():
        return RealPropertyValue.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wl(), item="House Purchase",
            purchase_date=datetime.date(2021, 7, 14), cost_basis=Decimal("84493.00"),
            dep_class=RealPropertyValue.DepClass.GDS_RRP_SL_MM, disposal_date=None, notes=None)[0]

    @staticmethod
    def real_property_value_house_apt():
        return RealPropertyValue.objects.get_or_create(
            real_estate=RealEstateTests.real_estate_10wlapt1(), item="House Purchase",
            purchase_date=datetime.date(2021, 7, 14), cost_basis=Decimal("84493.00"),
            dep_class=RealPropertyValue.DepClass.GDS_RRP_SL_MM, disposal_date=None,
            notes="purchase price and fees at 408000 + 4970 = 412970. land asmt of 150 and assessed value of 2240 so "
                  "full house is 93% of assessed value so cost basis of full house = 93% * 412970 = 384062. Apt is 22% "
                  "of full house so cost basis = 22% * 384062 = 84493")[0]