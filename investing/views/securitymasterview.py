from django.shortcuts import render


def security_master_home(request):
    return render(request, "investing/securitymaster/securitymasterhome.html")