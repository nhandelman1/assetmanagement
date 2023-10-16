import datetime

from django.contrib import messages
from django.shortcuts import render

from ..forms.forms import DepreciationBillSelectForm
from ..forms.modelforms import DepreciationBillForm
from ..models.depreciationbilldata import DepreciationBillData


def depreciation_home(request):
    return render(request, "realestate/depreciation/depreciationhome.html")


def depreciation_bill_create(request):
    if request.method == "POST":
        form = DepreciationBillSelectForm(request.POST)
        if form.is_valid():
            real_estate = form.cleaned_data["real_estate"]
            service_provider = form.cleaned_data["service_provider"]
            year = form.cleaned_data["year"]
            try:
                bill_list, nd_list = DepreciationBillData.create_bills(real_estate, service_provider, year)
            except Exception as ex:
                messages.error(request, str(ex))
                return render(request, "realestate/depreciation/depreciationbillcreate.html",
                              context={"form": form})

            formset = DepreciationBillForm.formset(
                queryset=DepreciationBillData.objects.filter(real_estate=real_estate, service_provider=service_provider,
                                                             start_date=datetime.date(year, 1, 1)),
                edit_fields=["notes", "period_usage_pct"])
            context = {"formset": formset, "nd_list": nd_list}
            return render(request, "realestate/depreciation/depreciationbillcreatesuccess.html", context=context)
        else:
            messages.error(request, str(form.errors))
            return render(request, "realestate/depreciation/depreciationbillcreate.html", context={"form": form})
    else:
        form = DepreciationBillSelectForm()
        return render(request, "realestate/depreciation/depreciationbillcreate.html", context={"form": form})


def depreciation_bill_update(request):
    formset = DepreciationBillForm.formset(data=request.POST, edit_fields=["notes", "period_usage_pct"])
    if formset.is_valid():
        # bulk_update also an option but it has some caveats that are concerning (e.g. not calling save())
        for form in formset.forms:
            form.instance = DepreciationBillData.apply_period_usage_to_bills([form.instance])[0]
        formset.save()
        return render(request, "realestate/depreciation/depreciationbillsavesuccess.html")
    else:
        messages.error(request, str(formset.errors))
        context = {"formset": formset, "nd_list": []}
        return render(request, "realestate/depreciation/depreciationbillcreatesuccess.html", context=context)
