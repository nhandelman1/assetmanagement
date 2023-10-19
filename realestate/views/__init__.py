from .depreciationview import depreciation_home, depreciation_bill_create, depreciation_bill_update
from .electricview import electric_home, electric_bill_upload, \
    electric_bill_upload_success, electric_bill_estimate_input, electric_bill_estimate_edit,\
    electric_bill_estimate_select, electric_bill_partial_input_tax_related_cost, electric_bill_partial_input_bill_ratio, \
    electric_bill_partial_select, electric_data_input, electric_data_select
from .mortgageview import mortgage_home, mortgage_bill_upload, \
    mortgage_bill_upload_success, mortgage_bill_partial_input_tax_related_cost, \
    mortgage_bill_partial_input_bill_ratio, mortgage_bill_partial_select
from .natgasview import natgas_home, natgas_bill_upload, natgas_bill_upload_success, \
    natgas_bill_estimate_input, natgas_bill_estimate_edit, natgas_bill_estimate_select, natgas_data_input, \
    natgas_data_select, natgas_bill_partial_input_tax_related_cost, natgas_bill_partial_input_bill_ratio, \
    natgas_bill_partial_select
from .realestateview import real_estate_home
from .reportview import report_home, bill_report_select, utility_savings_select
from .simpleview import simple_home, simple_bill_partial_input_tax_related_cost, \
    simple_bill_partial_input_bill_ratio, simple_bill_partial_select
from .solarview import solar_home, solar_bill_input, solar_bill_update
