from django.db import models
from django.utils.translation import gettext_lazy


class InvestmentAccountDataManager(models.Manager):

    def account_id_to_account_dict(self, acc_id_list, broker):
        """ Create dict of account id to account with that id

        Args:
            acc_id_list (list[str]):
            broker (Broker):

        Returns:
            dict: account id (keys) to account (values)
        """
        return {acc.account_id: acc for acc in InvestmentAccount.objects.filter(
            account_id__in=acc_id_list, broker=broker)}


class InvestmentAccount(models.Model):
    """ Investment Account Model

    Attributes:
        broker (Broker): brokerage where account is
        account_id (str): account identifier that won't change
        account_name (str): account identifier that could change (and shouldn't be used as the primary identifier)
        taxable (boolean): is this account taxable or not
        create_date (datetime.date): account was created on this date
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
    create_date = models.DateField()

    objects = InvestmentAccountDataManager()

    def __repr__(self):
        return self.__str__() + ", " + str(self.taxable) + ", " + str(self.create_date)

    def __str__(self):
        """ __str__ override

        Format:
            self.broker, self.account_id, self.account_name

        Returns:
            str: as described by Format
        """
        return self.broker + ", " + self.account_id + ", " + self.account_name


Broker = InvestmentAccount.Broker
