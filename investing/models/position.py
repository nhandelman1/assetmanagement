from decimal import Decimal
import datetime

from django.db import models

from ..models.investmentaccount import InvestmentAccount
from ..models.securitymaster import SecurityMaster


class Position(models.Model):
    """ Position Model

    End of day portfolio positions

    Attributes:
        investment_account (InvestmentAccount):
        close_date (datetime.date):
        security (SecurityMaster):
        quantity (Decimal): can have partial shares
        close_price (Decimal):
        market_value (Decimal): typically quantity * close_price but this is not enforced
        cost_basis_avg (Decimal):
        cost_basis_total (Decimal): typically quantity * cost_basis_avg but this is not enforced
    """
    investment_account = models.ForeignKey(InvestmentAccount, models.PROTECT)
    close_date = models.DateField()
    security = models.ForeignKey(SecurityMaster, models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    close_price = models.DecimalField(max_digits=8, decimal_places=2)
    market_value = models.DecimalField(max_digits=12, decimal_places=2)
    cost_basis_avg = models.DecimalField(max_digits=8, decimal_places=2)
    cost_basis_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __repr__(self):
        return repr(self.investment_account) + ", " + repr(self.security) + ", " + str(self.quantity)

    def __str__(self):
        return self.investment_account.broker + ", " + self.investment_account.account_name + ", " + \
            self.security.ticker + ", " + str(self.quantity)
