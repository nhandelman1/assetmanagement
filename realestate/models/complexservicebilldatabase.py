from abc import abstractmethod

from django.db import models

from .simpleservicebilldatabase import SimpleServiceBillDataBase
from .utilitydatabase import UtilityDataBase


class ComplexServiceBillDataBase(SimpleServiceBillDataBase):
    """ Base class for complex data provided on service bill or relevant to service bill

    Complex data includes simple service data and an indicator of whether the service is actual or estimated. Complex
    data can also include more specific data used in calculating the total cost of the bill. This class is intended to
    be subclassed by specific forms of service (e.g. electric service) that include an estimation component and may or
    may not have subclass specific data fields.

    Attributes:
        see superclass docstring
        is_actual (boolean): is this data from an actual bill (True) or estimated (False)
    """
    class Meta:
        abstract = True

    is_actual = models.BooleanField()

    def __repr__(self):
        return super().__repr__() + ", Actual: " + str(self.is_actual)

    def __str__(self):
        return super().__str__() + ", Actual: " + str(self.is_actual)

    @abstractmethod
    def modify(self, cost_ratio=None, real_estate=None, **kwargs):
        return super().modify(cost_ratio=cost_ratio, real_estate=real_estate, **kwargs)

    @classmethod
    @abstractmethod
    def estimate_monthly_bill(cls, amb, emb, ud_start, ud_end):
        """ Run the process of estimating the complex service bill under other circumstances

         Other circumstances initially relate to solar usage but could be extended to other sources.

        Args:
            amb (ComplexServiceBillDataBase): actual bill data
            emb (ComplexServiceBillDataBase): estimated bill data
            ud_start (UtilityDataBase): utility data for the start month of the actual bill
            ud_end (UtilityDataBase): utility data for the end month of the actual bill

        Returns:
            ComplexServiceBillDataBase: estimated bill with all applicable estimate fields set
        """
        raise NotImplementedError("do_estimate_monthly_bill() not implemented by subclass")

    @classmethod
    @abstractmethod
    def initialize_complex_service_bill_estimate(cls, amb):
        """ Initialize complex service bill estimate using data from actual bill

        Args:
            amb (ComplexServiceBillDataBase):

        Returns:
            ComplexServiceBillDataBase: subclass with real_estate, provider, start_date and end_date set with same
                values as in actual bill. other values may also be set
        """
        raise NotImplementedError("initialize_monthly_bill_estimate() not implemented by subclass")