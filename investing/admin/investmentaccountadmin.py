from django.contrib import admin


class InvestmentAccountAdmin(admin.ModelAdmin):
    list_display = ["account_name", "broker", "account_id"]
    list_filter = ["broker"]
