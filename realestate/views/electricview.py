from decimal import Decimal
import datetime

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from ..forms.forms import ComplexServiceBillEstimateSelectForm, ComplexServiceBillPartialSelectForm, \
    ElectricBillEstimateInputForm, UploadFileForm, UtilityDataSelectForm
from ..forms.modelforms import ElectricBillForm, ElectricBillPartialInputRatioForm, ElectricDataForm
from ..models import ElectricBillData, ElectricData, EstimateNote, MySunpowerHourlyData


def electric_home(request):
    return render(request, "realestate/electric/electrichome.html")


def electric_bill_upload(request):
    if request.method == "POST":
        in_memory_file = request.FILES["file"]

        try:
            bill_data = ElectricBillData.process_service_bill(in_memory_file)
        except Exception as ex:
            return render(request, "realestate/electric/electricbilluploadfailed.html",
                          context={"filename": in_memory_file.name, "error": repr(ex)})

        if bill_data.real_estate.bill_tax_related:
            tax_rel_msg = "Electric bills associated with this real estate are typically tax related. " \
                          "The total cost is the usual tax related cost but a different cost can be entered."
        else:
            tax_rel_msg = "Electric bills associated with this real estate are typically NOT tax related. " \
                          "Zero (0) is the usual tax related cost but a different cost can be entered."
        bill_data = bill_data.set_default_tax_related_cost([(bill_data, Decimal("NaN"))])[0]

        try:
            bill_data.save()
        except Exception as ex:
            FileSystemStorage().delete(bill_data.bill_file.name)
            return render(request, "realestate/electric/electricbilluploadfailed.html",
                          context={"filename": bill_data.bill_file.name, "error": repr(ex)})

        form = ElectricBillForm(instance=bill_data)
        form.make_read_only(edit_fields=["notes", "paid_date", "tax_rel_cost"])
        return render(request, "realestate/electric/electricbilluploadsuccess.html",
                      context={"form": form, "tax_rel_msg": tax_rel_msg})

    else:
        form = UploadFileForm()
        return render(request, "realestate/electric/electricbillupload.html", context={"form": form})


def electric_bill_upload_success(request):
    if request.method == "POST":
        bill_data = ElectricBillData.objects.get(pk=request.POST["id"])
        form = ElectricBillForm(request.POST, request.FILES, instance=bill_data)
        if form.is_valid():
            form.save()
            return render(request, "realestate/electric/electricbillsavesuccess.html")
        else:
            if bill_data.real_estate.bill_tax_related:
                tax_rel_msg = "Electric bills associated with this real estate are typically tax related. " \
                              "The total cost is the usual tax related cost but a different cost can be entered."
            else:
                tax_rel_msg = "Electric bills associated with this real estate are typically NOT tax related. " \
                              "Zero (0) is the usual tax related cost but a different cost can be entered."
            form.make_read_only(edit_fields=["notes", "paid_date", "tax_rel_cost"])
            messages.error(request, str(form.errors))
            return render(request, "realestate/electric/electricbilluploadsuccess.html",
                          context={"form": form, "tax_rel_msg": tax_rel_msg})


