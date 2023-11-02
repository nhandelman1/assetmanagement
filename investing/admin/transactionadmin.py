from django.contrib import admin


class TransactionAdmin(admin.ModelAdmin):
    list_display = ["get_broker", "get_account_name", "trans_date", "trans_type", "action_type", "get_security_ticker",
                    "quantity", "price", "amount"]
    list_filter = ["investment_account__broker", "investment_account__account_name", "trans_date", "trans_type",
                   "action_type"]
    search_fields = ["security__ticker", "trans_date", "description"]

    @admin.display(ordering='investment_account__broker', description='Account_Broker')
    def get_broker(self, transaction):
        return transaction.investment_account.broker

    @admin.display(ordering='investment_account__name', description='Account_Name')
    def get_account_name(self, transaction):
        return transaction.investment_account.account_name

    @admin.display(ordering='security__ticker', description='Security_Ticker')
    def get_security_ticker(self, transaction):
        return None if transaction.security is None else transaction.security.ticker
