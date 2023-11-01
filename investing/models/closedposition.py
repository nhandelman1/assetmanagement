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


class ClosedPositionManager(models.Manager):
    def full_constructor(self, investment_account, enter_date, close_date, security, quantity, cost_basis_price,
                         cost_basis_total, proceeds_price, proceeds_total, short_term_pnl, long_term_pnl,
                         cost_basis_price_unadj, cost_basis_total_unadj, short_term_pnl_unadj, long_term_pnl_unadj,
                         create=True):
        """ Instantiate ClosedPosition instance with option to save to database

        Args:
            see ClosedPosition class docstring
            create (bool): False to create instance only. Default True to also save to database (self.create)

        Returns:
            ClosedPosition: instance
        """
        return (self.create if create else ClosedPosition)(
            investment_account=investment_account, enter_date=enter_date, close_date=close_date, security=security,
            quantity=quantity, cost_basis_price=cost_basis_price, cost_basis_total=cost_basis_total,
            proceeds_price=proceeds_price, proceeds_total=proceeds_total, short_term_pnl=short_term_pnl,
            long_term_pnl=long_term_pnl, cost_basis_price_unadj=cost_basis_price_unadj,
            cost_basis_total_unadj=cost_basis_total_unadj, short_term_pnl_unadj=short_term_pnl_unadj,
            long_term_pnl_unadj=long_term_pnl_unadj)


