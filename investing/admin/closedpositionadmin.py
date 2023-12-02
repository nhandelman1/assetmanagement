from django.contrib import admin


class ClosedPositionAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Position Information", {"fields": ["investment_account", "security", "quantity", "enter_date",
                                             "enter_price_net", "close_date", "close_price_net"]}),
        ("Basis Information", {"fields": ["cost_basis_price", "cost_basis_total", "cost_basis_price_unadj",
                                          "cost_basis_total_unadj"]}),
        ("Proceeds Information", {"fields": ["proceeds_price", "proceeds_total"]}),
        ("PnL Information", {"fields": ["short_term_pnl", "long_term_pnl", "short_term_pnl_unadj",
                                        "long_term_pnl_unadj"]})]
    list_display = ["get_broker", "get_account_name", "get_security_ticker", "get_security_asset_class",
                    "quantity", "enter_date", "cost_basis_total", "close_date", "proceeds_total", "short_term_pnl",
                    "long_term_pnl"]
    list_filter = ["investment_account__broker", "investment_account__account_name", "enter_date", "close_date"]
    search_fields = ["security__ticker", "enter_date", "close_date"]

    @admin.display(ordering='investment_account__broker', description='Account_Broker')
    def get_broker(self, closed_position):
        return closed_position.investment_account.broker

    @admin.display(ordering='investment_account__name', description='Account_Name')
    def get_account_name(self, closed_position):
        return closed_position.investment_account.account_name

    @admin.display(ordering='security__ticker', description='Security_Ticker')
    def get_security_ticker(self, closed_position):
        return closed_position.security.ticker

    @admin.display(ordering='security__asset_class', description='Security_Asset_Class')
    def get_security_asset_class(self, closed_position):
        return closed_position.security.asset_class