def electric_data_select(request):
    if request.method == "POST":
        form = UtilityDataSelectForm(request.POST, utility_bill_data_model=ElectricBillData)
        if form.is_valid():
            real_estate = form.cleaned_data["real_estate"]
            service_provider = form.cleaned_data["service_provider"]
            month_date = form.cleaned_data["month_year"]
            year_month = month_date.strftime("%Y%m")
            electric_data = ElectricData.objects.filter(real_estate=real_estate, year_month=year_month)
            estimate_notes = EstimateNote.objects.filter(real_estate=real_estate, service_provider=service_provider)
            if len(electric_data) == 0:
                found_message = "Electric Data not found for selected real estate, service provider, month and year. " \
                                "Input data below and select 'Save' to save the data."
                electric_data = ElectricData(real_estate=real_estate, service_provider=service_provider,
                                             month_date=month_date, year_month=year_month)
            else:
                found_message = "Electric Data found for selected real estate, service provider, month and year. " \
                                "Modify any data below and select 'Save' to save the changes."
                electric_data = electric_data[0]

            form = ElectricDataForm(instance=electric_data, estimate_note_query_set=estimate_notes)
            form.make_editable(read_only_fields=["month_date", "real_estate", "service_provider", "year_month"])
            return render(request, "realestate/electric/electricdatainput.html",
                          context={"form": form, "found_message": found_message})
        else:
            messages.error(request, str(form.errors))
            return render(request, "realestate/electric/electricdataselect.html", context={"form": form})

    else:
        form = UtilityDataSelectForm(utility_bill_data_model=ElectricBillData)
        return render(request, "realestate/electric/electricdataselect.html", context={"form": form})


def electric_data_input(request):
    electric_data = None if request.POST["id"] == "None" else ElectricData.objects.get(pk=request.POST["id"])
    form = ElectricDataForm(request.POST, instance=electric_data)
    if form.is_valid():
        form.save()
        return render(request, "realestate/electric/electricdatasavesuccess.html")
    else:
        messages.error(request, str(form.errors))
        form.make_editable(read_only_fields=["month_date", "real_estate", "service_provider", "year_month"])
        return render(request, "realestate/electric/electricdatainput.html", context={"form": form})


def electric_bill_estimate_select(request):
    if request.method == "POST":
        form = ComplexServiceBillEstimateSelectForm(request.POST, utility_bill_data_model=ElectricBillData)
        if form.is_valid():
            real_estate = form.cleaned_data["real_estate"]
            service_provider = form.cleaned_data["service_provider"]
            start_date = form.cleaned_data["start_date"]
            # indicate if actual and estimated bills exist
            bills = ElectricBillData.objects.filter(real_estate=real_estate, service_provider=service_provider,
                                                    start_date=start_date)
            actual_message = "Not Found"
            estimated_message = "Not Found"
            end_date = None
            for bill in bills:
                if bill.is_actual is True:
                    actual_message = "Found"
                    end_date = bill.end_date
                else:
                    estimated_message = "Found"

            # indicate if electric data exists for start year-month and end year-month
            start_year_month = start_date.strftime("%Y%m")
            end_year_month = None if end_date is None else end_date.strftime("%Y%m")
            datas = ElectricData.objects.filter(real_estate=real_estate, service_provider=service_provider,
                                                year_month__in=(start_year_month, end_year_month))
            start_month_message = "Not Found"
            end_month_message = "Not Found"
            for data in datas:
                if data.year_month == start_year_month:
                    start_month_message = "Found"
                if data.year_month == end_year_month:
                    end_month_message = "Found"

            # indicate if estimation data exists (e.g. solar)
            solar_message = "Not Found"
            if end_date is not None:
                try:
                    MySunpowerHourlyData.calculate_total_kwh_between_dates(start_date, end_date)
                    solar_message = "Found"
                except ValueError as ex:
                    solar_message = "Not Found: " + str(ex)

            allow_create = estimated_message == "Not Found" and \
                all([x == "Found" for x in [actual_message, start_month_message, end_month_message, solar_message]])

            form = ElectricBillEstimateInputForm(
                initial={"real_estate": real_estate, "service_provider": service_provider, "start_date": start_date,
                         "end_date": end_date, "allow_create": allow_create})
            context = {"actual_message": actual_message, "estimated_message": estimated_message,
                       "start_month_message": start_month_message, "end_month_message": end_month_message,
                       "solar_message": solar_message, "form": form}
            return render(request, "realestate/electric/electricbillestimateinput.html", context=context)
        else:
            messages.error(request, str(form.errors))
            return render(request, "realestate/electric/electricbillestimateselect.html", context={"form": form})
    else:
        form = ComplexServiceBillEstimateSelectForm(utility_bill_data_model=ElectricBillData)
        return render(request, "realestate/electric/electricbillestimateselect.html", context={"form": form})


