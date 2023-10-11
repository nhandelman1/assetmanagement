from abc import abstractmethod

from django.core.exceptions import ValidationError
from django.db import models

from .realestate import RealEstate
from .serviceprovider import ServiceProvider


class UtilityDataBase(models.Model):
    """ Base class for monthly data not necessarily provided on monthly utility bill and can be found elsewhere

    Attributes:
        real_estate (RealEstate): real estate data
        service_provider (ServiceProvider):
        month_date (datetime.date): date representation for the month of this data
        year_month (str): "YYYYMM" representation for the month of this data
    """
    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(fields=["real_estate", "year_month"], name="unique_%(app_label)s_%(class)s_re_my")
        ]

    # noinspection PyMethodParameters
    @abstractmethod
    def validate_service_provider(service_provider):
        """ Validate service_provider is a valid service provider

        This is not an instance function. It could be moved to a module level function but I'm keeping it here to force
        subclasses to implement it.

        Args:
             service_provider (ServiceProvider):

        Raises:
            ValidationError: if service_provider.provider (ServiceProviderEnum) is not valid
        """
        raise NotImplementedError(
            "validate_service_provider() must be implemented by subclass and service_provider "
            "validator must be overridden.")

    # noinspection PyMethodParameters
    @abstractmethod
    def valid_service_providers():
        """ Return valid providers for subclass

        This is not an instance function. It could be moved to a module level function but I'm keeping it here to force
        subclasses to implement it.

        Returns:
            dict: {"provider__in": SubclassName.valid_providers()}
        """
        raise NotImplementedError("valid_service_providers() must be implemented by subclass and service_provider "
                                  "limit_choices_to must be overridden.")

    real_estate = models.ForeignKey(RealEstate, models.PROTECT)
    service_provider = models.ForeignKey(ServiceProvider, models.PROTECT, validators=[validate_service_provider],
                                         limit_choices_to=valid_service_providers)
    month_date = models.DateField()
    year_month = models.CharField(max_length=6)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        """ __str__ override

        Format:
            str(self.real_estate), str(self.service_provider), str(self.year_month)

        Returns:
            str: as described by Format
        """
        return str(self.real_estate) + ", " + str(self.service_provider) + ", " + str(self.year_month)

    def save(self, *args, **kwargs):
        self._validate_monthdate_monthyear()
        return super().save(*args, **kwargs)

    def _validate_monthdate_monthyear(self):
        if self.month_date.strftime("%Y%m") != self.year_month:
            raise ValidationError("year_month must have format 'YYYYMM' matching month_date year and month")