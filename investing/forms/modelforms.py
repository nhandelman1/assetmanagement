from decimal import InvalidOperation

from django import forms
from django.core.exceptions import ObjectDoesNotExist

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
        for total, price in (("market_value", "eod_price"), ("cost_basis_total", "cost_basis_price")):
            if cd[total] is None:
                if all([x in cd for x in ["quantity", price]]):
                    cd[total] = round(cd["quantity"] * cd[price], self.fields[total].decimal_places)

        return self.cleaned_data


class SecurityMasterAdminForm(forms.ModelForm):

    class Meta:
        model = SecurityMaster
        opt_str = "For " + str(SecurityMaster.AssetClass.OPTION) + ": leave blank to infer this field from ticker."
        help_texts = {"my_id": "auto populated - not editable", "underlying_security": opt_str,
                      "expiration_date": opt_str, "option_type": opt_str, "strike_price": opt_str,
                      "contract_size": opt_str}
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # my_id should not be changed by user. set readonly here so it is returned in cleaned_data
        self.fields["my_id"].widget.attrs['readonly'] = True

    def clean(self):
        """ Override clean to set my_id if creating new SecurityMaster object or changing asset_class """
        cd = super().clean()  # super returns self.cleaned_data

        if len(self.errors) > 0:
            return self.cleaned_data

        if len(self.initial) == 0 or self.initial["asset_class"] != cd["asset_class"]:
            cd["my_id"] = SecurityMaster.generate_my_id(cd["asset_class"])
        if cd["asset_class"] == SecurityMaster.AssetClass.OPTION.label:
            fld_list = ["underlying_security", "expiration_date", "option_type", "strike_price", "contract_size"]
            if any([cd[x] is None for x in fld_list]):
                try:
                    val_list = list(SecurityMaster.get_option_data_from_ticker(cd["ticker"]))
                except (InvalidOperation, ObjectDoesNotExist, ValueError) as ex:
                    raise forms.ValidationError(str(ex))

                val_list[2] = val_list[2].value
                for i, f in enumerate(fld_list):
                    cd[f] = cd[f] if cd[f] is not None else val_list[i]

        return self.cleaned_data
