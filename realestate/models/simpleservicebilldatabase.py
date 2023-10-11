from abc import abstractmethod
from decimal import Decimal
from typing import Optional, Union
import copy

from django.db import models

from .realestate import RealEstate
from .serviceprovider import ServiceProvider, ServiceProviderEnum


class SimpleServiceBillDataBase(models.Model):
    """ Base class for simple data provided on service bill or relevant to service bill

    Simple data is for services actually provided and includes location (real estate), provider, start date, end date,
    total cost, paid date and notes. These are service attributes that are common to all forms of service. This class is
    intended to be subclassed by specific forms of service (e.g. electric service) that may or may not be more complex.
    Note that a "service" is loosely defined and may include actual services, goods purchased or any other item that
    can loosely be considered a "service".

    Attributes:
        real_estate (RealEstate): real estate info
        service_provider (ServiceProvider): service provider
        start_date (datetime.date): bill start date
        end_date (datetime.date): bill end date
        total_cost (Decimal): total bill cost
        tax_rel_cost (Decimal): tax related cost
        paid_date (Optional[datetime.date]): date on which bill was paid (for tax purposes). Optional since bill
            data might be saved before bill is paid
        notes (Optional[str]): notes about this bill
    """

    class Meta:
        abstract = True

    # noinspection PyMethodParameters
    @abstractmethod
    def file_upload_path(instance, filename):
        """ Upload path for bill files

        This is not an instance function. It could be moved to a module level function but I'm keeping it here to force
        subclasses to implement it.
        """
        raise NotImplementedError("file_upload_path() must be implemented by subclass and bill_file upload_to must "
                                  "be overridden.")

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
        raise NotImplementedError("validate_service_provider() must be implemented by subclass and service_provider "
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
    start_date = models.DateField()
    end_date = models.DateField()
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    tax_rel_cost = models.DecimalField(max_digits=8, decimal_places=2)
    paid_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    bill_file = models.FileField(blank=True, null=True, upload_to=file_upload_path)

    def __repr__(self):
        """ __repr__ override

        Format:
            str(self.real_estate)
            str(self.service_provider)
            Start Date: str(self.start_date), End Date: str(self.end_date)
            Total Cost: str(self.total_cost), Tax Rel Cost: str(self.tax_rel_cost)
            Paid Date: str(self.paid_date)
            Notes: str(self.notes)

        Returns:
            str: as described by Format
        """
        return str(self.real_estate) + "\n" + str(self.service_provider) + "\nStart Date: " + str(self.start_date) + \
            ", EndDate: " + str(self.end_date) + "\nTotal Cost: " + str(self.total_cost) + ", Tax Related Cost: " + \
            str(self.tax_rel_cost) + "\nPaid Date: " + str(self.paid_date) + "\nNotes: " + str(self.notes)

    def __str__(self):
        return str(self.real_estate) + ", " + str(self.service_provider) + ", " + str(self.start_date) + \
            ", " + str(self.end_date) + ", " + str(self.total_cost)

    @abstractmethod
    def modify(self, cost_ratio=None, real_estate=None, **kwargs):
        """ Create and return a deep copy of this bill with args applied as described

        This function uses copy.deepcopy(self) instead of reloading self from the database, since attributes may have
        been changed without being saved to the database.
        pk of modified bill is set to None but not saved to database. Caller can save if desired
        cost_ratio applied to total_cost in this function and notes is updated indicating this. subclasses may apply
            cost_ratio to other attributes related to total_cost, typically numerical attributes, and update notes to
            indicate any changes.
        if real_estate is not None, the copy's real_estate attribute is changed to real_estate and notes is updated
            indicating this
        Neither this function nor overriding functions will guarantee that the modified bill will not cause a constraint
            violation (typically unique constraint violation) if saved to db

        Args:
            cost_ratio (Optional[Decimal]): Must be between 0 (inclusive) and 1 (exclusive). Applied to instance
                attributes as specified in this function and overriding functions in subclasses. Default None to not
                apply a cost ratio.
            real_estate (Optional[RealEstate]): replace self.real_estate with this value. Update notes to reflect the
                change. Default None to not replace
            **kwargs: specified by subclasses

        Returns:
            SimpleServiceBillDataBase: subclass instance

        Raises:
            ValueError: if cost ratio is not between 0 and 1 inclusive
        """
        bill_copy = copy.deepcopy(self)
        bill_copy.pk = None

        bill_copy.notes = "" if bill_copy.notes is None else bill_copy.notes
        bill_copy.notes += " This bill is a modification of the original bill."
        if cost_ratio is not None:
            if cost_ratio < Decimal(0) or cost_ratio >= Decimal(1):
                raise ValueError("cost ratio must be between 0 (inclusive) and 1 (exclusive)")
            bill_copy.total_cost *= cost_ratio
            bill_copy.notes += " Ratio of " + str(cost_ratio) + " applied to total cost."
        if real_estate is not None:
            bill_copy.real_estate = real_estate
            bill_copy.notes += " Real estate changed from original."
        return bill_copy

    @abstractmethod
    def tax_related_cost_message(self):
        """ Message about typical tax related cost for a bill

        Returns:
            str: message about typical tax related cost for a bill
        """
        raise NotImplementedError("tax_related_cost_message() not implemented by subclass")

    def tax_related_cost_message_helper(self, bill_type, default_tax_rel_field, default_not_tax_rel_val):
        if self.real_estate.bill_tax_related:
            print_str = bill_type + " bills associated with this real estate are typically tax related. " + \
                        "The tax rel cost field is set to " + default_tax_rel_field + ", which is the typical tax " \
                        "related cost. Another value can be set in the field."
        else:
            print_str = bill_type + " bills associated with this real estate are typically NOT tax related. " + \
                        "The tax rel cost field is set to " + default_not_tax_rel_val + ", which is the typical tax " \
                        "related cost. Another value can be set in the field."

        return print_str

    def round_fields(self):
        for field in self._meta.fields:
            if isinstance(field, models.DecimalField):
                field_val = getattr(self, field.name)
                if field_val is not None:
                    setattr(self, field.name, round(field_val, field.decimal_places))

    @classmethod
    @abstractmethod
    def process_service_bill(cls, file):
        """ Open, process and return service bill

        Args:
            file (Union[str, django.core.files.base.File]): name of file in media directory specified by subclass or a
                File object.

        Returns:
            SimpleServiceBillDataBase: subclass with all required fields populated and as many non required fields as
            available populated

        Raises:
            FileNotFoundError: if file not found
        """
        raise NotImplementedError("process_service_bill() not implemented by subclass")

    def calc_this_bill_month_year(self, threshold: int = 25):
        """ Call self.calc_bill_month_year(self.start_date, self.end_date)

        Args:
            threshold (int): 1-31. Default 25

        Returns:
            str: month year with format "YYYY-MM"
        """
        return self.calc_bill_month_year(self.start_date, self.end_date, threshold=threshold)

    @classmethod
    @abstractmethod
    def valid_providers(cls):
        """ Which service providers are valid for this model

        Returns:
            list[ServiceProviderEnum]: list of ServiceProviderEnum
        """
        raise NotImplementedError("valid_providers() not implemented by subclass")

    @classmethod
    @abstractmethod
    def set_default_tax_related_cost(cls, bill_tax_related_cost_list):
        """ Set tax_rel_cost in each bill with the provided tax related cost or use default value

        Overriding functions should do the following:
            If a number Decimal is provided, set the bill's tax_rel_cost to that value.
            If Decimal(NaN) is provided, set the bill's tax_rel_cost depending on the bill's
                real_estate.bill_tax_related value

        Args:
            bill_tax_related_cost_list (list[tuple[SimpleServiceBillDataBase, Decimal]]): sub tuples are 2-tuples where
                the first element is the bill and the second element is the tax related cost of the bill or Decimal(NaN)
                to use default tax related cost.

        Returns:
            list[SimpleServiceBillDataBase]: subclass instances. tax_rel_cost in each bill is set as described. bills
                are returned in same order as in bill_tax_related_cost_list
        """
        raise NotImplementedError("set_default_tax_related_cost() not implemented by subclass")

    @staticmethod
    def calc_bill_month_year(start_date, end_date, threshold: int = 25):
        """ Calculate bill month depending on start_date and end_date

        Args:
            start_date (datetime.date): bill start date
            end_date (datetime.date): bill end date
            threshold (int): 1-31. if start_date day is before or equal to this value, get month year from
                start_date. otherwise, get month year from end_date. Default 25

        Returns:
            str: month year with format "YYYY-MM"
        """
        return start_date.strftime("%Y-%m") if start_date.day <= threshold else end_date.strftime("%Y-%m")