def electric_bill_estimate_input(request):
    """
    This view should be called after electric_bill_estimate_select() is called to ensure that required data exists.
    """
    form = ElectricBillEstimateInputForm(request.POST)

    if form.is_valid():
        real_estate = form.cleaned_data["real_estate"]
        service_provider = form.cleaned_data["service_provider"]
        start_date = form.cleaned_data["start_date"]

        # due to unique constraint, at most one bill will match these criteria
        amb = ElectricBillData.objects.filter(real_estate=real_estate, service_provider=service_provider,
                                              start_date=start_date, is_actual=True)
        if len(amb) == 0:
            messages.error(request, "No actual monthly bill found for " + str(real_estate) + ", " +
                           str(service_provider) + ", start date: " + str(start_date))
            form = ComplexServiceBillEstimateSelectForm(utility_bill_data_model=ElectricBillData)
            return render(request, "realestate/electric/electricbillestimateselect.html", context={"form": form})
        else:
            amb = amb[0]

        # load start and end month electric datas
        start_year_month = start_date.strftime("%Y%m")
        end_year_month = amb.end_date.strftime("%Y%m")
        # due to unique constraint, at most two electric datas will match these criteria
        datas = ElectricData.objects.filter(real_estate=real_estate, service_provider=service_provider,
                                            year_month__in=(start_year_month, end_year_month))
        ed_sm = None
        ed_em = None
        for data in datas:
            if data.year_month == start_year_month:
                ed_sm = data
            if data.year_month == end_year_month:
                ed_em = data
        year_month_str = start_year_month if ed_sm is None else end_year_month if ed_em is None else None
        if year_month_str is not None:
            messages.error(request, "No electric data found for " + str(real_estate) + ", " + str(service_provider) +
                           ", year month: " + year_month_str)
            form = ComplexServiceBillEstimateSelectForm(utility_bill_data_model=ElectricBillData)
            return render(request, "realestate/electric/electricbillestimateselect.html", context={"form": form})

        emb = ElectricBillData.initialize_complex_service_bill_estimate(amb)
        try:
            kwh_dict = MySunpowerHourlyData.calculate_total_kwh_between_dates(emb.start_date, emb.end_date)
        except ValueError as ex:
            messages.error(request, "Solar data error - " + str(real_estate) + ", " + str(emb.start_date) +
                           " - " + str(emb.end_date)) + ": " + str(ex)
            form = ComplexServiceBillEstimateSelectForm(utility_bill_data_model=ElectricBillData)
            return render(request, "realestate/electric/electricbillestimateselect.html", context={"form": form})

        emb.total_kwh = int(round(kwh_dict["home_kwh"], 0))
        emb.eh_kwh = form.cleaned_data["electric_heater_kwh"]
        emb = ElectricBillData.estimate_monthly_bill(amb, emb, ed_sm, ed_em)
        emb.save()

        form = ElectricBillForm(instance=emb)
        return render(request, "realestate/electric/electricbillestimateedit.html", context={"form": form})
    else:
        electric_bill_estimate_select(request)


def electric_bill_estimate_edit(request):
    if request.method == "POST":
        bill_data = ElectricBillData.objects.get(pk=request.POST["id"])
        form = ElectricBillForm(request.POST, instance=bill_data)
        if form.is_valid():
            form.save()
            return render(request, "realestate/electric/electricbillestimatesavesuccess.html")
        else:
            messages.error(request, str(form.errors))
            return render(request, "realestate/electric/electricbillestimateedit.html", context={"form": form})


