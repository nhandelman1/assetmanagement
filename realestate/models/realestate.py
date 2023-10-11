from typing import Optional

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy


class RealEstateManager(models.Manager):
    def create_real_estate(self, address, street_num, street_name, city, state, zip_code, bill_tax_related, apt=None):
        """ See RealEstate class docstring """
        return self.create(address=address, street_num=street_num, street_name=street_name, city=city, state=state,
                           zip_code=zip_code, bill_tax_related=bill_tax_related, apt=apt)


class RealEstate(models.Model):
    """ Real estate data

    Attributes:
        address (Address): real estate address
        street_num (str): street number or id
        street_name (str): street name
        city (str): city
        state (str): 2 letter state code
        zip_code (str): 5 letter zip code
        bill_tax_related (boolean): True if bills associated with this real estate typically (but not necessarily)
            affect taxes in some way. False if they typically (but not necessarily) do not.
        apt (Optional[str]): apt name or number. Default None for no apt name or number
    """
    class Meta:
        ordering = ["address"]

    class Address(models.TextChoices):
        WAGON_LN_10 = "10 Wagon Ln Centereach NY 11720", gettext_lazy("10 Wagon Ln Centereach NY 11720")
        WAGON_LN_10_APT_1 = "10 Wagon Ln Apt 1 Centereach NY 11720", \
            gettext_lazy("10 Wagon Ln Apt 1 Centereach NY 11720")

        @staticmethod
        def to_address(str_addr):
            """ Try to match str_val to an Address using street number, street name, apt, city, state and zip code

            Args:
                str_addr (str): string address

            Returns:
                Address: that matches str_addr

            Raises:
                ValueError: if no Address matches str_addr
            """
            str_addr = str_addr.lower()
            if all([x in str_addr for x in ["10", "wagon", "centereach", "ny", "11720"]] +
                   [any([x in str_addr for x in ["ln", "la"]])]):
                return Address.WAGON_LN_10_APT_1 if "apt 1" in str_addr else Address.WAGON_LN_10
            raise ValueError("No Address matches string address: " + str_addr)

        def short_name(self):
            """ Short name for each address

            Done here to maintain some control over uniqueness of naming

            Returns:
                str: short name for self Address
            Raises
            """
            if self == Address.WAGON_LN_10:
                return "WL10"
            elif self == Address.WAGON_LN_10_APT_1:
                return "WL10A1"
            else:
                raise ValueError("No short name set for Address: " + str(self))

    address = models.CharField(max_length=70, choices=Address.choices, unique=True)
    street_num = models.CharField(max_length=10)
    street_name = models.CharField(max_length=20)
    apt = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=2, validators=[RegexValidator(r'^[A-Z]{2}$')])
    zip_code = models.CharField(max_length=5, validators=[RegexValidator(r'^[0-9]{5}$')])
    bill_tax_related = models.BooleanField()

    objects = RealEstateManager()

    def __repr__(self):
        return self.address + ", Bill Tax Related: " + str(self.bill_tax_related)

    def __str__(self):
        return self.address


Address = RealEstate.Address
