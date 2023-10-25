from django.contrib import admin

from ..models import InvestmentAccount, SecurityMaster
from .investmentaccountadmin import InvestmentAccountAdmin
from .securitymasteradmin import SecurityMasterAdmin


admin.site.register(InvestmentAccount, InvestmentAccountAdmin)
admin.site.register(SecurityMaster, SecurityMasterAdmin)
