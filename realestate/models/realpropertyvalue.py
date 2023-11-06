from django.db import models
from django.utils.translation import gettext_lazy

from .realestate import RealEstate


class RealPropertyValueManager(models.Manager):
    def create_real_property_value(self, real_estate, item, purchase_date, cost_basis, dep_class, disposal_date=None,
                                    notes=None):
        """ See RealPropertyValue class docstring """
        return self.create(real_estate=real_estate, item=item, purchase_date=purchase_date, cost_basis=cost_basis,
                           dep_class=dep_class, disposal_date=disposal_date, notes=notes)


class RealPropertyValue(models.Model):
    """ Real property values data

    Initially used for home improvement related data but could be others. Might need to generalize this concept.

    Attributes:
        real_estate (RealEstate): real estate data
        item (str): real property item (e.g. House, Roof, etc.)
        purchase_date (datetime.date): date of item purchase
        cost_basis (Decimal): cost basis of item
        dep_class (DepClass): depreciation class
        disposal_date (Optional[datetime.date]): date of disposal of item. Default None for not disposed
        notes (Optional[str]): any notes associated with this item. Default None for no notes
    """
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["real_estate", "item", "purchase_date"], name="unique_re_item_pd")
        ]
        ordering = ["real_estate", "item"]

    class DepClass(models.TextChoices):
        """ Depreciation Class

        Enum value naming convention (**REQUIRED**, convention assumed by users of this class):
            system-propertyclass-method-convention
        """
        NONE = "None-None-None-None", gettext_lazy("None-None-None-None")
        GDS_RRP_SL_MM = "GDS-RRP-SL-MM", gettext_lazy("GDS-RRP-SL-MM")
        GDS_YEAR5_SL_HY = "GDS-YEAR5-SL-HY", gettext_lazy("GDS-YEAR5-SL-HY")

    real_estate = models.ForeignKey(RealEstate, models.PROTECT)
    item = models.CharField(max_length=100)
    purchase_date = models.DateField()
    disposal_date = models.DateField(blank=True, null=True)
    cost_basis = models.DecimalField(max_digits=11, decimal_places=2)
    dep_class = models.CharField(max_length=100, choices=DepClass.choices)
    notes = models.TextField(blank=True, null=True)

    objects = RealPropertyValueManager()

    def __repr__(self):
        return self.real_estate.address + "\n" + self.item + ", Depreciation Class: " + self.dep_class \
            + "\nPurchase Date: " + str(self.purchase_date) + ", Disposal Date: " + str(self.disposal_date) \
            + "\nCost Basis: " + str(self.cost_basis) + "\nNotes: " + str(self.notes)

    def __str__(self):
        return self.real_estate.address + ", " + self.item + ", " + str(self.purchase_date)


DepClass = RealPropertyValue.DepClass
