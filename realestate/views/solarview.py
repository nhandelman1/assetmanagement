from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError
from django.shortcuts import render

from ..forms.modelforms import SolarBillForm
from ..models import MySunpowerHourlyData, SolarBillData


def solar_home(request):
    return render(request, "realestate/solar/solarhome.html")


def solar_bill_input(request):
    if request.method == "POST":
        form = SolarBillForm(request.POST, request.FILES)
        in_memory_file = form.files.get("hourly_usage_file", None)
        if in_memory_file is not None:
            try:
                MySunpowerHourlyData.process_save_sunpower_hourly_file(in_memory_file)
            except IntegrityError as ex:
                messages.error(request,
                               str(ex) + ". At least part of the data in " + in_memory_file.name +
                               " was previously saved. Remove repeat data from the file or don't submit the file.")
                form.make_editable(read_only_fields=["solar_kwh", "home_kwh", "oc_bom_basis", "oc_pnl", "oc_eom_basis",
                                                     "tax_rel_cost", "total_cost"], disable_read_only_fields=True)
                return render(request, "realestate/solar/solarbillinput.html", context={"form": form})
            except Exception as ex:
                messages.error(request, str(ex))
                form.make_editable(read_only_fields=["solar_kwh", "home_kwh", "oc_bom_basis", "oc_pnl", "oc_eom_basis",
                                                     "tax_rel_cost", "total_cost"], disable_read_only_fields=True)
                return render(request, "realestate/solar/solarbillinput.html", context={"form": form})

            FileSystemStorage().save("files/input/solar/" + in_memory_file.name, in_memory_file)

        # form wont be valid as several required fields are not set in the form. process_service_bill() sets all
        # required fields and returns a new SolarBillData instance. need to call is_valid() so instance has the values
        # input into the form
        form.is_valid()
        sbd = SolarBillData.process_service_bill(form.instance)
        form = SolarBillForm(instance=sbd)
        return render(request, "realestate/solar/solarbillupdate.html", context={"form": form})
    else:
        form = SolarBillForm()
        form.make_editable(read_only_fields=["solar_kwh", "home_kwh", "oc_bom_basis", "oc_pnl", "oc_eom_basis",
                                             "tax_rel_cost", "total_cost"], disable_read_only_fields=True)
        return render(request, "realestate/solar/solarbillinput.html", context={"form": form})


def solar_bill_update(request):
    form = SolarBillForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return render(request, "realestate/solar/solarbillupdatesuccess.html")
    else:
        messages.error(request, str(form.errors))
        return render(request, "realestate/solar/solarbillupdate.html", context={"form": form})