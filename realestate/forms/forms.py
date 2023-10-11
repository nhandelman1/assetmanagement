import datetime

from django import forms

from ..models import ComplexServiceBillDataBase, DepreciationBillData, RealEstate, ServiceProvider, \
    SimpleServiceBillDataBase, SolarBillData


class ComplexServiceBillEstimateInputForm(forms.Form):
    real_estate = forms.ModelChoiceField(RealEstate.objects.all(), empty_label=None)
    service_provider = forms.ModelChoiceField(ServiceProvider.objects.all(), empty_label=None)
    start_date = forms.DateField()
    end_date = forms.DateField()
    allow_create = forms.BooleanField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "real_estate" in self.initial:
            self.fields["real_estate"].queryset = RealEstate.objects.filter(pk=self.initial["real_estate"].pk)
        if "service_provider" in self.initial:
            self.fields["service_provider"].queryset = \
                ServiceProvider.objects.filter(pk=self.initial["service_provider"].pk)
        self.fields["start_date"].widget.attrs['readonly'] = True
        self.fields["end_date"].widget.attrs['readonly'] = True


class ElectricBillEstimateInputForm(ComplexServiceBillEstimateInputForm):
    electric_heater_kwh = forms.IntegerField(min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["electric_heater_kwh"].widget.attrs['style'] = 'background-color: yellow'


class NatGasBillEstimateInputForm(ComplexServiceBillEstimateInputForm):
    saved_therms = forms.IntegerField(min_value=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["saved_therms"].widget.attrs['style'] = 'background-color: yellow'


class SolarBillInputFirstForm(forms.Form):
    real_estate = forms.ModelChoiceField(RealEstate.objects.all(), empty_label=None)
    service_provider = forms.ModelChoiceField(
        ServiceProvider.objects.filter(provider__in=SolarBillData.valid_providers()), empty_label=None)
    start_date = forms.DateField()
    end_date = forms.DateField()
    hourly_usage_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_date"].widget = forms.SelectDateWidget()
        self.fields["end_date"].widget = forms.SelectDateWidget()


class UploadFileForm(forms.Form):
    file = forms.FileField()


class UtilityDataSelectForm(forms.Form):
    class MonthYearSelectWidget(forms.SelectDateWidget):
        def get_context(self, name, value, attrs):
            context = super().get_context(name, value, attrs)
            for d in context["widget"]["subwidgets"]:
                if d["name"] == "month_year_day":
                    d["is_hidden"] = True
                    d["attrs"]["hidden"] = True
                    break
            return context

    real_estate = forms.ModelChoiceField(RealEstate.objects.all(), empty_label=None)
    service_provider = forms.ModelChoiceField(None, empty_label=None)
    month_year = forms.DateField(initial=datetime.date.today())

    def __init__(self, *args, **kwargs):
        utility_bill_data_model = kwargs.pop("utility_bill_data_model", None)
        if utility_bill_data_model is None or not issubclass(utility_bill_data_model, ComplexServiceBillDataBase):
            raise ValueError("kwargs must have keyword utility_bill_data_model. value must be a type that is a "
                             "subclass of ComplexServiceBillDataBase model")

        super().__init__(*args, **kwargs)

        self.fields["month_year"].widget = UtilityDataSelectForm.MonthYearSelectWidget(
            years=range(2000, datetime.date.today().year + 1))
        self.fields["month_year"].widget.is_required = True
        self.fields["service_provider"].queryset = ServiceProvider.objects.filter(
            provider__in=utility_bill_data_model.valid_providers())


class DepreciationBillSelectForm(forms.Form):
    real_estate = forms.ModelChoiceField(RealEstate.objects.all(), empty_label=None)
    service_provider = forms.ModelChoiceField(
        ServiceProvider.objects.filter(provider__in=DepreciationBillData.valid_providers()), empty_label=None)
    year = forms.IntegerField(min_value=2000, max_value=2100)


class ComplexServiceBillEstimateSelectForm(forms.Form):
    real_estate = forms.ModelChoiceField(RealEstate.objects.all(), empty_label=None)
    service_provider = forms.ModelChoiceField(None, empty_label=None)
    start_date = forms.DateField(widget=forms.SelectDateWidget())

    def __init__(self, *args, **kwargs):
        utility_bill_data_model = kwargs.pop("utility_bill_data_model", None)
        if utility_bill_data_model is None or not issubclass(utility_bill_data_model, ComplexServiceBillDataBase):
            raise ValueError("kwargs must have keyword utility_bill_data_model. value must be a type that is a "
                             "subclass of ComplexServiceBillDataBase model")

        super().__init__(*args, **kwargs)

        self.fields["service_provider"].queryset = ServiceProvider.objects.filter(
            provider__in=utility_bill_data_model.valid_providers())


class SimpleServiceBillPartialSelectForm(forms.Form):
    load_from_real_estate = forms.ModelChoiceField(RealEstate.objects.all())
    create_for_real_estate = forms.ModelChoiceField(RealEstate.objects.all())
    service_provider = forms.ModelChoiceField(None)
    paid_year = forms.IntegerField(min_value=2000, max_value=2100)

    def __init__(self, *args, **kwargs):
        utility_bill_data_model = kwargs.pop("utility_bill_data_model", None)
        if utility_bill_data_model is None or not issubclass(utility_bill_data_model, SimpleServiceBillDataBase):
            raise ValueError("kwargs must have keyword utility_bill_data_model. value must be a type that is a "
                             "subclass of SimpleServiceBillDataBase model")

        super().__init__(*args, **kwargs)

        self.fields["service_provider"].queryset = ServiceProvider.objects.filter(
            provider__in=utility_bill_data_model.valid_providers())


class ComplexServiceBillPartialSelectForm(SimpleServiceBillPartialSelectForm):
    is_actual_bill = forms.BooleanField(initial=True)

    def __init__(self, *args, **kwargs):
        utility_bill_data_model = kwargs.get("utility_bill_data_model", None)
        if utility_bill_data_model is None or not issubclass(utility_bill_data_model, ComplexServiceBillDataBase):
            raise ValueError("kwargs must have keyword utility_bill_data_model. value must be a type that is a "
                             "subclass of ComplexServiceBillDataBase model")

        super().__init__(*args, **kwargs)