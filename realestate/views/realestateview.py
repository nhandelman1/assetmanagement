from django.shortcuts import render


def real_estate_home(request):
    return render(request, "realestate/realestatehome.html")