def electric_bill_partial_select(request):
    if request.method == "POST":
        form = ComplexServiceBillPartialSelectForm(request.POST, utility_bill_data_model=ElectricBillData)
        if form.is_valid():
            load_from_real_estate = form.cleaned_data["load_from_real_estate"]
            create_for_real_estate = form.cleaned_data["create_for_real_estate"]
            service_provider = form.cleaned_data["service_provider"]
            year = form.cleaned_data["paid_year"]
            is_actual = form.cleaned_data["is_actual_bill"]
            # start_date is part of unique constraint so use it instead of paid_date
            start_dates = ElectricBillData.objects.filter(
                real_estate=create_for_real_estate, service_provider=service_provider,
                is_actual=is_actual, paid_date__gte=datetime.date(year, 1, 1),
                paid_date__lte=datetime.date(year, 12, 31)).values_list("start_date", flat=True)
            load_bills_qs = ElectricBillData.objects.filter(
                real_estate=load_from_real_estate, service_provider=service_provider,
                is_actual=is_actual, paid_date__gte=datetime.date(year, 1, 1),
                paid_date__lte=datetime.date(year, 12, 31))

            num_bills_loaded = len(load_bills_qs)
            load_bills_qs = load_bills_qs.exclude(start_date__in=start_dates)

            formset = ElectricBillPartialInputRatioForm.formset(
                queryset=load_bills_qs, init_dict={"create_for_real_estate": create_for_real_estate})
            num_bills_create = len(formset)
            context = {"formset": formset, "load_from_real_estate": load_from_real_estate, "year": year,
                       "create_for_real_estate": create_for_real_estate, "service_provider": service_provider,
                       "num_bills_loaded": num_bills_loaded, "num_bills_create": num_bills_create}
            return render(request, "realestate/electric/electricbillpartialinputratio.html", context=context)
        else:
            messages.error(request, str(form.errors))
            return render(request, "realestate/electric/electricbillpartialselect.html", context={"form": form})
    else:
        form = ComplexServiceBillPartialSelectForm(utility_bill_data_model=ElectricBillData)
        return render(request, "realestate/electric/electricbillpartialselect.html", context={"form": form})


def electric_bill_partial_input_bill_ratio(request):
    formset = ElectricBillPartialInputRatioForm.formset(data=request.POST, files=request.FILES)

    if formset.is_valid():
        new_bill_pk_list = []
        for form in formset.forms:
            bill = form.instance.modify(cost_ratio=form.cleaned_data["bill_ratio"],
                                        real_estate=form.cleaned_data["create_for_real_estate"])
            bill = ElectricBillData.set_default_tax_related_cost([(bill, Decimal("NaN"))])[0]
            bill.save()
            new_bill_pk_list.append(bill.pk)

        formset = ElectricBillForm.formset(queryset=ElectricBillData.objects.filter(pk__in=new_bill_pk_list),
                                           edit_fields=["notes", "tax_rel_cost"])

        context = {"formset": formset}
        return render(request, "realestate/electric/electricbillpartialinputtaxrelatedcost.html", context=context)
    else:
        messages.error(request, str(formset.errors))
        d = request.POST
        context = {"formset": formset, "load_from_real_estate": d["load_from_real_estate"], "year": d["year"],
                   "create_for_real_estate": formset.forms[0].cleaned_data["create_for_real_estate"],
                   "service_provider": d["service_provider"], "num_bills_loaded": d["num_bills_loaded"],
                   "num_bills_create": d["num_bills_create"]}
        return render(request, "realestate/electric/electricbillpartialinputratio.html", context=context)


def electric_bill_partial_input_tax_related_cost(request):
    formset = ElectricBillForm.formset(data=request.POST, files=request.FILES, edit_fields=["notes", "tax_rel_cost"])

    if formset.is_valid():
        formset.save()
        return render(request, "realestate/electric/electricbillpartialsavesuccess.html")
    else:
        messages.error(request, str(formset.errors))
        context = {"formset": formset}
        return render(request, "realestate/electric/electricbillpartialinputtaxrelatedcost.html", context=context)

