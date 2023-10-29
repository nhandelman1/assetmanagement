from django import forms

from ..models.position import Position
from ..models.securitymaster import SecurityMaster


class PositionAdminForm(forms.ModelForm):
    class Meta:
        model = Position
        help_texts = {"market_value": "Value will be calculated if left blank.",
                      "cost_basis_total": "Value will be calculated if left blank."}
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['market_value'].required = False
        self.fields['cost_basis_total'].required = False

    def clean(self):
        """ Override clean to calculate market_value and cost_basis_total if not set """
        cd = super().clean()  # super returns self.cleaned_data
        for total, price in (("market_value", "close_price"), ("cost_basis_total", "cost_basis_price")):
            if cd[total] is None:
                if all([x in cd for x in ["quantity", price]]):
                    cd[total] = round(cd["quantity"] * cd[price], self.fields[total].decimal_places)

        return self.cleaned_data


class SecurityMasterAdminForm(forms.ModelForm):

    class Meta:
        model = SecurityMaster
        help_texts = {"my_id": "auto populated - not editable"}
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # my_id should not be changed by user. set readonly here so it is returned in cleaned_data
        self.fields["my_id"].widget.attrs['readonly'] = True

    def clean(self):
        """ Override clean to set my_id if creating new SecurityMaster object or changing asset_class """
        self.cleaned_data = super().clean()
        if len(self.initial) == 0 or self.initial["asset_class"] != self.cleaned_data["asset_class"]:
            self.cleaned_data["my_id"] = SecurityMaster.generate_my_id(self.cleaned_data["asset_class"])
        return self.cleaned_data
