from django import forms

from ..models.investmentaccount import Broker


class BrokerUploadFileForm(forms.Form):
    broker = forms.ChoiceField(choices=Broker.choices)
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        file_label = kwargs.pop("file_label", None)
        super().__init__(*args, **kwargs)
        if file_label is not None:
            self.fields["file"].label = file_label

