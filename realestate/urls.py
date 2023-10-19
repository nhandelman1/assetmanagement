from django.urls import path

from . import views

app_name = "realestate"
urlpatterns = [
    path("", views.real_estate_home, name="realestate"),

    path("depreciation/", views.depreciation_home, name="depreciation"),
    path("depreciation/bill/create/", views.depreciation_bill_create, name="depreciationbillcreate"),
    path("depreciation/bill/update/", views.depreciation_bill_update, name="depreciationbillupdate"),

    path("electric/", views.electric_home, name="electric"),
    path("electric/bill/estimate/", views.electric_bill_estimate_select, name="electricbillestimateselect"),
    path("electric/bill/estimate/input", views.electric_bill_estimate_input, name="electricbillestimateinput"),
    path("electric/bill/estimate/edit", views.electric_bill_estimate_edit, name="electricbillestimateedit"),
    path("electric/bill/partial/", views.electric_bill_partial_select, name="electricbillpartialselect"),
    path("electric/bill/partial/input/billratio", views.electric_bill_partial_input_bill_ratio,
         name="electricbillpartialinputbillratio"),
    path("electric/bill/partial/input/taxrelatedcost", views.electric_bill_partial_input_tax_related_cost,
         name="electricbillpartialinputtaxrelatedcost"),
    path("electric/bill/upload/", views.electric_bill_upload, name="electricbillupload"),
    path("electric/bill/upload/success/", views.electric_bill_upload_success,
         name="electricbilluploadsuccess"),
    path("electric/data/select/", views.electric_data_select, name="electricdataselect"),
    path("electric/data/input/", views.electric_data_input, name="electricdatainput"),

    path("mortgage/", views.mortgage_home, name="mortgage"),
    path("mortgage/bill/partial/", views.mortgage_bill_partial_select, name="mortgagebillpartialselect"),
    path("mortgage/bill/partial/input/billratio", views.mortgage_bill_partial_input_bill_ratio,
         name="mortgagebillpartialinputbillratio"),
    path("mortgage/bill/partial/input/taxrelatedcost", views.mortgage_bill_partial_input_tax_related_cost,
         name="mortgagebillpartialinputtaxrelatedcost"),
    path("mortgage/bill/upload/", views.mortgage_bill_upload, name="mortgagebillupload"),
    path("mortgage/bill/upload/success/", views.mortgage_bill_upload_success,
         name="mortgagebilluploadsuccess"),

    path("natgas/", views.natgas_home, name="natgas"),
    path("natgas/bill/estimate/", views.natgas_bill_estimate_select, name="natgasbillestimateselect"),
    path("natgas/bill/estimate/input", views.natgas_bill_estimate_input, name="natgasbillestimateinput"),
    path("natgas/bill/estimate/edit", views.natgas_bill_estimate_edit, name="natgasbillestimateedit"),
    path("natgas/bill/partial/", views.natgas_bill_partial_select, name="natgasbillpartialselect"),
    path("natgas/bill/partial/input/billratio", views.natgas_bill_partial_input_bill_ratio,
         name="natgasbillpartialinputbillratio"),
    path("natgas/bill/partial/input/taxrelatedcost", views.natgas_bill_partial_input_tax_related_cost,
         name="natgasbillpartialinputtaxrelatedcost"),
    path("natgas/bill/upload/", views.natgas_bill_upload, name="natgasbillupload"),
    path("natgas/bill/upload/success/", views.natgas_bill_upload_success,
         name="natgasbilluploadsuccess"),
    path("natgas/data/select/", views.natgas_data_select, name="natgasdataselect"),
    path("natgas/data/input/", views.natgas_data_input, name="natgasdatainput"),

    path("report/", views.report_home, name="report"),
    path("report/billreport/select/", views.bill_report_select, name="billreportselect"),
    path("report/utilitysavings/select/", views.utility_savings_select, name="utilitysavingsselect"),

    path("simple/", views.simple_home, name="simple"),
    path("simple/bill/partial/", views.simple_bill_partial_select, name="simplebillpartialselect"),
    path("simple/bill/partial/input/billratio", views.simple_bill_partial_input_bill_ratio,
         name="simplebillpartialinputbillratio"),
    path("simple/bill/partial/input/taxrelatedcost", views.simple_bill_partial_input_tax_related_cost,
         name="simplebillpartialinputtaxrelatedcost"),

    path("solar/", views.solar_home, name="solar"),
    path("solar/bill/input/", views.solar_bill_input, name="solarbillinput"),
    path("solar/bill/update/", views.solar_bill_update, name="solarbillupdate")
]