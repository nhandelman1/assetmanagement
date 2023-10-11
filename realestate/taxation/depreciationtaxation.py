from decimal import Decimal
from enum import Enum
from typing import Optional
import datetime

from django.db import models

import realestate.models.depreciationbilldata as depreciationbilldata  # circular reference if using from ... import
import realestate.models.realpropertyvalue as realpropertyvalue  # circular reference if using from ... import


class DepreciationType:

    class DepreciationSystem(Enum):
        """ Depreciation System Enum

        NONE: no system specified. functions of this class will specify how this is handled
        GDS: MACRS GDS system
        """
        NONE = "None"
        GDS = "GDS"

    class PropertyClass(Enum):
        """ Depreciation Property Class Enum

        https://www.irs.gov/publications/p946 -> Which Recovery Period Applies?

        NONE: no property class specified. functions of this class will specify how this is handled
        RRP: Residential Real Property
        YEAR5: 5 Year Property
        """
        NONE = "None"
        RRP = "RRP"
        YEAR5 = "YEAR5"

        def get_recovery_period(self, dep_sys):
            """ Get recovery period in years

            Args:
                dep_sys (DepreciationType.DepreciationSystem): recovery period for property class may depend on
                    depreciation system

            Returns:
                Decimal: recovery period in years. self NONE and dep_sys NONE return Decimal(Infinity)

            Raises:
                NotImplementedError: if recovery period not set for self and dep_sys
            """
            if dep_sys == DepreciationType.DepreciationSystem.NONE or self == self.NONE:
                return Decimal("Infinity")
            elif self == self.RRP:
                if dep_sys == DepreciationType.DepreciationSystem.GDS:
                    return Decimal("27.5")
                else:
                    raise NotImplementedError("get_recovery_period() not implemented for: " + str(dep_sys)
                                              + " - " + str(self.RRP))
            elif self == self.YEAR5:
                return Decimal(5)

    class DepreciationMethod(Enum):
        """ Depreciation Method Enum

        NONE: no method specified. functions of this class will specify how this is handled
        SL: Straight Line depreciation
        """
        NONE = "None"
        SL = "SL"

    class DepreciationConvention(Enum):
        """ Depreciation Convention Enum

        NONE: no convention specified. functions of this class will specify how this is handled
        MM: Mid-Month Convention
        FM: Full-Month Convention
        """
        NONE = "None"
        MM = "MM"
        FM = "FM"

    # aliases for convenience
    DS = DepreciationSystem
    PC = PropertyClass
    DM = DepreciationMethod
    DC = DepreciationConvention

    def __init__(self, dep_sys, prop_class, dep_method, dep_conv):
        """ init function

        Args:
            dep_sys (DepreciationType.DepreciationSystem):
            prop_class (DepreciationType.PropertyClass):
            dep_method (DepreciationType.DepreciationMethod):
            dep_conv (DepreciationType.DepreciationConvention):
        """
        self.dep_sys = dep_sys
        self.prop_class = prop_class
        self.dep_method = dep_method
        self.dep_conv = dep_conv

    def __str__(self):
        """ str function """
        return "Depreciation Type: " + self.dep_sys.value + "-" + self.prop_class.value + "-" + self.dep_method.value \
            + "-" + self.dep_conv.value

    @staticmethod
    def from_dep_class(dep_class):
        """ Create DepreciationType instance from DepClass instance

        Args:
            dep_class (realpropertyvalue.RealPropertyValue.DepClass):
                assumes enum value is a str with this format: system-propertyclass-method-convention

        Returns:
            DepreciationType: with instance variables associated with dep_class

        Raises:
            ValueError: if dep_class does not have the required enum value format
        """
        DT = DepreciationType

        try:
            lst = dep_class.split("-")
            return DepreciationType(DT.DS(lst[0]), DT.PC(lst[1]), DT.DM(lst[2]), DT.DC(lst[3]))
        except ValueError:
            raise ValueError(str(dep_class) +
                             " Enum value does not have the required format: system-propertyclass-method-convention"
                             " or does not match DepreciationType inner Enum classes.")

    def depreciation_ratio_for_tax_year(self, purchase_date, disposal_date, tax_year):
        """ Get ratio to be applied to cost basis to get depreciation for tax year

        Determined depending on instance variables. The following cases are considered:
            1. any instance variable set to its Enum class's NONE enum: Decimal(0)
            2. purchase and disposal happen in the same year: Decimal(0). no depreciation can be taken
            3. [GDS] - [Residential Real Estate, 5 Year Property] - [Straight Line] - [Mid-Month, Full-Month]:
                calculate depreciation ratio considering args. See 4.
            4. This function does not assume that depreciation was taken perfectly on schedule (i.e. property was idle
                for some period(s)). So, every year after the purchase year, through the year before the disposal year
                (if any), is assumed to be a full year of depreciation. Callers need to account for an imperfect
                depreciation schedule.

        Args:
            purchase_date (datetime.date): date of purchase of depreciation item
            disposal_date (Optional[datetime.date]): date of disposal of depreciation item or None if not disposed
            tax_year (int): tax year for which depreciation is being calculated

        Returns:
            Decimal: ratio (rounded to 9 decimal places) to be applied to cost basis to get depreciation for tax year.
                If not depreciable, Decimal(0) is returned.

        Raises:
            NotImplementedError: if this function is not implemented for an instance variable
        """
        if self.dep_sys == self.DepreciationSystem.NONE or self.prop_class == self.PropertyClass.NONE or \
                self.dep_method == self.DepreciationMethod.NONE or self.dep_conv == self.DepreciationConvention.NONE:
            return Decimal(0)
        if disposal_date is not None and (purchase_date.year == disposal_date.year or tax_year > disposal_date.year):
            return Decimal(0)

        rat_val = None

        if self.dep_sys == self.DepreciationSystem.GDS:
            if self.dep_method == self.DepreciationMethod.SL:
                year_usage_rat = None
                if self.dep_conv in (self.DepreciationConvention.MM, self.DepreciationConvention.FM):
                    # tax year is purchase year
                    if purchase_date.year == tax_year:
                        year_usage_rat = Decimal(13) - Decimal(purchase_date.month)
                        if self.dep_conv == self.DepreciationConvention.MM:
                            year_usage_rat -= Decimal("0.5")
                    # tax year is disposal year
                    elif disposal_date is not None and disposal_date.year == tax_year:
                        year_usage_rat = Decimal(disposal_date.month) - Decimal(1)
                        if self.dep_conv == self.DepreciationConvention.MM:
                            year_usage_rat += Decimal("0.5")
                    # tax year is between purchase and disposal years
                    else:
                        year_usage_rat = Decimal(12)

                    year_usage_rat /= Decimal(12)

                if year_usage_rat is not None:
                    rat_val = Decimal(1) / self.prop_class.get_recovery_period(self.dep_sys) * year_usage_rat

        if rat_val is None:
            raise NotImplementedError(str(self) + " not implemented for function depreciation_ratio_for_tax_year()")

        return round(rat_val, 9)


