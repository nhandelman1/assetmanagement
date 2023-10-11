from django.contrib import admin

from ..models import DepreciationBillData, ElectricBillData, ElectricData, EstimateNote, MortgageBillData, \
    MySunpowerHourlyData, NatGasBillData, NatGasData, RealPropertyValue, ServiceProvider, SimpleBillData, \
    SolarBillData, RealEstate
from .depreciationbilldataadmin import DepreciationBillDataAdmin
from .electricbilldataadmin import ElectricBillDataAdmin
from .electricdataadmin import ElectricDataAdmin
from .estimatenoteadmin import EstimateNoteAdmin
from .mortgagebilldataadmin import MortgageBillDataAdmin
from .mysunpowerhourlydataadmin import MySunpowerHourlyDataAdmin
from .natgasbilldataadmin import NatGasBillDataAdmin
from .natgasdataadmin import NatGasDataAdmin
from .realpropertyvalueadmin import RealPropertyValueAdmin
from .serviceprovideradmin import ServiceProviderAdmin
from .simplebilldataadmin import SimpleBillDataAdmin
from .solarbilldataadmin import SolarBillDataAdmin


admin.site.register(DepreciationBillData, DepreciationBillDataAdmin)
admin.site.register(ElectricBillData, ElectricBillDataAdmin)
admin.site.register(ElectricData, ElectricDataAdmin)
admin.site.register(EstimateNote, EstimateNoteAdmin)
admin.site.register(MortgageBillData, MortgageBillDataAdmin)
admin.site.register(MySunpowerHourlyData, MySunpowerHourlyDataAdmin)
admin.site.register(NatGasBillData, NatGasBillDataAdmin)
admin.site.register(NatGasData, NatGasDataAdmin)
admin.site.register(RealPropertyValue, RealPropertyValueAdmin)
admin.site.register(ServiceProvider, ServiceProviderAdmin)
admin.site.register(SimpleBillData, SimpleBillDataAdmin)
admin.site.register(SolarBillData, SolarBillDataAdmin)
admin.site.register(RealEstate)
