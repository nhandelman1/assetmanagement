from decimal import Decimal
from typing import Union
import datetime

import numpy as np
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, models, transaction
import pandas as pd

from ..models.investmentaccount import Broker, InvestmentAccount
from ..models.securitymaster import SecurityMaster


class Position(models.Model):
    """ Position Model

    End of day portfolio positions by lot

    Attributes:
        investment_account (InvestmentAccount):
        eod_date (datetime.date): position as of this end of day date
        security (SecurityMaster):
        quantity (Decimal): can have partial shares
        close_price (Decimal): actual close price at the end of day. NOT ADJUSTED
        market_value (Decimal): typically quantity * close_price but this is not enforced
        enter_date (datetime.date): date this lot position was entered into
        cost_basis_price (Decimal):
        cost_basis_total (Decimal): typically quantity * cost_basis_price but this is not enforced
    """

    investment_account = models.ForeignKey(InvestmentAccount, models.PROTECT)
    eod_date = models.DateField()
    security = models.ForeignKey(SecurityMaster, models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    close_price = models.DecimalField(max_digits=8, decimal_places=2)
    market_value = models.DecimalField(max_digits=12, decimal_places=2)
    enter_date = models.DateField(blank=True, null=True, help_text="Required if broker breaks position into lots.")
    cost_basis_price = models.DecimalField(max_digits=8, decimal_places=2)
    cost_basis_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __repr__(self):
        return repr(self.investment_account) + ", " + repr(self.security) + ", " + repr(self.quantity) + ", " + \
            repr(self.enter_date)

    def __str__(self):
        return self.investment_account.broker + ", " + self.investment_account.account_name + ", " + \
            self.security.ticker + ", " + str(self.quantity) + ", " + str(self.enter_date)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        self._validate_broker_lots_enter_date()

    def save(self, *args, **kwargs):
        self._validate_broker_lots_enter_date()
        return super().save(*args, **kwargs)

    def _validate_broker_lots_enter_date(self):
        if self.investment_account.broker == Broker.FIDELITY and self.security.has_fidelity_lots and \
                self.enter_date is None:
            raise ValidationError(self.security.ticker +
                                  " is broken into lots by FIDELITY so positions must have an enter date.")

    @classmethod
    def load_positions_from_fidelity_file(cls, file):
        """ Open Fidelity file and create and return positions

        File must be csv from Fidelity Active Trader Pro -> Accounts -> Positions. Columns must be: Close Date, Account,
        Symbol, Currency, Quantity, Last, Value, Purchase Price, Basis, Type. If a Symbol has lots, it must be expanded
        to show the lots. Close Date column must only have 1 distinct close date (other numbers that are not dates
        are allowed) but this is not enforced (should it be?).

        Args:
            file (Union[str, django.core.files.base.File]): name of file in media directory /files/input/positions/ or a
                File object. file is expected to be csv

        Returns:
            tuple[list[Position], list[SecurityMaster]]: each Position instance is saved to the database,
                SecurityMaster list contains securities that did not exist but were created and set to default

        Raises:
            DatabaseError: if atomic transaction to save all positions fails
            ObjectDoesNotExist: if investment account not found
            ValidationError: if a position that should have lots does not have lots
            ValueError: if close date not found in 'Close Date' column
        """
        dp_dict = {}
        for f in Position._meta.get_fields():
            if f.name == "quantity":
                dp_dict["Lot Quantity"] = f.decimal_places
            elif f.name == "close_price":
                dp_dict["Last Price"] = f.decimal_places
            elif f.name == "market_value":
                dp_dict["Market Value"] = f.decimal_places
            elif f.name == "cost_basis_total":
                dp_dict["Cost Basis Total"] = f.decimal_places
            elif f.name == "cost_basis_price":
                dp_dict["Cost Basis Price"] = f.decimal_places

        df = pd.read_csv(file, names=list(range(10)))
        df.columns = df.loc[2]
        df = df[3:-2].rename(columns={"Last": "Last Price"})

        eod_date = None
        for ind, date in df["Close Date"].items():
            try:
                eod_date = datetime.datetime.strptime(date, "%m/%d/%Y").date()
                break
            except Exception:
                continue
        if eod_date is None:
            raise ValueError("close date not found in 'Close Date' column. Manually add a close date in this column "
                             "for one of the positions")

        df.insert(1, "Account ID", df["Account"].fillna("1").str.split(" ").str[-1])
        df["Account ID"] = df["Account ID"].map(lambda x: x[1:-1] if x[0] == "(" and x[-1] == ")" else np.nan)

        df.insert(3, "Ticker", df["Symbol"].fillna("1").str.split(" ").str[0])
        df.loc[df["Account ID"].isnull(), "Ticker"] = np.nan

        df["is_lot"] = df["Account ID"].isnull()
        df["Account ID"] = df["Account ID"].ffill()
        df["Ticker"] = df["Ticker"].ffill()

        lot_df = df.loc[df["is_lot"]]

        df = df.loc[~df["is_lot"], ["Account ID", "Ticker", "Quantity", "Last Price", "Value", "Purchase Price"]]

        if len(lot_df) > 0:
            lot_df = lot_df[lot_df.columns[0:8]]
            lot_df.columns = ["Lot Quantity", "Account ID", "Cost Basis Price", "Ticker", "Unrealized G/L",
                              "Unrealized % G/L", "Purchase Date", "Holding Period"]
            lot_df["Cost Basis Price"] = lot_df["Cost Basis Price"].replace("Cost Basis/Share", np.nan)
            lot_df = lot_df.loc[~lot_df["Cost Basis Price"].isnull()].drop(
                columns=["Unrealized G/L", "Unrealized % G/L", "Holding Period"])
            df = lot_df.merge(df, on=["Account ID", "Ticker"], how="outer")
            df["Lot Quantity"] = df["Lot Quantity"].fillna(df["Quantity"])
            print()
        else:
            df["Purchase Date"] = None
            df = df.rename(columns={"Quantity": "Lot Quantity", "Purchase Price": "Cost Basis Price"})

        df = df[["Account ID", "Ticker", "Lot Quantity", "Last Price", "Purchase Date", "Cost Basis Price"]]
        df = df.sort_values(by=["Account ID", "Ticker", "Purchase Date"])
        for col in ["Lot Quantity", "Last Price", "Cost Basis Price"]:
            df[col] = df[col].str.replace(",", "").fillna("1").map(lambda x: round(Decimal(x), dp_dict[col]))
        df["Market Value"] = df.apply(lambda row: round(Decimal(row["Lot Quantity"] * row["Last Price"]),
                                                        dp_dict["Market Value"]), axis=1)
        df["Cost Basis Total"] = df.apply(lambda row: round(Decimal(row["Lot Quantity"] * row["Cost Basis Price"]),
                                                            dp_dict["Cost Basis Total"]), axis=1)
        df["Purchase Date"] = pd.to_datetime(df["Purchase Date"], format="%m/%d/%Y").dt.date.replace({pd.NaT: None})

        acc_dict = InvestmentAccount.objects.account_id_to_account_dict(
            df["Account ID"].drop_duplicates().tolist(), Broker.FIDELITY)
        sec_dict = SecurityMaster.objects.ticker_to_security_dict(df["Ticker"].drop_duplicates().tolist())
        sec_ns_list = []
        pos_list = []
        for ind, row in df.iterrows():
            try:
                inv_acc = acc_dict[row["Account ID"]]
            except KeyError:
                raise ObjectDoesNotExist("Account ID: " + row["Account ID"] + " does not exist as a " +
                                         str(Broker.FIDELITY) + " account")

            security = sec_dict.get(row["Ticker"], None)
            if security is None:
                security = SecurityMaster.objects.get_or_create_default(
                    row["Ticker"], has_fidelity_lots=(row["Purchase Date"] is not None))
                sec_ns_list.append(security)
                sec_dict[row["Ticker"]] = security

            pos_list.append(Position(
                investment_account=inv_acc, eod_date=eod_date, security=security, quantity=row["Lot Quantity"],
                close_price=row["Last Price"], market_value=row["Market Value"], enter_date=row["Purchase Date"],
                cost_basis_price=row["Cost Basis Price"], cost_basis_total=row["Cost Basis Total"]))

        with transaction.atomic():
            for pos in pos_list:
                pos.save()

        return pos_list, sec_ns_list

    @classmethod
    def load_positions_from_file(cls, broker, file):
        """ Open file and create and return positions

        If a ticker/symbol is not found, a default SecurityMaster object for that ticker/symbol will be created

        Args:
            broker (Broker): load positions from this broker
            file (Union[str, django.core.files.base.File]): name of file in media directory /files/input/positions/ or a
                File object.

        Returns:
            tuple[list[Position], list[SecurityMaster]]: each Position instance is saved to the database,
                SecurityMaster list contains securities that did not exist but were created and set to default

        Raises:
            DatabaseError: if a function called from this function raises a DatabaseError
            NotImplementedError: if broker not set in this function, if a function called from this function raises a
                NotImplementedError
            ObjectDoesNotExist: if a function called from this function raises a ObjectDoesNotExist
            ValidationError: if a function called from this function raises a ValidationError
            ValueError: if a function called from this function raises a ValueError

        See Also:
            load_positions_from_fidelity_file()
        """
        if isinstance(file, str):
            file = settings.MEDIA_ROOT + "/files/input/positions/" + file

        if broker == Broker.FIDELITY:
            return cls.load_positions_from_fidelity_file(file)
        else:
            raise NotImplementedError("broker not set in load_positions_from_file()")