class ClosedPosition(models.Model):
    """ Closed Position Model

    Closed positions by lot

    Attributes:
        investment_account (InvestmentAccount):
        enter_date (datetime.date): date this lot position was entered into
        close_date (datetime.date): date this lot position was closed
        security (SecurityMaster):
        quantity (Decimal): can have partial shares
        cost_basis_price (Decimal): cost basis price after wash sale adjustment
        cost_basis_total (Decimal): cost basis total after wash sale adjustment
        proceeds_price (Decimal): price at close of position
        proceeds_total (Decimal): proceeds at close of position
        short_term_pnl (Decimal): short term pnl after wash sale adjustment. always 0 for non taxable accounts even
            if position was held short term
        long_term_pnl (Decimal): long term pnl after wash sale adjustment. non taxable accounts always show pnl here
            for all position (those held short term and long term)
        cost_basis_price_unadj (Decimal): cost basis price before wash sale adjustment
        cost_basis_total_unadj (Decimal): cost basis total before wash sale adjustment
        short_term_pnl_unadj (Decimal): short term pnl before wash sale adjustment. always 0 for non taxable accounts
            even if position was held short term
        long_term_pnl_unadj (Decimal): long term pnl before wash sale adjustment. non taxable accounts always show pnl
            here for all position (those held short term and long term)
    """

    investment_account = models.ForeignKey(InvestmentAccount, models.PROTECT)
    enter_date = models.DateField()
    close_date = models.DateField()
    security = models.ForeignKey(SecurityMaster, models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    cost_basis_price = models.DecimalField(max_digits=9, decimal_places=3)
    cost_basis_total = models.DecimalField(max_digits=13, decimal_places=3)
    proceeds_price = models.DecimalField(max_digits=9, decimal_places=3)
    proceeds_total = models.DecimalField(max_digits=13, decimal_places=3)
    short_term_pnl = models.DecimalField(max_digits=13, decimal_places=3)
    long_term_pnl = models.DecimalField(max_digits=13, decimal_places=3)
    cost_basis_price_unadj = models.DecimalField(max_digits=9, decimal_places=3)
    cost_basis_total_unadj = models.DecimalField(max_digits=13, decimal_places=3)
    short_term_pnl_unadj = models.DecimalField(max_digits=13, decimal_places=3)
    long_term_pnl_unadj = models.DecimalField(max_digits=13, decimal_places=3)

    objects = ClosedPositionManager()

    def __repr__(self):
        return repr(self.investment_account) + ", " + repr(self.security) + ", " + repr(self.enter_date) + ", " + \
            repr(self.close_date) + ", " + repr(self.quantity)

    def __str__(self):
        return self.investment_account.broker + ", " + self.investment_account.account_name + ", " + \
            self.security.ticker + ", " + str(self.enter_date) + ", " + str(self.close_date) + ", " + str(self.quantity)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        self._validate_non_taxable_pnl()

    def save(self, *args, **kwargs):
        self._validate_non_taxable_pnl()
        return super().save(*args, **kwargs)

    def _validate_non_taxable_pnl(self):
        if not self.investment_account.taxable and \
                (not Decimal.is_zero(self.short_term_pnl) or not Decimal.is_zero(self.short_term_pnl_unadj)):
            raise ValidationError("Non taxable accounts must have short term pnl fields set to 0. pnl for non taxable "
                                  "accounts must be entered in long term pnl fields")

    @classmethod
    def load_closed_positions_from_fidelity_file(cls, file):
        """ Open Fidelity file and create and return closed positions

        File must be csv from Fidelity Active Trader Pro -> Accounts -> Closed Positions.
        Primary Columns must be: "Symbol", "Security Description", "Quantity", "Basis/Share", "Proceeds/Share",
        "Basis", "Proceeds", "Short-Term G/L", "Long-Term G/L", "Unadj Basis/Share", "Unadj Basis",
        "Unadj Short-Term G/L", "Unadj Long-Term G/L", "Account".
        Lot Columns must be: "Date Acquired", "Date Sold", "Quantity", "Basis/Share", "Proceeds/Share", "Basis",
        "Proceeds", "Short-Term G/L", "Long-Term G/L", "Unadj Basis/Share", "Unadj Basis", "Unadj Short-Term G/L",
        "Unadj Long-Term G/L", "Unadj Date Acquired".
        Closed positions must be expanded to show the lots.

        Args:
            file (Union[str, django.core.files.base.File]): name of file in media directory
                /files/input/closedpositions/ or a File object. file is expected to be csv

        Returns:
            tuple[list[ClosedPosition], list[SecurityMaster]]: each ClosedPosition instance is saved to the database,
                SecurityMaster list contains securities that did not exist but were created and set to default

        Raises:
            DatabaseError: if atomic transaction to save all positions fails
            ObjectDoesNotExist: if investment account not found
            ValueError: if a closed position is not expanded into lots
        """
        dp_dict = {}
        for f in ClosedPosition._meta.get_fields():
            if isinstance(f, models.DecimalField):
                dp_dict[f.name] = f.decimal_places

        df = pd.read_csv(file, names=list(range(14)))
        df.columns = df.loc[9]
        df = df[10:-2]

        try:
            found_lot_groups = df["Symbol"].value_counts().loc["ASSOCIATED LOTS"]
        except KeyError:
            found_lot_groups = 0

        df["Enter Date1"] = pd.to_datetime(df["Symbol"], format="%m/%d/%Y", errors="coerce").dt.date
        df["Close Date1"] = pd.to_datetime(df["Security Description"], format="%m/%d/%Y", errors="coerce").dt.date
        df.insert(0, "Enter Date", df[["Enter Date1", "Close Date1"]].min(axis=1))
        df.insert(1, "Close Date", df[["Enter Date1", "Close Date1"]].max(axis=1))
        df["Symbol"] = df["Symbol"].replace(["ASSOCIATED LOTS", "Date Acquired"], np.nan)
        df.loc[~df["Enter Date"].isnull(), "Symbol"] = np.nan

        exp_lot_groups = df["Symbol"].count()
        if found_lot_groups != exp_lot_groups:
            raise ValueError("Found " + str(found_lot_groups) + " lot groups but expected " + str(exp_lot_groups) +
                             ". At least one closed position was not expanded into lots.")

        df.insert(3, "Account ID", df["Account"])
        df.loc[df["Symbol"].isnull(), "Account ID"] = np.nan
        acc_rows = ~df["Account ID"].isnull()
        df.loc[acc_rows, "Account ID"] = df.loc[acc_rows, "Account ID"].str.split(" ").str[-1].map(
            lambda x: x[1:-1] if x[0] == "(" and x[-1] == ")" else np.nan)
        for col in ["Symbol", "Account ID"]:
            df[col] = df[col].ffill()
        df = df[~df["Enter Date"].isnull()]

        df = df.drop(columns=["Security Description", "Account", "Enter Date1", "Close Date1"])
        df = df.rename(columns={
            "Quantity": "quantity", "Basis/Share": "cost_basis_price", "Proceeds/Share": "proceeds_price",
            "Basis": "cost_basis_total", "Proceeds": "proceeds_total", "Short-Term G/L": "short_term_pnl",
            "Long-Term G/L": "long_term_pnl", "Unadj Basis/Share": "cost_basis_price_unadj",
            "Unadj Basis": "cost_basis_total_unadj", "Unadj Short-Term G/L": "short_term_pnl_unadj",
            "Unadj Long-Term G/L": "long_term_pnl_unadj"})
        for col in df.columns[4:]:
            df[col] = df[col].replace("--", "0").str.replace(",", "").map(lambda x: round(Decimal(x), dp_dict[col]))

        acc_dict = InvestmentAccount.objects.account_id_to_account_dict(
            df["Account ID"].drop_duplicates().tolist(), Broker.FIDELITY)
        sec_dict = SecurityMaster.objects.ticker_to_security_dict(df["Symbol"].drop_duplicates().tolist())
        sec_ns_list = []
        pos_list = []
        for ind, row in df.iterrows():
            try:
                inv_acc = acc_dict[row["Account ID"]]
            except KeyError:
                raise ObjectDoesNotExist("Account ID: " + row["Account ID"] + " does not exist as a " +
                                         str(Broker.FIDELITY) + " account")

            security = sec_dict.get(row["Symbol"], None)
            if security is None:
                security = SecurityMaster.objects.get_or_create_default(row["Symbol"])
                sec_ns_list.append(security)
                sec_dict[row["Symbol"]] = security

            pos_list.append(ClosedPosition.objects.full_constructor(
                inv_acc, row["Enter Date"], row["Close Date"], security, row["quantity"], row["cost_basis_price"],
                row["cost_basis_total"], row["proceeds_price"], row["proceeds_total"], row["short_term_pnl"],
                row["long_term_pnl"], row["cost_basis_price_unadj"], row["cost_basis_total_unadj"],
                row["short_term_pnl_unadj"], row["long_term_pnl_unadj"], create=False))

        with transaction.atomic():
            for pos in pos_list:
                pos.save()

        return pos_list, sec_ns_list

    @classmethod
    def load_closed_positions_from_file(cls, broker, file):
        """ Open file and create and return closed positions

        If a ticker/symbol is not found, a default SecurityMaster object for that ticker/symbol will be created

        Args:
            broker (Broker): load closed positions from this broker
            file (Union[str, django.core.files.base.File]): name of file in media directory
                /files/input/closedpositions/ or a File object.

        Returns:
            tuple[list[ClosedPosition], list[SecurityMaster]]: each ClosedPosition instance is saved to the database,
                SecurityMaster list contains securities that did not exist but were created and set to default

        Raises:
            DatabaseError: if a function called from this function raises a DatabaseError
            NotImplementedError: if broker not set in this function, if a function called from this function raises a
                NotImplementedError
            ObjectDoesNotExist: if a function called from this function raises a ObjectDoesNotExist
            ValidationError: if a function called from this function raises a ValidationError
            ValueError: if a function called from this function raises a ValueError

        See Also:
            load_closed_positions_from_fidelity_file()
        """
        if isinstance(file, str):
            file = settings.MEDIA_ROOT + "/files/input/closedpositions/" + file

        if broker == Broker.FIDELITY:
            return cls.load_closed_positions_from_fidelity_file(file)
        else:
            raise NotImplementedError("broker not set in load_closed_positions_from_file()")