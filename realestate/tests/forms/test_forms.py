import datetime

from django import forms
from django.test import TestCase

from ...forms.forms import ComplexServiceBillEstimateInputForm, ComplexServiceBillEstimateSelectForm, \
    ComplexServiceBillPartialSelectForm, DepreciationBillSelectForm, SimpleServiceBillPartialSelectForm, \
    SolarBillInputFirstForm, UtilityDataSelectForm
from ...models.electricbilldata import ElectricBillData
from ...models.electricdata import ElectricData
from ...models.mortgagebilldata import MortgageBillData
from ...models.simplebilldata import SimpleBillData
from ..models.test_realestate import RealEstateTests
from ..models.test_serviceprovider import ServiceProviderTests


class FormTests(TestCase):

    def test_complex_service_bill_estimate_input_form(self):
        re_list = [RealEstateTests.real_estate_10wl()]
        sp_list = [ServiceProviderTests.service_provider_pseg()]
        form = ComplexServiceBillEstimateInputForm(initial={"real_estate": re_list[0], "service_provider": sp_list[0]})

        self.assertEqual(re_list, list(form.fields["real_estate"].queryset))
        self.assertEqual(sp_list, list(form.fields["service_provider"].queryset))
        for name in ["start_date", "end_date"]:
            self.assertIn("readonly", form.fields[name].widget.attrs)
            self.assertTrue(form.fields[name].widget.attrs["readonly"])

    def test_complex_service_bill_estimate_select_form(self):
        with self.assertRaises(ValueError):
            ComplexServiceBillEstimateSelectForm(utility_bill_data_model=SimpleBillData)

        form = ComplexServiceBillEstimateSelectForm(utility_bill_data_model=ElectricBillData)
        # check form has all real estate options
        self.assertEqual(self.RE_LIST, list(form.fields["real_estate"].choices.queryset))
        # check form has all ElectricBillData service provider options
        self.assertEqual(self.SP_ELECTRIC_LIST, list(form.fields["service_provider"].choices.queryset))

    def test_complex_service_bill_partial_select_form(self):
        with self.assertRaises(ValueError):
            ComplexServiceBillPartialSelectForm(utility_bill_data_model=SimpleBillData)

    def test_depreciation_bill_select_form(self):
        form = DepreciationBillSelectForm()

        # check form has all real estate options
        self.assertEqual(self.RE_LIST, list(form.fields["real_estate"].choices.queryset))
        # check form has all MortgageBillData service provider options
        self.assertEqual(self.SP_DEPRECIATION_LIST, list(form.fields["service_provider"].choices.queryset))
        # check form uses a year integer field
        self.assertIsInstance(form.fields["year"], forms.IntegerField)
        self.assertEqual(form.fields["year"].min_value, 2000)
        self.assertEqual(form.fields["year"].max_value, 2100)

    def test_simple_service_bill_partial_select_form(self):
        with self.assertRaises(ValueError):
            SimpleServiceBillPartialSelectForm(utility_bill_data_model=ElectricData)

        form = SimpleServiceBillPartialSelectForm(utility_bill_data_model=MortgageBillData)
        # check form has all real estate options
        self.assertEqual(self.RE_LIST, list(form.fields["load_from_real_estate"].choices.queryset))
        self.assertEqual(self.RE_LIST, list(form.fields["create_for_real_estate"].choices.queryset))
        # check form has all MortgageBillData service provider options
        self.assertEqual(self.SP_MORTGAGE_LIST, list(form.fields["service_provider"].choices.queryset))
        # check form uses a year integer field
        self.assertIsInstance(form.fields["paid_year"], forms.IntegerField)
        self.assertEqual(form.fields["paid_year"].min_value, 2000)
        self.assertEqual(form.fields["paid_year"].max_value, 2100)

    def test_solar_bill_input_first_form(self):
        form = SolarBillInputFirstForm()

        self.assertEqual(self.RE_LIST, list(form.fields["real_estate"].choices.queryset))
        self.assertEqual(self.SP_SOLAR_LIST, list(form.fields["service_provider"].choices.queryset))

    def test_utility_data_select_form(self):
        with self.assertRaises(ValueError):
            UtilityDataSelectForm(utility_bill_data_model=ElectricData)

        form = UtilityDataSelectForm(utility_bill_data_model=ElectricBillData)
        self.assertEqual(self.RE_LIST, list(form.fields["real_estate"].choices.queryset))
        self.assertEqual(self.SP_ELECTRIC_LIST, list(form.fields["service_provider"].choices.queryset))

        # month_year field can only show month and year
        self.assertIsInstance(form.fields["month_year"].widget, UtilityDataSelectForm.MonthYearSelectWidget)
        self.assertTrue(form.fields["month_year"].widget.is_required, True)
        self.assertEqual(form.fields["month_year"].widget.years, range(2000, datetime.date.today().year + 1))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RE_LIST = [RealEstateTests.real_estate_10wlapt1(), RealEstateTests.real_estate_10wl()]
        cls.SP_DEPRECIATION_LIST = [ServiceProviderTests.service_provider_dep()]
        cls.SP_ELECTRIC_LIST = [ServiceProviderTests.service_provider_pseg()]
        cls.SP_MORTGAGE_LIST = [ServiceProviderTests.service_provider_ms()]
        cls.SP_SOLAR_LIST = [ServiceProviderTests.service_provider_solar()]