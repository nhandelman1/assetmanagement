from decimal import Decimal
import datetime

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from ..forms.forms import SimpleServiceBillPartialSelectForm, UploadFileForm
from ..forms.modelforms import MortgageBillForm, MortgageBillPartialInputRatioForm
from ..models import MortgageBillData


def mortgage_home(request):
    return render(request, "realestate/mortgage/mortgagehome.html")


def mortgage_bill_upload(request):
    if request.method == "POST":
        in_memory_file = request.FILES["file"]

        try:
            bill_data = MortgageBillData.process_service_bill(in_memory_file)
        except Exception as ex:
            context = {"filename": in_memory_file.name, "error": repr(ex)}
            return render(request, "realestate/mortgage/mortgagebilluploadfailed.html", context)

        if bill_data.real_estate.bill_tax_related:
            tax_rel_msg = "Mortgage bills associated with this real estate are typically tax related. " \
                          "The interest payment (entered) is the usual tax related cost but a different cost " \
                          "can be entered."
        else:
            tax_rel_msg = "Mortgage bills associated with this real estate are typically NOT tax related. " \
                          "Zero (0) is the usual tax related cost but a different cost can be entered."
        bill_data = bill_data.set_default_tax_related_cost([(bill_data, Decimal("NaN"))])[0]

        try:
            bill_data.save()
        except Exception as ex:
            FileSystemStorage().delete(bill_data.bill_file.name)
            context = {"filename": bill_data.bill_file.name, "error": repr(ex)}
            return render(request, "realestate/mortgage/mortgagebilluploadfailed.html", context)

        form = MortgageBillForm(instance=bill_data)
        form.make_read_only(edit_fields=["notes", "paid_date", "tax_rel_cost"])
        context = {"form": form, "tax_rel_msg": tax_rel_msg}
        return render(request, "realestate/mortgage/mortgagebilluploadsuccess.html", context)

    else:
        form = UploadFileForm()
        return render(request, "realestate/mortgage/mortgagebillupload.html", {"form": form})


def mortgage_bill_upload_success(request):
    if request.method == "POST":
        bill_data = MortgageBillData.objects.get(pk=request.POST["id"])
        form = MortgageBillForm(request.POST, request.FILES, instance=bill_data)
        if form.is_valid():
            form.save()
            return render(request, "realestate/mortgage/mortgagebillsavesuccess.html")
        else:
            if form.instance.real_estate.bill_tax_related:
                tax_rel_msg = "Mortgage bills associated with this real estate are typically tax related. " \
                              "The interest payment (entered) is the usual tax related cost but a different cost " \
                              "can be entered."
            else:
                tax_rel_msg = "Mortgage bills associated with this real estate are typically NOT tax related. " \
                              "Zero (0) is the usual tax related cost but a different cost can be entered."
            form.make_read_only(edit_fields=["notes", "paid_date", "tax_rel_cost"])
            messages.error(request, str(form.errors))
            context = {"form": form, "tax_rel_msg": tax_rel_msg}
            return render(request, "realestate/mortgage/mortgagebilluploadsuccess.html", context)


def mortgage_bill_partial_select(request):
    if request.method == "POST":
        form = SimpleServiceBillPartialSelectForm(request.POST, utility_bill_data_model=MortgageBillData)
        if form.is_valid():
            load_from_real_estate = form.cleaned_data["load_from_real_estate"]
            create_for_real_estate = form.cleaned_data["create_for_real_estate"]
            service_provider = form.cleaned_data["service_provider"]
            year = form.cleaned_data["paid_year"]
            # start_date is part of unique constraint so use it instead of paid_date
            start_dates = MortgageBillData.objects.filter(
                real_estate=create_for_real_estate, service_provider=service_provider,
                paid_date__gte=datetime.date(year, 1, 1), paid_date__lte=datetime.date(year, 12, 31))\
                .values_list("start_date", flat=True)
            load_bills_qs = MortgageBillData.objects.filter(
                real_estate=load_from_real_estate, service_provider=service_provider,
                paid_date__gte=datetime.date(year, 1, 1), paid_date__lte=datetime.date(year, 12, 31))

            num_bills_loaded = len(load_bills_qs)
            load_bills_qs = load_bills_qs.exclude(start_date__in=start_dates)

            formset = MortgageBillPartialInputRatioForm.formset(
                queryset=load_bills_qs, init_dict={"create_for_real_estate": create_for_real_estate})

            num_bills_create = len(formset)
            context = {"formset": formset, "load_from_real_estate": load_from_real_estate, "year": year,
                       "create_for_real_estate": create_for_real_estate, "service_provider": service_provider,
                       "num_bills_loaded": num_bills_loaded, "num_bills_create": num_bills_create}
            return render(request, "realestate/mortgage/mortgagebillpartialinputratio.html", context=context)
        else:
            messages.error(request, str(form.errors))
            return render(request, "realestate/mortgage/mortgagebillpartialselect.html", context={"form": form})
    else:
        form = SimpleServiceBillPartialSelectForm(utility_bill_data_model=MortgageBillData)
        return render(request, "realestate/mortgage/mortgagebillpartialselect.html", context={"form": form})


def mortgage_bill_partial_input_bill_ratio(request):
    formset = MortgageBillPartialInputRatioForm.formset(data=request.POST, files=request.FILES)

    if formset.is_valid():
        new_bill_pk_list = []
        for form in formset.forms:
            bill = form.instance.modify(cost_ratio=form.cleaned_data["bill_ratio"],
                                        real_estate=form.cleaned_data["create_for_real_estate"])
            bill = MortgageBillData.set_default_tax_related_cost([(bill, Decimal("NaN"))])[0]
            bill.save()
            new_bill_pk_list.append(bill.pk)

        formset = MortgageBillForm.formset(queryset=MortgageBillData.objects.filter(pk__in=new_bill_pk_list),
                                           edit_fields=["notes", "tax_rel_cost"])

        context = {"formset": formset}
        return render(request, "realestate/mortgage/mortgagebillpartialinputtaxrelatedcost.html", context=context)
    else:
        messages.error(request, str(formset.errors))
        d = request.POST
        context = {"formset": formset, "load_from_real_estate": d["load_from_real_estate"], "year": d["year"],
                   "create_for_real_estate": formset.forms[0].cleaned_data["create_for_real_estate"],
                   "service_provider": d["service_provider"], "num_bills_loaded": d["num_bills_loaded"],
                   "num_bills_create": d["num_bills_create"]}
        return render(request, "realestate/mortgage/mortgagebillpartialinputratio.html", context=context)


def mortgage_bill_partial_input_tax_related_cost(request):
    formset = MortgageBillForm.formset(data=request.POST, files=request.FILES, edit_fields=["notes", "tax_rel_cost"])

    if formset.is_valid():
        formset.save()
        return render(request, "realestate/mortgage/mortgagebillpartialsavesuccess.html")
    else:
        messages.error(request, str(formset.errors))
        context = {"formset": formset}
        return render(request, "realestate/mortgage/mortgagebillpartialinputtaxrelatedcost.html", context=context)