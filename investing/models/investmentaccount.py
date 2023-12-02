from django.db import models
from django.utils.translation import gettext_lazy


class InvestmentAccountDataManager(models.Manager):

    def field_to_account_dict(self, key_field, keys, broker):
        """ Create dict of key_field to investment account with that key_field value

        Args:
            key_field (str): field of InvestmentAccount whose values are the return dict keys, if an InvestmentAccount
                object with that value for key_field is found. one of "pk", "account_id"
            keys (list[Union[int, str]]): e.g. [1, 2], ["Z123456789", "123456789"]
            broker (Broker):

        Returns:
            dict: key_field (keys) to InvestmentAccount object (values).  e.g. {1: inv acc 1}, {"123456789": inv acc 1}

        Raises:
            ValueError: if key_field is not one of "pk", "account_id"
        """
        if key_field not in ("pk", "account_id"):
            raise ValueError("key_field must be one of 'pk', 'account_id'")
        d = {key_field + "__in": keys, "broker": broker}
        return {getattr(sec, key_field): sec for sec in InvestmentAccount.objects.filter(**d)}


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
    create_date = models.DateField(help_text="Be wary of changing this to a more recent date (will cause issues with "
                                             "data including transactions, positions and others.")

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
