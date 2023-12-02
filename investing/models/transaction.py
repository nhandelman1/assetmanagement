import datetime
from decimal import Decimal
from typing import Optional, Union

import numpy as np
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, IntegrityError, models, transaction
from django.utils.translation import gettext_lazy
import pandas as pd

from ..models.investmentaccount import Broker, InvestmentAccount
from ..models.securitymaster import ChangeType, SecurityMaster, TickerHistory


class Transaction(models.Model):
    """ Transaction model

    Attributes:
        investment_account (InvestmentAccount):
        trans_date (datetime.date):
        trans_type (TransactionType):
        action_type (ActionType):
        description (str):
        security (Optional[SecurityMaster]):
        quantity (Optional[Decimal]):
        price (Optional[Decimal]): transaction price (before commission and fees)
        amount_net (Decimal): transaction amount (after commission and fees)
        commission (Decimal):
        fees (Decimal):

    """
    class ActionType(models.TextChoices):
        BUY = "BUY", gettext_lazy("Buy")
        BUY_COVER = "BUY_COVER", gettext_lazy("Buy Cover")
        CONV = "CONVERSION", gettext_lazy("Conversion")
        COUP_PMT = "COUP_PMT", gettext_lazy("Coupon Payment")
        DIV = "DIVIDEND", gettext_lazy("Dividend")
        INT_PMT = "INT_PMT", gettext_lazy("Interest Payment")
        LOAN = "LOAN", gettext_lazy("Loan")
        MERGER_OLD = "MERGER_OLD", gettext_lazy("Merger Old")
        MERGER_NEW = "MERGER_NEW", gettext_lazy("Merger New")
        OPT_EXER = "OPT_EXER", gettext_lazy("Option Exercise")
        OPT_EXP = "OPT_EXP", gettext_lazy("Option Expire")
        SELL = "SELL", gettext_lazy("Sell")
        SELL_SHORT = "SELL_SHORT", gettext_lazy("Sell Short")
        SPIN_OFF = "SPINOFF", gettext_lazy("Spin-Off")
        STOCK_CONS = "STOCK_CONS", gettext_lazy("Stock Consolidation")
        STOCK_DIV = "STOCK_DIV", gettext_lazy("Stock Dividend")
        STOCK_SPLIT = "STOCK_SPLIT", gettext_lazy("Stock Split")
        TRANSFER = "TRANSFER", gettext_lazy("Transfer")

        @staticmethod
        def get_transaction_type(action_type):
            if action_type in (ActionType.CONV, ActionType.DIV, ActionType.MERGER_OLD, ActionType.MERGER_NEW,
                               ActionType.SPIN_OFF,ActionType.STOCK_CONS, ActionType.STOCK_DIV, ActionType.STOCK_SPLIT):
                return TransactionType.CORP_ACT
            elif action_type in (ActionType.COUP_PMT, ActionType.INT_PMT):
                return TransactionType.INTEREST
            elif action_type in (ActionType.LOAN, ActionType.OPT_EXER, ActionType.OPT_EXP):
                return TransactionType.OTHER
            elif action_type in (ActionType.BUY, ActionType.BUY_COVER, ActionType.SELL, ActionType.SELL_SHORT):
                return TransactionType.TRADE
            elif action_type in (ActionType.TRANSFER,):
                return TransactionType.TRANSFER
            else:
                raise ValueError(str(action_type) + " not set in Transaction.ActionType.get_transaction_type()")

    class TransactionType(models.TextChoices):
        CORP_ACT = "CORP_ACT", gettext_lazy("CORPORATE ACTION")
        INTEREST = "INTEREST", gettext_lazy("INTEREST")
        OTHER = "OTHER", gettext_lazy("OTHER")
        TRADE = "TRADE", gettext_lazy("TRADE")
        TRANSFER = "TRANSFER", gettext_lazy("TRANSFER")

        @staticmethod
        def get_action_types(trans_type):
            if trans_type == TransactionType.CORP_ACT:
                return (ActionType.CONV, ActionType.DIV, ActionType.MERGER_OLD, ActionType.MERGER_NEW,
                        ActionType.SPIN_OFF, ActionType.STOCK_CONS, ActionType.STOCK_DIV, ActionType.STOCK_SPLIT)
            elif trans_type == TransactionType.INTEREST:
                return ActionType.COUP_PMT, ActionType.INT_PMT
            elif trans_type == TransactionType.OTHER:
                return ActionType.LOAN, ActionType.OPT_EXER, ActionType.OPT_EXP
            elif trans_type == TransactionType.TRADE:
                return ActionType.BUY, ActionType.BUY_COVER, ActionType.SELL, ActionType.SELL_SHORT
            elif trans_type == TransactionType.TRANSFER:
                return ActionType.TRANSFER,
            else:
                raise ValueError(str(trans_type) + " not set in Transaction.TransactionType.get_action_types()")

        @staticmethod
        def is_security_required(trans_type):
            """ Transaction Types that are always associated with a security """
            return trans_type in (TransactionType.CORP_ACT, TransactionType.INTEREST, TransactionType.OTHER,
                                  TransactionType.TRADE)

    investment_account = models.ForeignKey(InvestmentAccount, models.PROTECT)
    trans_date = models.DateField()
    trans_type = models.CharField(max_length=10, choices=TransactionType.choices)
    action_type = models.CharField(max_length=11, choices=ActionType.choices)
    description = models.CharField(max_length=100)
    security = models.ForeignKey(SecurityMaster, models.PROTECT, blank=True, null=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=4, blank=True, null=True)
    amount_net = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=6, decimal_places=2)
    fees = models.DecimalField(max_digits=6, decimal_places=2)

    def __repr__(self):
        return repr(self.investment_account) + ", " + repr(self.trans_date) + ", " + repr(self.trans_type) + ", " + \
            repr(self.action_type) + ", " + self.description + ", " + repr(self.security)

    def __str__(self):
        return self.investment_account.broker + ", " + self.investment_account.account_name + ", " + \
            str(self.trans_date) + ", " + str(self.trans_type) + ", " + str(self.action_type) + ", " + \
            self.description + ", " + str(self.security)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        self._validate_action_type_for_transaction_type()
        self._validate_transaction_type_has_security()

    def save(self, *args, **kwargs):
        self._validate_action_type_for_transaction_type()
        self._validate_transaction_type_has_security()
        return super().save(*args, **kwargs)

    def _validate_action_type_for_transaction_type(self):
        required_trans_type = ActionType.get_transaction_type(self.action_type)
        if required_trans_type != self.trans_type:
            raise ValidationError("Action type: " + str(self.action_type) + " must have transaction type: " +
                                  str(required_trans_type))

    def _validate_transaction_type_has_security(self):
        if self.security is None and TransactionType.is_security_required(self.trans_type):
            raise ValidationError("A security must be selected for transaction type: " + str(self.trans_type))

    @classmethod
    def load_transactions_from_fidelity_file(cls, file):
        """ Open Fidelity file and create and return transactions

        File must be csv from Fidelity Active Trader Pro -> Accounts -> History. Columns must be: Date, Account,
        Symbol, Description, Currency, Quantity, Price, Amount, Commission, Fees, Type.
        Transactions in the file will not be created if there already exists transactions with the same investment
        account and transaction date. This is to prevent the same transaction being saved more than once.

        Args:
            file (Union[str, django.core.files.base.File]): name of file in media directory /files/input/transactions/
                or a File object. file is expected to be csv

        Returns:
            tuple[list[Transaction], list[SecurityMaster], set[tuple[InvestmentAccount, datetime.date]]]:
                Transaction instances with investment account / transaction date combinations that have no records are
                saved to the database, SecurityMaster list contains securities that did not exist but were created and
                set to default, set of investment account / transaction date combinations that have records in the
                database already (we dont want to create multiple copies of the same transaction)

        Raises:
            DatabaseError: if atomic transaction to save all transactions fails
            ObjectDoesNotExist: if investment account not found
            ValueError: if a DISTRIBUTION transaction quantity is 0, if unable to match transaction description with
                a TransactionType and ActionType, transactions have trans_date before account create date
        """
        def get_trans_act_type(desc_str, qty):
            # arranged from most likely to least likely transaction/action types
            if desc_str == "DIVIDEND RECEIVED":
                return TransactionType.CORP_ACT, ActionType.DIV
            elif desc_str[:10] == "YOU LOANED" or desc_str[-18:] == "MARK TO MARKET ADJ":
                return TransactionType.OTHER, ActionType.LOAN
            elif desc_str[:12] == "REINVESTMENT" or desc_str == "YOU BOUGHT":
                return TransactionType.TRADE, ActionType.BUY
            elif desc_str[:7] == "CONTRIB" or desc_str[:10] == "MONEY LINE" or desc_str[:13] == "ROLLOVER CASH" or \
                    desc_str[:18] == "TRANSFER OF ASSETS" or desc_str[:14] == "TRANSFERRED TO" or \
                    desc_str[:10] == "WIRE TRANS" or desc_str == "RECEIVED FROM YOU":
                return TransactionType.TRANSFER, ActionType.TRANSFER
            elif desc_str == "YOU SOLD":
                return TransactionType.TRADE, ActionType.SELL
            elif desc_str == "YOU SOLD OPENING TRANSACTION":
                return TransactionType.TRADE, ActionType.SELL_SHORT
            elif desc_str[:12] == "EXPIRED CALL" or desc_str[:11] == "EXPIRED PUT":
                return TransactionType.OTHER, ActionType.OPT_EXP
            elif desc_str == "YOU BOUGHT CLOSING TRANSACTION":
                return TransactionType.TRADE, ActionType.BUY_COVER
            elif desc_str == "DISTRIBUTION":
                if Decimal.is_zero(qty):
                    raise ValueError("Quantity is 0 for DISTRIBUTION transaction. How to handle this?")
                return TransactionType.CORP_ACT, (ActionType.STOCK_SPLIT if qty > Decimal(0) else ActionType.STOCK_CONS)
            elif desc_str[:10] == "MERGER MER":
                return TransactionType.CORP_ACT, \
                    ActionType.MERGER_NEW if desc_str[11:15] == "FROM" else ActionType.MERGER_OLD
            else:
                raise ValueError("Unable to match description: '" + desc_str +
                                 "' with a transaction type and action type")

        dp_dict = {}
        for f in Transaction._meta.get_fields():
            if f.name == "quantity":
                dp_dict["Quantity"] = f.decimal_places
            elif f.name == "price":
                dp_dict["Price"] = f.decimal_places
            elif f.name == "amount_net":
                dp_dict["Amount"] = f.decimal_places
            elif f.name == "commission":
                dp_dict["Commission"] = f.decimal_places
            elif f.name == "fees":
                dp_dict["Fees"] = f.decimal_places

        df = pd.read_csv(file, names=list(range(11)))
        df.columns = df.loc[5]
        df = df[6:-1]
        df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y").dt.date
        df.insert(1, "Account ID", df["Account"].fillna("1").str.split(" ").str[-1])
        df["Account ID"] = df["Account ID"].map(lambda x: x[1:-1] if x[0] == "(" and x[-1] == ")" else np.nan)
        df["Symbol"] = df["Symbol"].replace({np.nan: None})
        for col in ["Quantity", "Price", "Amount", "Commission", "Fees"]:
            df[col] = df[col].str.replace("[$,]", "", regex=True).map(lambda x: round(Decimal(x), dp_dict[col]))
        # must do this after Quantity is converted to a Decimal
        df[["Transaction Type", "Action Type"]] = df.apply(
            lambda row: get_trans_act_type(row["Description"], row["Quantity"]), axis=1,
            result_type="expand")
        # the transaction date for option expiration is at least a day after the option actually expires. set the
        # transaction date to the date in the description
        oe_rows = (df["Transaction Type"] == TransactionType.OTHER.value) & (df["Action Type"] == ActionType.OPT_EXP)
        df.loc[oe_rows, "Date"] = df.loc[oe_rows, "Description"].str.split(" ").map(
            lambda x: datetime.datetime.strptime(x[-4] + "-" + x[-3] + "-20" + x[-2], "%b-%d-%Y").date())

        acc_dict = InvestmentAccount.objects.field_to_account_dict(
            "account_id", df["Account ID"].drop_duplicates().tolist(), Broker.FIDELITY)
        sec_dict = SecurityMaster.objects.field_to_security_dict("ticker", df["Symbol"].drop_duplicates().tolist())

        for acc_id, acc in acc_dict.items():
            oldest_trans_date = df.loc[df["Account ID"] == acc_id, "Date"].min()
            if oldest_trans_date < acc.create_date:
                raise ValueError(str(acc) + ": earliest transaction is on " + str(oldest_trans_date) +
                                 ". This is before the account create_date of " + str(acc.create_date))

        # investment account and date combinations that have transaction(s) saved already
        rem_acc_dates = list(Transaction.objects.values("investment_account", "trans_date").distinct())
        rem_acc_dates = [(d["investment_account"], d["trans_date"]) for d in rem_acc_dates]

        sec_ns_list = []
        trans_list = []
        exist_inv_acc_dates_set = set()
        for ind, row in df.iterrows():
            try:
                inv_acc = acc_dict[row["Account ID"]]
            except KeyError:
                raise ObjectDoesNotExist("Account ID: " + row["Account ID"] + " does not exist as a " +
                                         str(Broker.FIDELITY) + " account")

            # don't keep transaction if its investment account and date combo has saved transaction(s)
            if (inv_acc.pk, row["Date"]) in rem_acc_dates:
                exist_inv_acc_dates_set.add((inv_acc, row["Date"]))
                continue

            if row["Symbol"] is None:
                security = None
            else:
                security = sec_dict.get(row["Symbol"], None)
                if security is None:
                    security = SecurityMaster.objects.get_or_create_default(row["Symbol"])
                    sec_ns_list.append(security)
                    sec_dict[row["Symbol"]] = security

            # create a ticker history record for mergers
            if row["Action Type"] == ActionType.MERGER_NEW.value:
                old_ticker = row["Description"][16: row["Description"].find("#")]
                try:
                    TickerHistory.objects.create(security=security, new_ticker=row["Symbol"], old_ticker=old_ticker,
                                                 change_date=row["Date"], change_type=ChangeType.MERGER)
                except IntegrityError:
                    # ok to pass. this ticker history record was already created
                    pass

            trans_list.append(Transaction(
                investment_account=inv_acc, trans_date=row["Date"], trans_type=row["Transaction Type"],
                action_type=row["Action Type"], description=row["Description"], security=security,
                quantity=row["Quantity"], price=row["Price"], amount_net=row["Amount"], commission=row["Commission"],
                fees=row["Fees"]))

        with transaction.atomic():
            for t in trans_list:
                t.save()

        return trans_list, sec_ns_list, exist_inv_acc_dates_set

    @classmethod
    def load_transactions_from_file(cls, broker, file):
        """ Open file and create and return transactions

        If a ticker/symbol is not found, a default SecurityMaster object for that ticker/symbol will be created
        Transactions in the file will not be created if there already exists transactions with the same investment
        account and transaction date. This is to prevent the same transaction being saved more than once.

        Args:
            broker (Broker): load transactions from this broker
            file (Union[str, django.core.files.base.File]): name of file in media directory /files/input/transactions/
                or a File object.

        Returns:
            tuple[list[Transaction], list[SecurityMaster], set[tuple[InvestmentAccount, datetime.date]]]:
                Transaction instances with investment account / transaction date combinations that have no records are
                saved to the database, SecurityMaster list contains securities that did not exist but were created and
                set to default, set of investment account / transaction date combinations that have records in the
                database already (we dont want to create multiple copies of the same transaction)

        Raises:
            DatabaseError: if a function called from this function raises a DatabaseError
            NotImplementedError: if broker not set in this function, if a function called from this function raises a
                NotImplementedError
            ObjectDoesNotExist: if a function called from this function raises a ObjectDoesNotExist
            ValueError: if a function called from this function raises a ValueError

        See Also:
            load_transactions_from_fidelity_file()
        """
        if isinstance(file, str):
            file = settings.MEDIA_ROOT + "/files/input/transactions/" + file

        if broker == Broker.FIDELITY:
            return cls.load_transactions_from_fidelity_file(file)
        else:
            raise NotImplementedError("broker not set in load_transactions_from_file()")


ActionType = Transaction.ActionType
TransactionType = Transaction.TransactionType
