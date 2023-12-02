from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from ..forms.forms import BrokerUploadFileForm
from ..models.investmentaccount import Broker
from ..models.transaction import Transaction


def transaction_home(request):
    return render(request, "investing/transaction/transactionhome.html")


def transaction_file_upload(request):
    if request.method == "POST":
        in_memory_file = request.FILES["file"]

        try:
            trans_list, sec_ns_list, exist_inv_acc_dates_set = Transaction.load_transactions_from_file(
                Broker(request.POST["broker"]), in_memory_file)
        except Exception as ex:
            return render(request, "investing/transaction/transactionfileuploadfailed.html",
                          context={"filename": in_memory_file.name, "error": repr(ex)})

        FileSystemStorage().save("files/input/transactions/" + in_memory_file.name, in_memory_file)

        sec_ns_str = ", ".join(sorted([x.ticker for x in sec_ns_list]))
        eiacd_list = sorted([{"broker": x[0].broker, "account_name": x[0].account_name, "date": str(x[1])}
                             for x in exist_inv_acc_dates_set],
                            key=lambda x: (x["broker"], x["account_name"], x["date"]))
        trans_list = [(x.investment_account.broker, x.investment_account.account_name, str(x.trans_date),
                       str(x.trans_type), str(x.action_type), x.description,
                       "" if x.security is None else x.security.ticker, str(x.quantity), str(x.price),
                       str(x.amount_net), str(x.commission), str(x.fees)) for x in trans_list]
        return render(request, "investing/transaction/transactionfileuploadsuccess.html",
                      context={"sec_ns_str": sec_ns_str, "eiacd_list": eiacd_list, "trans_list": trans_list})
    else:
        form = BrokerUploadFileForm(file_label="Transaction File")
        return render(request, "investing/transaction/transactionfileupload.html", context={"form": form})

