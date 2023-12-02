from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from ..forms.forms import BrokerUploadFileForm
from ..models.closedposition import ClosedPosition
from ..models.investmentaccount import Broker


def closed_position_home(request):
    return render(request, "investing/closedposition/closedpositionhome.html")


def closed_position_file_upload(request):
    if request.method == "POST":
        in_memory_file = request.FILES["file"]

        try:
            pos_list, sec_ns_list, exist_inv_acc_dates_set = ClosedPosition.load_closed_positions_from_file(
                Broker(request.POST["broker"]), in_memory_file)
        except Exception as ex:
            return render(request, "investing/closedposition/closedpositionfileuploadfailed.html",
                          context={"filename": in_memory_file.name, "error": repr(ex)})

        FileSystemStorage().save("files/input/closedpositions/" + in_memory_file.name, in_memory_file)

        sec_ns_str = ", ".join(sorted([x.ticker for x in sec_ns_list]))
        eiacd_list = sorted([{"broker": x[0].broker, "account_name": x[0].account_name, "date": str(x[1])}
                             for x in exist_inv_acc_dates_set],
                            key=lambda x: (x["broker"], x["account_name"], x["date"]))
        pos_list = [(x.investment_account.broker, x.investment_account.account_name, str(x.enter_date),
                     str(x.close_date), x.security.ticker, str(x.quantity), str(x.enter_price_net),
                     str(x.close_price_net), str(x.cost_basis_price), str(x.cost_basis_total), str(x.proceeds_price),
                     str(x.proceeds_total), str(x.short_term_pnl), str(x.long_term_pnl), str(x.cost_basis_price_unadj),
                     str(x.cost_basis_total_unadj), str(x.short_term_pnl_unadj), str(x.long_term_pnl_unadj))
                    for x in pos_list]
        return render(request, "investing/closedposition/closedpositionfileuploadsuccess.html",
                      context={"sec_ns_str": sec_ns_str, "eiacd_list": eiacd_list, "pos_list": pos_list})
    else:
        form = BrokerUploadFileForm(file_label="Closed Position File")
        return render(request, "investing/closedposition/closedpositionfileupload.html", context={"form": form})