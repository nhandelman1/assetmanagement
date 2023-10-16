from decimal import Decimal
import datetime

from django import forms
from django.test import TestCase

from ...forms.modelforms import DepreciationBillForm, ElectricBillForm, ElectricBillPartialInputRatioForm, \
    ElectricDataForm, NatGasDataForm, SimpleBillForm
from ...models.electricbilldata import ElectricBillData
from ...models.electricdata import ElectricData
from ...models.estimatenote import EstimateNote
from ...models.simplebilldata import SimpleBillData
from ..models.test_depreciationbilldata import DepreciationBillDataTests
from ..models.test_electricbilldata import ElectricBillDataTests
from ..models.test_estimatenote import EstimateNoteTests
from ..models.test_realestate import RealEstateTests
from ..models.test_simplebilldata import SimpleBillDataTests


class BillFormTests(TestCase):

    def test_base_model_form_editable(self):
        bill = ElectricBillDataTests.electric_bill_data_1()
        form = ElectricBillForm(instance=bill)
        form.make_editable(read_only_fields=["service_provider", "total_cost"])

        # check that fields not in read_only_fields do not have readonly attr set to True
        # readonly shouldn't be in attrs but if it is, it can be set to False
        with self.subTest():
            if "readonly" in form.fields["tax_rel_cost"].widget.attrs:
                self.assertFalse(form.fields["tax_rel_cost"].widget.attrs["readonly"])

        with self.subTest():
            self.assertIn("readonly", form.fields["total_cost"].widget.attrs)
            self.assertTrue(form.fields["total_cost"].widget.attrs["readonly"])

    def test_base_model_form_formset(self):
        # check at least one of data and queryset is not None
        with self.subTest():
            with self.assertRaises(ValueError):
                ElectricBillForm.formset()

        pk_list = (ElectricBillDataTests.electric_bill_data_1().pk, ElectricBillDataTests.electric_bill_data_2().pk,
                   ElectricBillDataTests.electric_bill_data_3().pk)

        # check total cost is editable and not disabled (i.e. read_only_fields is not applied)
        # check any other field is readonly and disabled
        formset = ElectricBillForm.formset(
            queryset=ElectricBillData.objects.filter(pk__in=pk_list), edit_fields=["total_cost"],
            read_only_fields=["total_cost"], disable_read_only_fields=True)
        with self.subTest():
            for form in formset:
                if "readonly" in form.fields["total_cost"].widget.attrs:
                    self.assertFalse(form.fields["total_cost"].widget.attrs["readonly"])
                self.assertFalse(form.fields["total_cost"].disabled)
                self.assertIn("readonly", form.fields["tax_rel_cost"].widget.attrs)
                self.assertTrue(form.fields["tax_rel_cost"].widget.attrs["readonly"])
                self.assertTrue(form.fields["tax_rel_cost"].disabled)

        # check total cost is read only and disabled and check any other field is editable and not disabled
        formset = ElectricBillForm.formset(
            queryset=ElectricBillData.objects.filter(pk__in=pk_list), read_only_fields=["total_cost"],
            disable_read_only_fields=True)
        with self.subTest():
            for form in formset:
                self.assertIn("readonly", form.fields["total_cost"].widget.attrs)
                self.assertTrue(form.fields["total_cost"].widget.attrs["readonly"])
                self.assertTrue(form.fields["total_cost"].disabled)
                if "readonly" in form.fields["tax_rel_cost"].widget.attrs:
                    self.assertFalse(form.fields["tax_rel_cost"].widget.attrs["readonly"])
                self.assertFalse(form.fields["tax_rel_cost"].disabled)

        # test init_dict
        RealEstateTests.real_estate_10wl()
        re_10wlapt1 = RealEstateTests.real_estate_10wlapt1()
        formset = ElectricBillPartialInputRatioForm.formset(
            queryset=ElectricBillData.objects.filter(pk__in=pk_list), init_dict={"create_for_real_estate": re_10wlapt1})
        with self.subTest():
            for form in formset:
                self.assertEqual(form.fields["create_for_real_estate"].initial, re_10wlapt1)

        # check that data is used (queryset is ignored) when both data and queryset are passed
        pk = SimpleBillDataTests.simple_bill_data_1().pk
        post_dict = SimpleBillDataTests.simple_bill_data_post_data()
        formset = SimpleBillForm.formset(data=post_dict, queryset=SimpleBillData.objects.filter(pk=pk))

        with self.subTest():
            # if queryset were used, length would be 1
            self.assertEqual(len(formset), 2)

    def test_base_model_form_read_only(self):
        # make_read_only should throw a value error if instance is not set
        with self.subTest():
            form = ElectricBillForm()
            with self.assertRaises(ValueError):
                form.make_read_only()

        bill = ElectricBillDataTests.electric_bill_data_1()
        form = ElectricBillForm(instance=bill)
        form.fields["end_date"].required = False
        form.make_read_only(edit_fields=["service_provider", "total_cost"], disable_read_only_fields=True)

        # edit fields that are required are yellow
        with self.subTest():
            self.assertIn("style", form.fields["service_provider"].widget.attrs)
            self.assertEqual(form.fields["service_provider"].widget.attrs["style"], "background-color: yellow")

        # edit fields that are not required have no color change
        with self.subTest():
            if "style" in form.fields["end_date"].widget.attrs:
                self.assertNotIn("background-color:", form.fields["end_date"].widget.attrs["style"])

        # read only fields:
        # ModelChoiceField has no empty label and only has one object
        with self.subTest():
            self.assertIsNone(form.fields["real_estate"].empty_label)
            self.assertEqual(list(form.fields["real_estate"].queryset), [bill.real_estate])

        # FileField and BooleanField are hidden
        with self.subTest():
            self.assertIsInstance(form.fields["is_actual"].widget, forms.HiddenInput)
            self.assertIsInstance(form.fields["bill_file"].widget, forms.HiddenInput)

        # DateField has widget DateInput
        with self.subTest():
            self.assertIsInstance(form.fields["start_date"].widget, forms.DateInput)

        # edit field is not read only and not disabled
        # readonly shouldn't be in attrs but if it is, it can be set to False
        with self.subTest():
            if "readonly" in form.fields["total_cost"].widget.attrs:
                self.assertFalse(form.fields["total_cost"].widget.attrs["readonly"])
            self.assertFalse(form.fields["total_cost"].disabled)

        # field is read only and disabled
        with self.subTest():
            self.assertIn("readonly", form.fields["tax_rel_cost"].widget.attrs)
            self.assertTrue(form.fields["tax_rel_cost"].widget.attrs["readonly"])
            self.assertTrue(form.fields["tax_rel_cost"].disabled)

    def test_depreciation_bill_form(self):
        form = DepreciationBillForm()

        self.assertEqual(form.fields["period_usage_pct"].min_value, Decimal(0))
        self.assertEqual(form.fields["period_usage_pct"].max_value, Decimal(100))

        with self.assertRaises(ValueError):
            form.make_read_only()

        bill = DepreciationBillDataTests.depreciation_bill_data_1()
        form = DepreciationBillForm(instance=bill)

        form.make_read_only()

        self.assertEqual(list(form.fields["real_property_value"].queryset), [bill.real_property_value])

    def test_utility_data_form(self):
        # test that estimate notes are set correctly
        note = EstimateNoteTests.estimate_note_pseg_1()
        electric_data = ElectricData(real_estate=note.real_estate, service_provider=note.service_provider,
                                     month_date=datetime.date(2021, 1, 15), year_month="202101")

        estimate_notes = EstimateNote.objects.filter(pk=note.pk)
        form = ElectricDataForm(instance=electric_data, estimate_note_query_set=estimate_notes)

        self.assertEqual(form.fields["first_kwh"].help_text, note.note)

        # test formset is not implemented
        with self.assertRaises(NotImplementedError):
            ElectricDataForm.formset()

        with self.assertRaises(NotImplementedError):
            NatGasDataForm.formset()
