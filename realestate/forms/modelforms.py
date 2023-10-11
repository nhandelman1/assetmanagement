from decimal import Decimal

from django import forms
from django.db import models

from ..models import DepreciationBillData, ElectricBillData, ElectricData, MortgageBillData, NatGasBillData, \
    NatGasData, RealEstate, RealPropertyValue, ServiceProvider, SimpleBillData, SolarBillData, UtilityDataBase


class BaseModelForm(forms.ModelForm):
    """ This form is intended to be abstract
    Forms that inherit this form will have the following attributes set in __init__:
        DateField: use SelectDateWidget
        FileField: file name will be set to the file relative path if name is missing
    """
    class Meta:
        # no model set. this is to prevent BaseModelForm from being instantiated
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.DateField):
                field.widget = forms.SelectDateWidget()
            elif isinstance(field, forms.FileField):
                # request.POST has FileField relative path as a str but wont put relative path as the name of the file
                if self.data is not None and field_name in self.data and self.instance is not None and \
                        getattr(self.instance, field_name).name is None:
                    getattr(self.instance, field_name).name = self.data[field_name]

    def make_read_only(self, edit_fields=(), disable_read_only_fields=False):
        """ Utility function to make the form read only except for specified fields

        Calling this function will have the following effects:
            Fields in edit_fields that are also required will be yellow highlighted
            ModelChoiceFields: if not in edit fields, the choices are limited to the value set in the form instance and
                the empty label is removed
            FileField, CheckboxInput: readonly does not work for these fields so they are hidden if not in edit fields,
                hidden allows them to be included in POST data
            DateField: use DateInput widget if not in edit_fields. readonly does not work for SelectDateWidget

        Args:
            edit_fields (list(str)): fields in this list are editable. Default () for no editable fields
            disable_read_only_fields: True to also disable read only fields (disabled fields won't be included in POST
                data). Default False to keep read only fields enabled.
        """
        for name, field in self.fields.items():
            if name in edit_fields:
                if field.required:
                    field.widget.attrs['style'] = 'background-color: yellow'
            else:
                if isinstance(field, forms.ModelChoiceField):
                    # setting attr readonly=True doesn't work for this field
                    field.empty_label = None
                    # TODO generalize this to work with variable number of fields
                    if name == "real_estate":
                        field.queryset = RealEstate.objects.filter(pk=self.instance.real_estate.pk)
                    elif name == "service_provider":
                        field.queryset = ServiceProvider.objects.filter(pk=self.instance.service_provider.pk)
                else:
                    if isinstance(field, (forms.FileField, forms.CheckboxInput)):
                        field.widget = forms.HiddenInput()
                    elif isinstance(field, forms.DateField):
                        field.widget = forms.DateInput()

                    field.widget.attrs['readonly'] = True

                if disable_read_only_fields:
                    field.disabled = True

    def make_editable(self, read_only_fields=(), disable_read_only_fields=False):
        """ Convenience function for make_read_only()

        Useful if caller intends for a small number of fields to be readonly
        """
        self.make_read_only(edit_fields=list(set(self.fields) - set(read_only_fields)),
                            disable_read_only_fields=disable_read_only_fields)

    @classmethod
    def formset(cls, data=None, queryset=None, files=None, edit_fields=(), read_only_fields=(),
                disable_read_only_fields=False, init_dict=None):
        """ Create a formset of consisting of forms of this class

        Args:
            data: form data
            queryset (models.QuerySet):
            files: file data
            edit_fields: see cls.make_read_only()
            read_only_fields: see cls.make_editable(). only applied if edit_fields is empty
            disable_read_only_fields: see cls.make_read_only(). only applied if at least one of edit_fields or
                read_only_fields is not empty
            init_dict (dict): initialize field (key) with value in this dict for all forms in this formset

        Returns:
            models.BaseModelFormSet: subclass of this class

        Raises:
            ValueError: if both data and queryset are None
        """
        if init_dict is None:
            init_dict = {}

        FormSet = forms.modelformset_factory(cls.Meta.model, exclude=[], extra=0, form=cls)

        if data is not None:
            formset = FormSet(data=data, files=files)
        elif queryset is not None:
            formset = FormSet(queryset=queryset, files=files)
        else:
            raise ValueError("At least one of data or queryset must not be None")

        if len(edit_fields) > 0:
            for form in formset:
                form.make_read_only(edit_fields=edit_fields, disable_read_only_fields=disable_read_only_fields)
        elif len(read_only_fields) > 0:
            for form in formset:
                form.make_editable(read_only_fields=edit_fields, disable_read_only_fields=disable_read_only_fields)

        for name, init_value in init_dict.items():
            for form in formset:
                form.fields[name].initial = init_value

        return formset


class DepreciationBillForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = DepreciationBillData

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["period_usage_pct"].min_value = Decimal("0")
        self.fields["period_usage_pct"].max_value = Decimal("100")

    def make_read_only(self, edit_fields=(), disable_read_only_fields=False):
        super().make_read_only(edit_fields=edit_fields, disable_read_only_fields=disable_read_only_fields)

        if "real_property_value" not in edit_fields:
            self.fields["real_property_value"].queryset = RealPropertyValue.objects.filter(
                pk=self.instance.real_property_value.pk)


class ElectricBillForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = ElectricBillData


class MortgageBillForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = MortgageBillData


class NatGasBillForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = NatGasBillData


class SimpleBillForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = SimpleBillData


class SolarBillForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = SolarBillData

    hourly_usage_file = forms.FileField(required=False)


class SimpleServiceBillPartialInputRatioForm(BaseModelForm):
    create_for_real_estate = forms.ModelChoiceField(RealEstate.objects.all(), widget=forms.HiddenInput())
    bill_ratio = forms.DecimalField(min_value=0, max_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.make_read_only(edit_fields=["bill_ratio", "create_for_real_estate"], disable_read_only_fields=True)


class ElectricBillPartialInputRatioForm(SimpleServiceBillPartialInputRatioForm):
    class Meta(BaseModelForm.Meta):
        model = ElectricBillData


class MortgageBillPartialInputRatioForm(SimpleServiceBillPartialInputRatioForm):
    class Meta(BaseModelForm.Meta):
        model = MortgageBillData


class NatGasBillPartialInputRatioForm(SimpleServiceBillPartialInputRatioForm):
    class Meta(BaseModelForm.Meta):
        model = NatGasBillData


class SimpleBillPartialInputRatioForm(SimpleServiceBillPartialInputRatioForm):
    class Meta(BaseModelForm.Meta):
        model = SimpleBillData


class UtilityDataForm(BaseModelForm):
    class Meta(BaseModelForm.Meta):
        model = UtilityDataBase

    def __init__(self, *args, **kwargs):
        estimate_note_query_set = kwargs.pop("estimate_note_query_set", [])
        super().__init__(*args, **kwargs)
        for estimate_note in estimate_note_query_set:
            if estimate_note.note_type in self.fields:
                self.fields[estimate_note.note_type].help_text = estimate_note.note


class ElectricDataForm(UtilityDataForm):
    class Meta(UtilityDataForm.Meta):
        model = ElectricData


class NatGasDataForm(UtilityDataForm):
    class Meta(UtilityDataForm.Meta):
        model = NatGasData
