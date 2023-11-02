from django.shortcuts import render


def investment_account_home(request):
    return render(request, "investing/investmentaccount/investmentaccounthome.html")