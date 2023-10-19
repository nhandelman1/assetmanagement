from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.shortcuts import render

from ..forms.forms import BillReportSelectForm, UtilitySavingsSelectForm
from ..reports.billreport import BillReport
from ..reports.utilitysavingsreport import UtilitySavingsReport


def report_home(request):
    return render(request, "realestate/report/reporthome.html")


def bill_report_select(request):
    if request.method == "POST":
        form = BillReportSelectForm(request.POST)
        if form.is_valid():
            br = BillReport()
            try:
                output_file_path = br.do_process(form.cleaned_data["real_estate"], form.cleaned_data["year"])
            except Exception as ex:
                messages.error(request, str(ex))
                return render(request, "realestate/report/billreportselect.html", context={"form": form})

            return FileResponse(FileSystemStorage().open(output_file_path, 'rb'), as_attachment=True,
                                filename=br.output_file_name)
        else:
            messages.error(request, str(form.errors))
            return render(request, "realestate/report/billreportselect.html", context={"form": form})

    else:
        form = BillReportSelectForm()
        return render(request, "realestate/report/billreportselect.html", context={"form": form})


def utility_savings_select(request):
    if request.method == "POST":
        form = UtilitySavingsSelectForm(request.POST)
        if form.is_valid():
            usr = UtilitySavingsReport()
            try:
                output_file_path = usr.do_process(form.cleaned_data["real_estate"])
            except Exception as ex:
                messages.error(request, str(ex))
                return render(request, "realestate/report/utilitysavingsselect.html", context={"form": form})

            return FileResponse(FileSystemStorage().open(output_file_path, 'rb'), as_attachment=True,
                                filename=usr.output_file_name)

        else:
            messages.error(request, str(form.errors))
            return render(request, "realestate/report/utilitysavingsselect.html", context={"form": form})

    else:
        form = UtilitySavingsSelectForm()
        return render(request, "realestate/report/utilitysavingsselect.html", context={"form": form})