class DepreciationTaxation:
    """ Calculate depreciation costs depending on various criteria

    Depreciation Criteria:
        1. Cost basis
        2. Purchase date
        3. Depreciation class - https://www.irs.gov/publications/p946 -> Which Recovery Period Applies?
        4. Tax year
        5. Previously accumulated depreciation (depending on if depreciation was constantly applied or not):
            a. Constant depreciation over life: the last year will be any remaining depreciation
            b. Not constant: item was not used for either active or idle business purposes (i.e. it was used for
                personal use) at certain points throughout its life. Depreciation continues from last time item was
                used for business purposes, up to the yearly max, until no remaining depreciation can be applied
    """
    def __init__(self):
        """ init function """
        pass

    def calculate_accumulated_depreciation(self, real_property_value, tax_year):
        """ Calculate accumulated depreciation for depreciation item up to the specified tax year

        Gather depreciation bills associated with depreciation item for years before tax_year. Sum total depreciation
        costs from these bills.

        Args:
            real_property_value (realpropertyvalue.RealPropertyValue): depreciation item
            tax_year (int): calculate accumulated depreciation up to (not including) this tax year. must be a year
                before the current year

        Returns:
            Decimal: sum of accumulated depreciation for depreciation item up to specified tax year

        Raises:
            ValueError: if tax_year is greater than or equal to the current year
        """
        if tax_year >= datetime.date.today().year:
            raise ValueError(str(tax_year) + " is not a previous year. Must be a previous year.")

        total_cost = depreciationbilldata.DepreciationBillData.objects.filter(
            real_property_value=real_property_value, paid_date__lt=datetime.date(tax_year, 1, 1)).aggregate(
            total_cost=models.Sum("total_cost"))["total_cost"]

        return Decimal(0) if total_cost is None else total_cost

    def calculate_depreciation_for_year(self, real_property_value, tax_year):
        """ Calculate depreciation for depreciation item for the specified tax year assuming full period usage

        "full period" used here instead of "full year" to indicate that first, last and disposal years may be partial
        years.

        Args:
            real_property_value (realpropertyvalue.RealPropertyValue): depreciation item
            tax_year (int): calculate depreciation for this tax year. must be a year before the current year

        Returns:
            (Decimal, Decimal, Decimal): (calculated depreciation, remaining depreciation for item before this tax
                year's depreciation is applied, max possible depreciation for the year). both are for the depreciation
                item for specified tax year rounded to the nearest ones digit with round half up convention

        Raises:
            ValueError: if tax_year is greater than or equal to the current year
        """
        if tax_year >= datetime.date.today().year:
            raise ValueError(str(tax_year) + " is not a previous year. Must be a previous year.")

        dep_type = DepreciationType.from_dep_class(real_property_value.dep_class)
        accum_dep = self.calculate_accumulated_depreciation(real_property_value, tax_year)
        remain_dep = real_property_value.cost_basis - accum_dep

        # this algorithm accounts for non depreciable property, property that has been fully depreciated
        # and property that has been disposed
        year_dep_rat = dep_type.depreciation_ratio_for_tax_year(real_property_value.purchase_date,
                                                                real_property_value.disposal_date, tax_year)
        max_year_dep = real_property_value.cost_basis * year_dep_rat
        # negative depreciation doesn't exist so this check ensures year_dep is at minimum 0. should only happen
        # if there is a slight numerical issue
        year_dep = round(max(Decimal(0), min(remain_dep, max_year_dep)), 0)

        return year_dep, round(remain_dep, 0), round(max_year_dep, 0)