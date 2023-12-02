import datetime

from django.db import IntegrityError

from ...models.investmentaccount import Broker, InvestmentAccount
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class InvestmentAccountTests(DjangoModelTestCaseBase):

    def equal(self, model1: InvestmentAccount, model2: InvestmentAccount):
        self.simple_equal(model1, model2, InvestmentAccount)

    def test_unique_broker_accountid(self):
        InvestmentAccountTests.inv_acc_fidelity_individual()

        with self.assertRaises(IntegrityError):
            InvestmentAccountTests.inv_acc_fidelity_individual(get_or_create=False)

    @staticmethod
    def inv_acc_fidelity_individual(get_or_create=True):
        inv_acc = (InvestmentAccount.objects.get_or_create if get_or_create else InvestmentAccount.objects.create)(
            broker=Broker.FIDELITY, account_id="Z12345678", account_name="Individual - Test", taxable=True,
            create_date=datetime.date(2021, 7, 19))
        return inv_acc[0] if get_or_create else inv_acc

    @staticmethod
    def inv_acc_fidelity_roth():
        return InvestmentAccount.objects.get_or_create(
            broker=Broker.FIDELITY, account_id="123456789", account_name="ROTH IRA - Test", taxable=False,
            create_date=datetime.date(2022, 9, 6))[0]
