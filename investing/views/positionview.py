from django.shortcuts import render


def position_home(request):
    return render(request, "investing/position/positionhome.html")