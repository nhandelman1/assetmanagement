from django.contrib import admin

from ..forms.modelforms import PositionAdminForm


class PositionAdmin(admin.ModelAdmin):
    form = PositionAdminForm

    fieldsets = [
        ("Purchase Information", {"fields": ["investment_account", "security", "quantity", "purchase_date",
                                             "cost_basis_price", "cost_basis_total"]}),
        ("End of Day Information", {"fields": ["close_date", "close_price", "market_value"]})]
    list_display = ["get_broker", "get_account_name", "close_date", "get_security_ticker", "get_security_asset_class",
                    "quantity", "close_price", "market_value", "purchase_date", "cost_basis_price", "cost_basis_total"]
    list_filter = ["investment_account__broker", "investment_account__account_name", "close_date", "purchase_date"]
    search_fields = ["security__ticker", "close_date", "purchase_date"]

    @admin.display(ordering='investment_account__broker', description='Account_Broker')
    def get_broker(self, position):
        return position.investment_account.broker

    @admin.display(ordering='investment_account__name', description='Account_Name')
    def get_account_name(self, position):
        return position.investment_account.account_name

    @admin.display(ordering='security__ticker', description='Security_Ticker')
    def get_security_ticker(self, position):
        return position.security.ticker

    @admin.display(ordering='security__asset_class', description='Security_Asset_Class')
    def get_security_asset_class(self, position):
        return position.security.asset_class