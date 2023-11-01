from django.contrib import admin

from ..models import ClosedPosition, InvestmentAccount, Position, SecurityMaster
from .closedpositionadmin import ClosedPositionAdmin
from .investmentaccountadmin import InvestmentAccountAdmin
from .positionadmin import PositionAdmin
from .securitymasteradmin import SecurityMasterAdmin


admin.site.register(ClosedPosition, ClosedPositionAdmin)
admin.site.register(InvestmentAccount, InvestmentAccountAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(SecurityMaster, SecurityMasterAdmin)
