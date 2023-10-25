from django import forms

from ..models.securitymaster import SecurityMaster


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
