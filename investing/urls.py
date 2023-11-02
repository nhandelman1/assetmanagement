from django.urls import path

from . import views

app_name = "investing"
urlpatterns = [
    path("", views.investing_home, name="investing"),

    path("closedposition/", views.closed_position_home, name="closedposition"),
    path("closedposition/file/upload/", views.closed_position_file_upload, name="closedpositionfileupload"),

    path("investmentaccount/", views.investment_account_home, name="investmentaccount"),

    path("position/", views.position_home, name="position"),

    path("securitymaster/", views.security_master_home, name="securitymaster"),

    path("transaction/", views.transaction_home, name="transaction"),
    path("transaction/file/upload/", views.transaction_file_upload, name="transactionfileupload"),
]
