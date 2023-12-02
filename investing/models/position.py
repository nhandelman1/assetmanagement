from decimal import Decimal
from typing import Union
import datetime

import numpy as np
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, models, transaction
import django_pandas.io
import pandas as pd

from ..models.closedposition import ClosedPosition
from ..models.investmentaccount import Broker, InvestmentAccount
from ..models.securitymaster import AssetClass, ChangeType, SecurityMaster, TickerHistory
from ..models.transaction import ActionType, Transaction, TransactionType
import util.pythonutil as PyUtil
import util.pandasutil as PdUtil


class PositionManager(models.Manager):
    def full_constructor(self, investment_account, eod_date, security, quantity, eod_price, market_value, enter_date,
                         enter_price, enter_total, enter_price_net, enter_total_net, cost_basis_price, cost_basis_total,
                         create=True):
        """ Instantiate Position instance with option to save to database

        Args:
            see Position class docstring
            create (bool): False to create instance only. Default True to also save to database (self.create)

        Returns:
            Position: instance
        """
        return (self.create if create else Position)(
            investment_account=investment_account, eod_date=eod_date, security=security, quantity=quantity,
            eod_price=eod_price, market_value=market_value, enter_date=enter_date, enter_price=enter_price,
            enter_total=enter_total, enter_price_net=enter_price_net, enter_total_net=enter_total_net,
            cost_basis_price=cost_basis_price, cost_basis_total=cost_basis_total)


