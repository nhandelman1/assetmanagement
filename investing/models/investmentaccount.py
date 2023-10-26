from django.db import models
from django.utils.translation import gettext_lazy


class InvestmentAccount(models.Model):
    """ Investment Account Model

    Attributes:
        broker (Broker): brokerage where account is
        account_id (str): account identifier that won't change
        account_name (str): account identifier that could change (and shouldn't be used as the primary identifier)
    """
    class Broker(models.TextChoices):
        FIDELITY = "FIDELITY", gettext_lazy("FIDELITY")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["broker", "account_id"],
                                    name="unique_%(app_label)s_%(class)s_broker_accountid")]
        ordering = ["broker", "account_name"]

    broker = models.CharField(max_length=30, choices=Broker.choices)
    account_id = models.CharField(max_length=20)
    account_name = models.CharField(max_length=30)
    taxable = models.BooleanField()

    def __repr__(self):
        return self.__str__() + ", " + str(self.taxable)

    def __str__(self):
        """ __str__ override

        Format:
            self.broker, self.account_id, self.account_name

        Returns:
            str: as described by Format
        """
        return self.broker + ", " + self.account_id + ", " + self.account_name


Broker = InvestmentAccount.Broker
