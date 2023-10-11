from django.core.exceptions import ValidationError
from django.db import models

from .realestate import RealEstate
from .serviceprovider import ServiceProvider, ServiceProviderEnum


class EstimateNote(models.Model):
    """ Estimate notes data

    Notes about data used for estimating utility bills

    Attributes:
        real_estate (RealEstate): real estate data
        service_provider (ServiceProvider):
        note_type (str):
        note (str):
        note_order (int): >= 0. the order in which the notes are intended to be displayed
    """
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["real_estate", "service_provider", "note_type"], name="unique_re_sp_nt")
        ]
        ordering = ["real_estate", "service_provider", "note_order"]

    # noinspection PyMethodParameters
    def validate_service_provider(service_provider):
        service_provider = ServiceProvider.objects.get(pk=service_provider)
        if service_provider.provider not in EstimateNote.valid_providers():
            raise ValidationError(str(service_provider) + " is not a valid service provider")

    # noinspection PyMethodParameters
    def valid_service_providers():
        return {"provider__in": EstimateNote.valid_providers()}

    real_estate = models.ForeignKey(RealEstate, models.PROTECT)
    service_provider = models.ForeignKey(ServiceProvider, models.PROTECT, validators=[validate_service_provider],
                                         limit_choices_to=valid_service_providers)
    note_type = models.CharField(max_length=20)
    note = models.TextField()
    note_order = models.PositiveSmallIntegerField()

    def __repr__(self):
        """ __str__ override

        Format:
            str(self.real_estate)
            str(self.service_provider)
            note_order, note_type, note

        Returns:
            str: as described by Format
        """
        return str(self.real_estate) + "\n" + str(self.service_provider) + "\n" + str(self.note_order) + ", " \
            + str(self.note_type) + ", " + str(self.note)

    def __str__(self):
        """ __str__ override

        Format:
            str(self.real_estate)
            str(self.service_provider)
            note_order, note_type, note

        Returns:
            str: as described by Format
        """
        return str(self.real_estate) + ", " + str(self.service_provider) + ", " + str(self.note_type) + ", " + \
            str(self.note_order)

    @classmethod
    def valid_providers(cls):
        """ Which service providers are valid for this model

        Returns:
            list[ServiceProviderEnum]: [ServiceProviderEnum.NG_UTI, ServiceProviderEnum.PSEG_UTI]
        """
        return [ServiceProviderEnum.NG_UTI, ServiceProviderEnum.PSEG_UTI]