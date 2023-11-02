from django.shortcuts import render


def investing_home(request):
    return render(request, "investing/investinghome.html")