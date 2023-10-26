from django.contrib import admin

from ..models import InvestmentAccount, Position, SecurityMaster
from .investmentaccountadmin import InvestmentAccountAdmin
from .positionadmin import PositionAdmin
from .securitymasteradmin import SecurityMasterAdmin


admin.site.register(InvestmentAccount, InvestmentAccountAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(SecurityMaster, SecurityMasterAdmin)
