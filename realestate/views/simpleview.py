from decimal import Decimal
import datetime

from django.contrib import messages
from django.shortcuts import render

from ..forms.forms import SimpleServiceBillPartialSelectForm
from ..forms.modelforms import SimpleBillForm, SimpleBillPartialInputRatioForm
from ..models.simplebilldata import SimpleBillData


def simple_home(request):
    return render(request, "realestate/simple/simplehome.html")


def simple_bill_partial_select(request):
    if request.method == "POST":
        form = SimpleServiceBillPartialSelectForm(request.POST, utility_bill_data_model=SimpleBillData)
        if form.is_valid():
            load_from_real_estate = form.cleaned_data["load_from_real_estate"]
            create_for_real_estate = form.cleaned_data["create_for_real_estate"]
            service_provider = form.cleaned_data["service_provider"]
            year = form.cleaned_data["paid_year"]
            # start_date is part of unique constraint so use it instead of paid_date
            start_dates = SimpleBillData.objects.filter(
                real_estate=create_for_real_estate, service_provider=service_provider,
                paid_date__gte=datetime.date(year, 1, 1), paid_date__lte=datetime.date(year, 12, 31))\
                .values_list("start_date", flat=True)
            load_bills_qs = SimpleBillData.objects.filter(
                real_estate=load_from_real_estate, service_provider=service_provider,
                paid_date__gte=datetime.date(year, 1, 1), paid_date__lte=datetime.date(year, 12, 31))

            num_bills_loaded = len(load_bills_qs)
            load_bills_qs = load_bills_qs.exclude(start_date__in=start_dates)
            formset = SimpleBillPartialInputRatioForm.formset(
                queryset=load_bills_qs, init_dict={"create_for_real_estate": create_for_real_estate})
            num_bills_create = len(formset)
            context = {"formset": formset, "load_from_real_estate": load_from_real_estate, "year": year,
                       "create_for_real_estate": create_for_real_estate, "service_provider": service_provider,
                       "num_bills_loaded": num_bills_loaded, "num_bills_create": num_bills_create}
            return render(request, "realestate/simple/simplebillpartialinputratio.html", context=context)
        else:
            messages.error(request, str(form.errors))
            return render(request, "realestate/simple/simplebillpartialselect.html", context={"form": form})
    else:
        form = SimpleServiceBillPartialSelectForm(utility_bill_data_model=SimpleBillData)
        return render(request, "realestate/simple/simplebillpartialselect.html", context={"form": form})


def simple_bill_partial_input_bill_ratio(request):
    formset = SimpleBillPartialInputRatioForm.formset(data=request.POST, files=request.FILES)

    if formset.is_valid():
        new_bill_pk_list = []
        for form in formset.forms:
            bill = form.instance.modify(cost_ratio=form.cleaned_data["bill_ratio"],
                                        real_estate=form.cleaned_data["create_for_real_estate"])
            bill = SimpleBillData.set_default_tax_related_cost([(bill, Decimal("NaN"))])[0]
            bill.save()
            new_bill_pk_list.append(bill.pk)

        formset = SimpleBillForm.formset(queryset=SimpleBillData.objects.filter(pk__in=new_bill_pk_list),
                                         edit_fields=["notes", "tax_rel_cost"])

        context = {"formset": formset}
        return render(request, "realestate/simple/simplebillpartialinputtaxrelatedcost.html", context=context)
    else:
        messages.error(request, str(formset.errors))
        d = request.POST
        context = {"formset": formset, "load_from_real_estate": d["load_from_real_estate"], "year": d["year"],
                   "create_for_real_estate": formset.forms[0].cleaned_data["create_for_real_estate"],
                   "service_provider": d["service_provider"], "num_bills_loaded": d["num_bills_loaded"],
                   "num_bills_create": d["num_bills_create"]}
        return render(request, "realestate/simple/simplebillpartialinputratio.html", context=context)


def simple_bill_partial_input_tax_related_cost(request):
    formset = SimpleBillForm.formset(data=request.POST, files=request.FILES, edit_fields=["notes", "tax_rel_cost"])

    if formset.is_valid():
        formset.save()
        return render(request, "realestate/simple/simplebillpartialsavesuccess.html")
    else:
        messages.error(request, str(formset.errors))
        context = {"formset": formset}
        return render(request, "realestate/simple/simplebillpartialinputtaxrelatedcost.html", context=context)