class Position(models.Model):
    """ Position Model

    End of day portfolio positions by lot

    Attributes:
        investment_account (InvestmentAccount):
        eod_date (datetime.date): position as of this end of day date
        security (SecurityMaster):
        quantity (Decimal): can have partial shares
        eod_price (Decimal): actual close price at the end of day. NOT ADJUSTED
        market_value (Decimal): typically quantity * eod_price but this is not enforced
        enter_date (datetime.date): date this lot position was entered into
        enter_price (Decimal): price at which this position was entered into (before commission and fees)
        enter_total (Decimal): typically quantity * enter_price * contract size (or 1) but not enforced
        enter_price_net (Decimal): price at which this position was entered into (after commission and fees)
        enter_total_net (Decimal): typically quantity * enter_price_net * contract size (or 1) but not enforced
        cost_basis_price (Decimal): for long positions, this is the enter_price_net. for short positions, this isnt
            known until the position is closed so it is not required (but it should set once the position is closed).
        cost_basis_total (Decimal): typically quantity * cost_basis_price * contract size (or 1) but not enforced
    """

    investment_account = models.ForeignKey(InvestmentAccount, models.PROTECT)
    eod_date = models.DateField()
    security = models.ForeignKey(SecurityMaster, models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    eod_price = models.DecimalField(max_digits=9, decimal_places=4)
    market_value = models.DecimalField(max_digits=12, decimal_places=2)
    enter_date = models.DateField(blank=True, null=True, help_text="Required if broker breaks position into lots.")
    enter_price = models.DecimalField(max_digits=9, decimal_places=4)
    enter_total = models.DecimalField(max_digits=12, decimal_places=2)
    enter_price_net = models.DecimalField(max_digits=9, decimal_places=4)
    enter_total_net = models.DecimalField(max_digits=12, decimal_places=2)
    cost_basis_price = models.DecimalField(max_digits=9, decimal_places=4, blank=True, null=True)
    cost_basis_total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    objects = PositionManager()

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
    def generate_position_history(cls, broker, transfer_security_file=None):
        """ Generate missing daily end of day position history for all accounts with broker

        Only generated through most recent transaction per account to prevent positions from being generated without up
        to date transaction info.
        Only applied for account and date combinations where there are no positions, starting from account create date
        Fidelity default settings:
            lots are sold first in, first out (oldest sold first then moving to more recent)
            Core position is set to SPAXX
            Dividend/Capital Gain (re)investment policy: core position reinvests in itself, all other positions invest
                in core position
            Transfers without a security: these are cash transfers that fidelity immediately converts to core position
                but there is no transaction indicating this conversion. Assume price is 1 and quantity is amount_net
            Transfers with a security: these do not include enter_date, cost_basis_price and cost_basis_total;
                this function requires transfer_security_file be provided and have data to fill in these values

        Args:
            broker (Broker): generate position history for all accounts with this broker
            transfer_security_file (Union[str, django.core.files.base.File]): name of file in media directory
                /files/input/transactions/ or a File object. file is expected to be csv with columns
                "trans_date", "account_id", "ticker", "quantity", "enter_date", "cost_basis_price", "cost_basis_total".
                Dates can have any common format. account_id must be an existing account. Default None

        Returns:
            list[Position]: positions generated and sorted by end of day date, account, security ticker, enter date.

        Raises:
            ObjectDoesNotExist: if SPAXX security is not created before calling this function, if account_id in
                transfer_security_file not found
            ValueError: if a transfer with a security does not have a matching account_id and trans_date in
                transfer_security_file (or if the file is not provided but is required),
        """
        dp_dict = {}
        for f in Position._meta.get_fields():
            if isinstance(f, models.DecimalField):
                dp_dict[f.name] = f.decimal_places

        core_security = SecurityMaster.objects.get(ticker="SPAXX")

        cp_df = ClosedPosition.objects.filter(investment_account__broker=broker)
        cp_df = django_pandas.io.read_frame(cp_df, verbose=False)

        # must be ordered by trans_date increasing first. others are optional
        t_df = Transaction.objects.filter(investment_account__broker=broker).order_by(
            "trans_date", "investment_account", "security")
        t_df = django_pandas.io.read_frame(t_df, verbose=False)

        if any((t_df["trans_type"] == TransactionType.TRANSFER.value) & (~t_df["security"].isnull())) \
                and transfer_security_file is None:
            raise ValueError(
                "A transfer security file must be provided for enter date, cost basis price and cost basis total data "
                "for transferred securities. See " + TransactionType.TRANSFER.value + " transactions where a security "
                "is provided. The file must be csv with columns 'trans_date', 'account_id', 'ticker', 'quantity', "
                "'enter_date', 'cost_basis_price', 'cost_basis_total'. Dates can have any common format.")
        if isinstance(transfer_security_file, str):
            transfer_security_file = settings.MEDIA_ROOT + "/files/input/transactions/" + transfer_security_file
        if transfer_security_file is None:
            trans_sec_df = None
        else:
            trans_sec_df = pd.read_csv(transfer_security_file)
            if any(trans_sec_df["quantity"] < 0):
                raise ValueError("Need to check that security transfer with a negative quantity works as expected")
            for col in ["trans_date", "enter_date"]:
                trans_sec_df[col] = pd.to_datetime(trans_sec_df[col]).dt.date
            for col in ["quantity", "cost_basis_price", "cost_basis_total"]:
                trans_sec_df[col] = trans_sec_df[col].map(lambda x: round(Decimal(x), dp_dict[col]))
            trans_sec_df["account_id"] = trans_sec_df["account_id"].astype(str)

        inv_acc_dict = InvestmentAccount.objects.field_to_account_dict(
            "pk", t_df["investment_account"].drop_duplicates().tolist(), Broker.FIDELITY)
        # hard coded SPAXX. it's not likely another core position will be used
        sec_dict = SecurityMaster.objects.field_to_security_dict(
            "pk", pd.concat([t_df["security"], cp_df["security"]], ignore_index=True).drop_duplicates().dropna().
            astype("int64").tolist())

        ns_list = sorted([x.ticker for x in sec_dict.values() if x.asset_class == AssetClass.NOT_SET])
        if len(ns_list) > 0:
            raise ValueError("The following securities must have an asset class set before generating positions: " +
                             str(ns_list))

        t_df["security"] = t_df["security"].map(sec_dict)
        cp_df["security"] = cp_df["security"].map(sec_dict)

        pos_df = pd.DataFrame()
        for acc_pk, acc in inv_acc_dict.items():
            pos_df = pd.concat([pos_df, Position.generate_position_history_by_account(
                t_df, cp_df, trans_sec_df, acc, core_security, dp_dict)], ignore_index=True)

        # sort by specified return order before saving
        # positions generated and sorted by end of day date, account, security ticker, enter date.
        pos_df["ticker"] = pos_df["security"].map(lambda x: x.ticker)
        pos_df = pos_df.sort_values(by=["eod_date", "investment_account", "ticker", "enter_date"])
        save_pos_list = []
        with transaction.atomic():
            for ind, row in pos_df.iterrows():
                save_pos_list.append(Position.objects.full_constructor(
                    inv_acc_dict[row["investment_account"]], row["eod_date"], row["security"], row["quantity"],
                    row["eod_price"], row["market_value"], row["enter_date"], row["enter_price"], row["enter_total"],
                    row["enter_price_net"], row["enter_total_net"], row["cost_basis_price"], row["cost_basis_total"]))

        return save_pos_list

    @classmethod
    def generate_position_history_by_account(cls, trans_df, closed_pos_df, ts_df, inv_acc, core_security, dp_dict):
        """

        assumes df is sorted by trans_date increasing

        Args:
            trans_df:
            closed_pos_df:
            ts_df:
            inv_acc:
            core_security:

        Returns:

        """
        closed_pos_df = closed_pos_df[closed_pos_df["investment_account"] == inv_acc.pk]
        closed_pos_df["processed"] = False
        ts_df = ts_df[ts_df["account_id"] == inv_acc.account_id]

        # get the oldest and newest transaction dates here so the positions are created through the entire transaction
        # date range
        trans_df = trans_df[trans_df["investment_account"] == inv_acc.pk]
        oldest_trans_date = trans_df["trans_date"].min()
        newest_trans_date = trans_df["trans_date"].max()

        if oldest_trans_date < inv_acc.create_date:
            raise ValueError(str(inv_acc) + ": earliest transaction is on " + str(oldest_trans_date) +
                             ". This is before the account create_date of " + str(inv_acc.create_date))

        # always start at create date. earliest transaction in account history may be after the create date
        cur_date = inv_acc.create_date
        prev_date = PyUtil.change_dt_date(cur_date, biz_days=-1)

        # get all positions for account
        pos_df = django_pandas.io.read_frame(Position.objects.filter(investment_account=inv_acc), verbose=False)
        sec_dict = SecurityMaster.objects.field_to_security_dict(
            "pk", pos_df["security"].drop_duplicates().dropna().astype("int64").tolist())
        pos_df["security"] = pos_df["security"].map(sec_dict)
        # positions with save == True are positions that will be saved to database. these could be new positions
        # or existing positions that are being updated (e.g. cost basis for short positions after they are closed)
        pos_df["save"] = False
        # create a fake position for day before create date as a starting point
        pos_df = PdUtil.ins_row_at_end(
            pos_df, [None, inv_acc.id, prev_date, core_security, Decimal(0), Decimal(1), Decimal(0), None, Decimal(1),
                     Decimal(0), Decimal(1), Decimal(0), Decimal(1), Decimal(0), False])

        # remove transactions where positions already exist for transaction's date
        trans_df = trans_df[~trans_df["trans_date"].isin(pos_df["eod_date"].drop_duplicates())]

        while cur_date <= newest_trans_date:
            if cur_date in pos_df["eod_date"]:
                prev_date, cur_date = cur_date, PyUtil.change_dt_date(cur_date, biz_days=1)
                continue

            # get transactions and starting positions for cur_date
            # use .copy() to get rid of pandas SettingWithCopyWarning
            cur_trans_df = trans_df[trans_df["trans_date"] == cur_date].copy()
            # sort by mergers then distribution then all other transactions
            cur_trans_df["sort"] = cur_trans_df.apply(
                lambda row: 0 if row["trans_type"] == TransactionType.CORP_ACT.value and
                                 row["action_type"] in (ActionType.MERGER_NEW.value, ActionType.MERGER_OLD.value)
                else 1 if row["trans_type"] == TransactionType.CORP_ACT.value and row["action_type"] in
                          (ActionType.STOCK_SPLIT.value, ActionType.STOCK_CONS.value, ActionType.STOCK_DIV.value)
                else 2, axis=1)
            cur_trans_df = cur_trans_df.sort_values(by="sort").drop(columns=["sort"])

            cur_pos_df = pos_df[pos_df["eod_date"] == prev_date].copy()
            cur_pos_df[["id", "eod_date", "save"]] = [None, cur_date, True]
            sec_sold_list = []
            sec_split_list = []
            sec_covered_list = []

            def add_pos(sec1, qty1, eodp1, mv1, ed1, ep1, et1, epn1, etn1, cbp1, cbt1):
                nonlocal cur_pos_df

                # TODO remove this line once market_value is set correctly
                mv1 = max(mv1, Decimal(-123456789))

                cur_pos_df = PdUtil.ins_row_at_end(
                    cur_pos_df, [None, inv_acc.id, cur_date, sec1, qty1, eodp1, mv1, ed1, ep1, et1, epn1, etn1, cbp1,
                                 cbt1, True])

            def add_core_sec_pos(amt1):
                add_pos(core_security, amt1, Decimal(1), amt1, None, Decimal(1), amt1, Decimal(1), amt1, Decimal(1),
                        amt1)

            # TODO will also need to change any options on the split stock
            def process_split(trans_sec_1):
                # there may be multiple split transactions on the same security. not clear how to match each
                # split transaction to a current position. get total quantities for security from current
                # positions and split transactions to calculate split ratio. apply split ratio to current
                # positions quantity and cost_basis_price
                if trans_sec_1 not in sec_split_list:
                    sec_split_list.append(trans_sec_1)

                    split_rows = cur_pos_df["security"] == trans_sec_1
                    sec_qty = cur_pos_df.loc[split_rows, "quantity"].sum()
                    split_qty = cur_trans_df.loc[
                        (cur_trans_df["trans_type"] == TransactionType.CORP_ACT.value) &
                        (cur_trans_df["action_type"] == ActionType.STOCK_SPLIT.value) &
                        (cur_trans_df["security"] == trans_sec_1), "quantity"].sum()
                    split_ratio = split_qty / sec_qty + 1
                    cur_pos_df.loc[split_rows, "quantity"] = (cur_pos_df.loc[split_rows, "quantity"] * split_ratio)\
                        .map(lambda x: round(x, dp_dict["quantity"]))
                    for col in ["enter_price", "enter_price_net", "cost_basis_price"]:
                        cur_pos_df.loc[split_rows, col] = (cur_pos_df.loc[split_rows, col] / split_ratio)\
                            .map(lambda x: round(x, dp_dict[col]))

            def process_buy(trans_sec_1, trans_qty_1, trans_price_1, trans_amt_net_1):
                # create the position. this is an actual lot if the security uses lots otherwise it is a
                # dummy lot that will be aggregated later
                # trans_price_1 is before commission and fees. trans_amt_net_1 is after commission and fees
                # cost_basis_price/total are after commission and fees
                trans_amt_net_1 = abs(trans_amt_net_1)
                contract_size_1 = 1 if trans_sec_1.contract_size is None else trans_sec_1.contract_size
                eod_price_1 = Decimal(1) if trans_sec_1 == core_security else Decimal("-12345.6789")
                enter_price_net_1 = round(trans_amt_net_1 / trans_qty_1 / contract_size_1, dp_dict["enter_price_net"])

                add_pos(trans_sec_1, trans_qty_1, eod_price_1,
                        round(trans_qty_1 * eod_price_1 * contract_size_1, dp_dict["market_value"]),
                        cur_date if trans_sec_1.has_fidelity_lots else None, trans_price_1,
                        round(trans_qty_1 * trans_price_1 * contract_size_1, dp_dict["enter_total"]),
                        enter_price_net_1, trans_amt_net_1, enter_price_net_1, trans_amt_net_1)

                # remove cash from core position
                add_core_sec_pos(-trans_amt_net_1)

            def process_sell(trans_sec_1, trans_amt_net_1):
                # there may be multiple sell transactions on the same security. not clear how to match each
                # sell transaction to the closed positions for that transaction. just process all the closed
                # positions for the security at once and prevent the program from doing it again
                # this also covers the case where there are more closed positions than sell transactions

                # add cash to core position
                add_core_sec_pos(abs(trans_amt_net_1))

                if trans_sec_1 in sec_sold_list:
                    return
                sec_sold_list.append(trans_sec_1)

                cur_cp_df_1 = closed_pos_df[(closed_pos_df["close_date"] == cur_date) &
                                            (closed_pos_df["security"] == trans_sec_1) &
                                            (closed_pos_df["processed"] == False)]
                for cp_ind, cp_row in cur_cp_df_1.iterrows():
                    for pos_ind, pos_row in cur_pos_df.iterrows():
                        # cost_basis_price in position is from the original transaction (before wash sale adjustment)
                        # but cost_basis_price in closed position is after wash sale adjustment. cost_basis_price_unadj
                        # in closed position is before wash sale adjustment so it will match original transaction cost
                        # basis price
                        # partial shares cost basis price are not matching within 0.001 due to rounding issues so
                        # allow for greater tolerance for partial shares only
                        if pos_row["security"] == cp_row["security"] and pos_row["enter_date"] == cp_row["enter_date"]\
                                and pos_row["cost_basis_price"] is not None:
                            diff = abs(pos_row["cost_basis_price"] - cp_row["cost_basis_price_unadj"])
                            if diff < Decimal("0.001") or (cp_row["quantity"] < Decimal(1) and diff < Decimal("0.02")):
                                qty, cbt = cp_row[["quantity", "cost_basis_total_unadj"]]
                                # position enter_total is before commission and fees but all closed position fields are
                                # after commission and fees. use ratio of quantity sold to quantity held before sale to
                                # get enter_total after sale
                                cur_pos_df.loc[pos_ind, "enter_total"] -= \
                                    round(pos_row["enter_total"] * qty/pos_row["quantity"], dp_dict["enter_total"])
                                # for long positions, enter_total_net and cost_basis_total are the same
                                cur_pos_df.loc[pos_ind, ["quantity", "enter_total_net", "cost_basis_total"]] -= \
                                    (qty, cbt, cbt)
                                closed_pos_df.loc[cp_ind, "processed"] = True
                                break

            def process_sell_short(trans_sec_1, trans_qty_1, trans_price_1, trans_amt_net_1):
                # create the position. this is an actual lot if the security uses lots otherwise it is a
                # dummy lot that will be aggregated later
                # cost_basis_price and cost_basis_total are None because the values aren't known until the
                # position is closed
                contract_size_1 = 1 if trans_sec_1.contract_size is None else trans_sec_1.contract_size
                eod_price_1 = Decimal(1) if trans_sec_1 == core_security else Decimal("-12345.6789")
                enter_price_net_1 = round(trans_amt_net_1 / abs(trans_qty_1) / contract_size_1,
                                          dp_dict["enter_price_net"])
                add_pos(trans_sec_1, trans_qty_1, eod_price_1,
                        round(abs(trans_qty_1) * eod_price_1 * contract_size_1, dp_dict["market_value"]),
                        cur_date if trans_sec_1.has_fidelity_lots else None, trans_price_1,
                        round(abs(trans_qty_1) * trans_price_1 * contract_size_1, dp_dict["enter_total"]),
                        enter_price_net_1, trans_amt_net_1, None, None)

                # add cash to core position
                add_core_sec_pos(trans_amt_net_1)

            def process_buy_cover(trans_sec_1, trans_amt_net_1):
                # remove cash from core position
                add_core_sec_pos(trans_amt_net_1)

                if trans_sec_1 in sec_covered_list:
                    return
                sec_covered_list.append(trans_sec_1)

                cur_cp_df_1 = closed_pos_df[(closed_pos_df["close_date"] == cur_date) &
                                            (closed_pos_df["security"] == trans_sec_1) &
                                            (closed_pos_df["processed"] == False)]
                for cp_ind, cp_row in cur_cp_df_1.iterrows():
                    for pos_ind, pos_row in cur_pos_df.iterrows():
                        # cost_basis_price in position is from the original transaction (before wash sale adjustment)
                        # but cost_basis_price in closed position is after wash sale adjustment. cost_basis_price_unadj
                        # in closed position is before wash sale adjustment so it will match original transaction cost
                        # basis price

                        if pos_row["security"] == cp_row["security"] and pos_row["enter_date"] == cp_row["enter_date"] \
                                and abs(pos_row["enter_price_net"] - cp_row["enter_price_net"]) < \
                                Decimal("0.001"):
                            qty = cp_row["quantity"]
                            cur_pos_df.loc[pos_ind, "quantity"] += qty
                            # position enter_total is before commission and fees but all closed position fields are
                            # after commission and fees. use ratio of quantity sold to quantity held before sale to get
                            # enter_total after sale
                            cur_pos_df.loc[pos_ind, "enter_total"] -= \
                                round(pos_row["enter_total"] * qty / abs(pos_row["quantity"]), dp_dict["enter_total"])
                            cur_pos_df.loc[pos_ind, "enter_total_net"] -= cp_row["proceeds_total"]
                            closed_pos_df.loc[cp_ind, "processed"] = True
                            # TODO update cost_basis_price and cost_basis_total for current and previous positions
                            # TODO if not all quantity of the position is sold, will need to keep the cost basis values
                            # TODO as None for the non sold quantity and create a new lot for the sold quantity with
                            # TODO closed cost basis values. save needs to be set to True on previous positions
                            break

            def process_transfer_security(sec_1, qty_1, cost_basis_price_1, cost_basis_total_1,
                                          enter_date_1):
                # cost_basis_price_1 and cost_basis_total_1 are cost basis values after commission and fees. values
                # before commission and fees are not provided during transfer
                contract_size_1 = 1 if sec_1.contract_size is None else sec_1.contract_size
                eod_price_1 = Decimal(1) if sec_1 == core_security else Decimal("-12345.6789")
                add_pos(sec_1, qty_1, eod_price_1, round(qty_1 * eod_price_1 * contract_size_1,dp_dict["market_value"]),
                        enter_date_1 if sec_1.has_fidelity_lots else None, cost_basis_price_1, cost_basis_total_1,
                        cost_basis_price_1, cost_basis_total_1, cost_basis_price_1, cost_basis_total_1)

            def process_merger(trans_sec_1, trans_date_1):
                nonlocal cur_pos_df
                th = TickerHistory.objects.get(security=trans_sec_1, change_date=trans_date_1,
                                               change_type=ChangeType.MERGER)
                ticker_srs = cur_pos_df["security"].map(lambda x: x.ticker)
                cur_pos_df.loc[ticker_srs == th.old_ticker, "security"] = trans_sec_1

            # iterate transactions and change cur_pos_df as you go
            for ind, row in cur_trans_df.iterrows():
                if row["trans_type"] == TransactionType.CORP_ACT.value:
                    if row["action_type"] == ActionType.DIV.value:
                        add_core_sec_pos(row["amount_net"])
                    elif row["action_type"] == ActionType.MERGER_NEW:
                        process_merger(row["security"], row["trans_date"])
                    elif row["action_type"] == ActionType.MERGER_OLD:
                        # MERGER_NEW will handle the changes around mergers
                        pass
                    elif row["action_type"] == ActionType.STOCK_SPLIT.value:
                        process_split(row["security"])
                    else:
                        raise ValueError(row["action_type"] + " not implemented for " + TransactionType.CORP_ACT.value +
                                         " transaction")
                elif row["trans_type"] == TransactionType.OTHER.value:
                    if row["action_type"] == ActionType.OPT_EXP:
                        # amount_net is 0 so a core position of 0 will be created.
                        if row["quantity"] < 0:
                            process_sell(row["security"], row["amount_net"])
                        else:
                            process_buy_cover(row["security"], row["amount_net"])
                    elif row["action_type"] == ActionType.LOAN:
                        # these have no effect on positions
                        pass
                    else:
                        raise ValueError(row["action_type"] + " not implemented for " + TransactionType.OTHER.value +
                                         " transaction")
                elif row["trans_type"] == TransactionType.TRADE.value:
                    if row["action_type"] == ActionType.BUY.value:
                        process_buy(row["security"], row["quantity"], row["price"], row["amount_net"])
                    elif row["action_type"] == ActionType.SELL.value:
                        process_sell(row["security"], row["amount_net"])
                    elif row["action_type"] == ActionType.SELL_SHORT.value:
                        process_sell_short(row["security"], row["quantity"], row["price"], row["amount_net"])
                    elif row["action_type"] == ActionType.BUY_COVER.value:
                        process_buy_cover(row["security"], row["amount_net"])
                    else:
                        raise ValueError(row["action_type"] + " not implemented for " + TransactionType.TRADE.value +
                                         " transaction")
                elif row["trans_type"] == TransactionType.TRANSFER.value:
                    if pd.isnull(row["security"]):
                        # cash transfers go straight to core security at price = cost_basis_price = 1 and
                        # quantity = cost_basis_total = amount_net
                        add_core_sec_pos(row["amount_net"])
                    else:
                        sec_ts_df = ts_df[
                            (ts_df["trans_date"] == row["trans_date"]) & (ts_df["account_id"] == inv_acc.account_id) &
                            (ts_df["ticker"] == row["security"].ticker)]
                        for ts_ind, ts_row in sec_ts_df.iterrows():
                            process_transfer_security(row["security"], ts_row["quantity"], ts_row["cost_basis_price"],
                                                      ts_row["cost_basis_total"], ts_row["enter_date"])

            # aggregate positions by lot
            no_lot_df, lot_df = PdUtil.split_df_rows(cur_pos_df, cur_pos_df["enter_date"].isnull())
            no_lot_df = no_lot_df.groupby(
                by=["id", "investment_account", "eod_date", "security", "enter_date"], as_index=False, dropna=False)\
                .agg({"quantity": "sum", "eod_price": "first", "market_value": "sum", "enter_price": "first",
                      "enter_total": "sum", "enter_price_net": "first", "enter_total_net": "sum",
                      "cost_basis_price": "first", "cost_basis_total": "sum", "save": "first"})
            lot_df = lot_df[lot_df["quantity"] != Decimal(0)]
            cur_pos_df = pd.concat([no_lot_df, lot_df], ignore_index=True)

            # add new positions to pos_df. they will be used on the next day
            pos_df = pd.concat([pos_df, cur_pos_df], ignore_index=True)

            prev_date, cur_date = cur_date, PyUtil.change_dt_date(cur_date, biz_days=1)

        # TODO eod_price and market_value (at least for stocks, probably wont have option data so use dummy value)
        # TODO set eod price and calculate eod market value here for now
        pos_df["eod_price"] = Decimal("-12345.6789")
        pos_df.loc[pos_df["security"] == core_security, "eod_price"] = 1
        pos_df["market_value"] = pos_df.apply(
            lambda row: round((Decimal(1) if row["security"].contract_size is None else row["security"].contract_size) *
                              row["quantity"] * row["eod_price"], dp_dict["market_value"]), axis=1)

        pos_df = pos_df[pos_df["save"] == True]
        pos_df["enter_date"] = pos_df["enter_date"].replace({np.nan: None})

        return pos_df

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
        """
        dp_dict = {}
        for f in Position._meta.get_fields():
            if f.name == "quantity":
                dp_dict["Lot Quantity"] = f.decimal_places
            elif f.name == "eod_price":
                dp_dict["Last Price"] = f.decimal_places
            elif f.name == "market_value":
                dp_dict["Market Value"] = f.decimal_places
            elif f.name == "cost_basis_total":
                dp_dict["Cost Basis Total"] = f.decimal_places
            elif f.name == "cost_basis_price":
                dp_dict["Cost Basis Price"] = f.decimal_places
            elif f.name == "enter_total":
                dp_dict["Enter Total"] = f.decimal_places
            elif f.name == "enter_total_net":
                dp_dict["Enter Total Net"] = f.decimal_places
            elif f.name == "enter_price":
                dp_dict["Enter Price"] = f.decimal_places
            elif f.name == "enter_price_net":
                dp_dict["Enter Price Net"] = f.decimal_places

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
        df["Enter Price"] = df["Cost Basis Price"]
        df["Enter Total"] = df["Cost Basis Total"]

        acc_dict = InvestmentAccount.objects.field_to_account_dict(
            "account_id", df["Account ID"].drop_duplicates().tolist(), Broker.FIDELITY)
        sec_dict = SecurityMaster.objects.field_to_security_dict("ticker", df["Ticker"].drop_duplicates().tolist())
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
                eod_price=row["Last Price"], market_value=row["Market Value"], enter_date=row["Purchase Date"],
                enter_price=row["Enter Price"], enter_total=row["Enter Total"], enter_price_net=row["Enter Price Net"],
                enter_total_net=row["Enter Total Net"], cost_basis_price=row["Cost Basis Price"],
                cost_basis_total=row["Cost Basis Total"]))

        with transaction.atomic():
            for pos in pos_list:
                pos.save()

        return pos_list, sec_ns_list
        """
        raise NotImplementedError("Fidelity position file does not provide information that can be used to reliably "
                                  "set enter_price and enter_total. Positions must be generated using "
                                  "generate_position_history().")

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
