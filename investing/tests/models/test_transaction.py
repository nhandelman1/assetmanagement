from decimal import Decimal
import datetime

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ...models.investmentaccount import Broker
from ...models.transaction import ActionType, Transaction, TransactionType
from .test_investmentaccount import InvestmentAccountTests
from .test_securitymaster import SecurityMasterTests
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class TransactionTests(DjangoModelTestCaseBase):

    def equal(self, model1: Transaction, model2: Transaction):
        InvestmentAccountTests().equal(model1.investment_account, model2.investment_account)
        if model1.security is not None or model2.security is not None:
            SecurityMasterTests().equal(model1.security, model2.security)
        self.simple_equal(model1, model2, Transaction, rem_attr_list=["investment_account", "security"])

    def test_action_type_get_transaction_type(self):
        # all ActionType enums are set in get_transaction_type()
        for action_type in ActionType:
            ActionType.get_transaction_type(action_type)

    def test_transaction_type_get_action_types(self):
        # all TransactionType enums are set in get_action_types()
        for trans_type in TransactionType:
            TransactionType.get_action_types(trans_type)

        # check get_action_types() return format
        action_types = TransactionType.get_action_types(TransactionType.INTEREST)
        self.assertEqual(action_types, (ActionType.COUP_PMT, ActionType.INT_PMT))

    def test_save_clean(self):
        trans = TransactionTests.transaction_transfer_wire_transfer()

        trans.action_type = ActionType.BUY
        with self.assertRaises(ValidationError):
            trans.save()

        with self.assertRaises(ValidationError):
            trans.clean_fields()

        trans.trans_type = TransactionType.TRADE
        with self.assertRaises(ValidationError):
            trans.save()

        with self.assertRaises(ValidationError):
            trans.clean_fields()

    def test_load_transactions_from_fidelity_file(self):
        self.maxDiff = None

        with self.subTest():
            # accounts not created
            with self.assertRaises(ObjectDoesNotExist):
                Transaction.load_transactions_from_file(Broker.FIDELITY, "test transactions.csv")

        with self.subTest():
            # DISTRIBUTION description but quantity is 0
            with self.assertRaises(ValueError):
                Transaction.load_transactions_from_file(Broker.FIDELITY, "test transactions distribution fail.csv")

        with self.subTest():
            # description does not match with transaction type and action type
            with self.assertRaises(ValueError):
                Transaction.load_transactions_from_file(Broker.FIDELITY, "test transactions description fail.csv")

        inv_acc_fid_ind = InvestmentAccountTests.inv_acc_fidelity_individual()
        InvestmentAccountTests.inv_acc_fidelity_roth()

        with self.subTest():
            # earliest transaction is before account create date
            with self.assertRaises(ValueError):
                Transaction.load_transactions_from_file(
                    Broker.FIDELITY, "test transactions before create date fail.csv")

        SecurityMasterTests.sm_aapl()
        SecurityMasterTests.sm_aapl_call()
        SecurityMasterTests.sm_aapl_put()
        SecurityMasterTests.sm_msft()

        trans_list, sec_ns_list, exist_inv_acc_dates_set = Transaction.load_transactions_from_file(
            Broker.FIDELITY, "test transactions.csv")

        with self.subTest():
            self.equal(trans_list[0], TransactionTests.transaction_transfer_wire_transfer())
        with self.subTest():
            self.equal(trans_list[1], TransactionTests.transaction_trade_reinvestment())
        with self.subTest():
            self.equal(trans_list[2], TransactionTests.transaction_corp_act_dividend_received())
        with self.subTest():
            self.equal(trans_list[3], TransactionTests.transaction_transfer_money_line_paid())
        with self.subTest():
            self.equal(trans_list[4], TransactionTests.transaction_trade_sell())
        with self.subTest():
            self.equal(trans_list[5], TransactionTests.transaction_trade_buy())
        with self.subTest():
            self.equal(trans_list[6], TransactionTests.transaction_transfer_money_line_received())
        with self.subTest():
            self.equal(trans_list[7], TransactionTests.transaction_transfer_contrib_current_year())
        with self.subTest():
            self.equal(trans_list[8], TransactionTests.transaction_other_expired_call())
        with self.subTest():
            self.equal(trans_list[9], TransactionTests.transaction_trade_buy_cover())
        with self.subTest():
            self.equal(trans_list[10], TransactionTests.transaction_transfer_transferred_to())
        with self.subTest():
            self.equal(trans_list[11], TransactionTests.transaction_corp_act_stock_split())
        with self.subTest():
            self.equal(trans_list[12], TransactionTests.transaction_corp_act_stock_cons())
        with self.subTest():
            self.equal(trans_list[13], TransactionTests.transaction_transfer_rollover())
        with self.subTest():
            self.equal(trans_list[14], TransactionTests.transaction_trade_sell_short())
        with self.subTest():
            self.equal(trans_list[15], TransactionTests.transaction_transfer_contrib_prior_year())
        with self.subTest():
            self.equal(trans_list[16], TransactionTests.transaction_transfer_transfer_of_assets_rescredit())
        with self.subTest():
            self.equal(trans_list[17], TransactionTests.transaction_transfer_transfer_of_assets_receive())
        with self.subTest():
            self.equal(trans_list[18], TransactionTests.transaction_transfer_security())
        with self.subTest():
            self.equal(trans_list[19], TransactionTests.transaction_corp_act_merger_old())
        with self.subTest():
            self.equal(trans_list[20], TransactionTests.transaction_corp_act_merger_new())
        with self.subTest():
            self.equal(trans_list[21], TransactionTests.transaction_other_loan_returned())
        with self.subTest():
            self.equal(trans_list[22], TransactionTests.transaction_other_loan_loan())
        with self.subTest():
            self.equal(trans_list[23], TransactionTests.transaction_other_loan_mark())
        with self.subTest():
            self.equal(trans_list[24], TransactionTests.transaction_other_fee())
        with self.subTest():
            self.equal(trans_list[25], TransactionTests.transaction_interest_interest())
        with self.subTest():
            self.assertEqual(len(sec_ns_list), 1)
            SecurityMasterTests().equal(sec_ns_list[0], SecurityMasterTests.sm_spaxx(has_fidelity_lots=True))
        with self.subTest():
            self.assertEqual(len(exist_inv_acc_dates_set), 0)

        trans_list, sec_ns_list, exist_inv_acc_dates_set = Transaction.load_transactions_from_file(
            Broker.FIDELITY, "test transactions duplicate.csv")

        with self.subTest():
            self.assertEqual(len(trans_list), 1)
        with self.subTest():
            self.assertEqual(len(sec_ns_list), 0)
        with self.subTest():
            # update expected number of transactions when number of transactions in "test transactions.csv" changes
            self.assertEqual(len(exist_inv_acc_dates_set), 1)
            self.assertEqual(list(exist_inv_acc_dates_set)[0], (inv_acc_fid_ind, datetime.date(2023, 10, 27)))

    @staticmethod
    def transaction_corp_act_dividend_received():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2023, 9, 27),
            trans_type=TransactionType.CORP_ACT, action_type=ActionType.DIV, description="DIVIDEND RECEIVED",
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal(0), price=Decimal(0),
            amount_net=Decimal("70.94"), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_corp_act_merger_new():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 6),
            trans_type=TransactionType.CORP_ACT, action_type=ActionType.MERGER_NEW,
            description="MERGER MER FROM MSFT#REOR M0051542700001", security=SecurityMasterTests.sm_aapl(),
            quantity=Decimal(100), price=Decimal(0), amount_net=Decimal(0), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_corp_act_merger_old():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 6),
            trans_type=TransactionType.CORP_ACT, action_type=ActionType.MERGER_OLD,
            description="MERGER MER PAYOUT #REOR M0051542700000", security=SecurityMasterTests.sm_msft(),
            quantity=Decimal(-100), price=Decimal(0), amount_net=Decimal(0), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_corp_act_stock_cons():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 9),
            trans_type=TransactionType.CORP_ACT, action_type=ActionType.STOCK_CONS, description="DISTRIBUTION",
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("-5.00"), price=Decimal(0), amount_net=Decimal(0),
            commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_corp_act_stock_split():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 9),
            trans_type=TransactionType.CORP_ACT, action_type=ActionType.STOCK_SPLIT, description="DISTRIBUTION",
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("7.00"), price=Decimal(0), amount_net=Decimal(0),
            commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_interest_interest():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 6),
            trans_type=TransactionType.INTEREST, action_type=ActionType.INT_PMT, description="INTEREST",
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal(0), price=Decimal(0), amount_net=Decimal("3.04"),
            commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_other_expired_call():
        # transaction in file is 2022-09-19 but the program changes it to 2022-09-16 to match expiry
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 16),
            trans_type=TransactionType.OTHER, action_type=ActionType.OPT_EXP,
            description="EXPIRED CALL (AAPL) PROSHARES ULTRAPRO SEP 16 22 $41.5",
            security=SecurityMasterTests.sm_aapl_call(), quantity=Decimal("12.00"), price=Decimal(0),
            amount_net=Decimal(0), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_other_fee():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 6),
            trans_type=TransactionType.OTHER, action_type=ActionType.FEE, description="FEE CHARGED",
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal(0), price=Decimal(0), amount_net=Decimal("-4.59"),
            commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_other_loan_returned():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 6),
            trans_type=TransactionType.OTHER, action_type=ActionType.LOAN,
            description="LOAN RETURNED YOU RETURNED VS Z21-323368-1", security=SecurityMasterTests.sm_aapl(),
            quantity=Decimal("-107"), price=Decimal(0), amount_net=Decimal(0), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_other_loan_loan():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 6),
            trans_type=TransactionType.OTHER, action_type=ActionType.LOAN, description="YOU LOANED VS Z21-323368-1",
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("107"), price=Decimal(0), amount_net=Decimal(0),
            commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_other_loan_mark():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 6),
            trans_type=TransactionType.OTHER, action_type=ActionType.LOAN,
            description="INCREASE COLLATERAL MARK TO MARKET ADJ", security=SecurityMasterTests.sm_aapl(),
            quantity=Decimal("13033"), price=Decimal(0), amount_net=Decimal(0), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_trade_buy():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2023, 2, 21),
            trans_type=TransactionType.TRADE, action_type=ActionType.BUY, description="YOU BOUGHT",
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("21.00"), price=Decimal("36.2936"),
            amount_net=Decimal("-762.17"), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_trade_buy_cover():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 12),
            trans_type=TransactionType.TRADE, action_type=ActionType.BUY_COVER,
            description="YOU BOUGHT CLOSING TRANSACTION",
            security=SecurityMasterTests.sm_aapl_put(), quantity=Decimal("14.00"), price=Decimal("0.11"),
            amount_net=Decimal("-154.41"), commission=Decimal(0), fees=Decimal("0.41"))

    @staticmethod
    def transaction_trade_reinvestment():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2023, 9, 29),
            trans_type=TransactionType.TRADE, action_type=ActionType.BUY, description="REINVESTMENT REINVEST @ $1.000",
            security=SecurityMasterTests.sm_spaxx(has_fidelity_lots=True), quantity=Decimal("1.28"), price=Decimal(1),
            amount_net=Decimal("-1.28"), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_trade_sell():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_individual(),
            trans_date=datetime.date(2023, 6, 30), trans_type=TransactionType.TRADE, action_type=ActionType.SELL,
            description="YOU SOLD", security=SecurityMasterTests.sm_msft(), quantity=Decimal("-74.00"),
            price=Decimal("89.75"), amount_net=Decimal("6641.44"), commission=Decimal(0), fees=Decimal("0.06"))

    @staticmethod
    def transaction_trade_sell_short():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 8),
            trans_type=TransactionType.TRADE, action_type=ActionType.SELL_SHORT,
            description="YOU SOLD OPENING TRANSACTION", security=SecurityMasterTests.sm_aapl_put(),
            quantity=Decimal("-14.00"), price=Decimal("0.70"), amount_net=Decimal("970.46"), commission=Decimal("9.1"),
            fees=Decimal("0.44"))

    @staticmethod
    def transaction_transfer_contrib_current_year():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2023, 1, 30),
            trans_type=TransactionType.TRANSFER, action_type=ActionType.TRANSFER,
            description="CONTRIB CURRENT YR CASH CONTRB CURR YR ER46855432 /WEB", security=None, quantity=Decimal(0),
            price=Decimal(0), amount_net=Decimal("560.00"), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_transfer_contrib_prior_year():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 8),
            trans_type=TransactionType.TRANSFER, action_type=ActionType.TRANSFER,
            description="CONTRIB PRIOR YEAR CASH CONTRIB PRIOR YER70674865 /WEB", security=None, quantity=Decimal(0),
            price=Decimal(0), amount_net=Decimal("6000.00"), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_transfer_money_line_paid():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_individual(),
            trans_date=datetime.date(2023, 8, 28), trans_type=TransactionType.TRANSFER, action_type=ActionType.TRANSFER,
            description="MONEY LINE PAID EFT FUNDS PAID ED07172945 /WEB", security=None, quantity=Decimal(0),
            price=Decimal(0), amount_net=Decimal("-3000.00"), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_transfer_money_line_received():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_individual(),
            trans_date=datetime.date(2023, 1, 31), trans_type=TransactionType.TRANSFER, action_type=ActionType.TRANSFER,
            description="MONEY LINE RECEIVED EFT FUNDS RECEIVED ER47281080 /WEB", security=None, quantity=Decimal(0),
            price=Decimal(0), amount_net=Decimal("25.00"), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_transfer_rollover():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 9),
            trans_type=TransactionType.TRANSFER, action_type=ActionType.TRANSFER,
            description="ROLLOVER CASH DIRECT ROLLOVER FROM FIRSCO PLAN 38452 HARBOR FINANCIAL", security=None,
            quantity=Decimal(0), price=Decimal(0), amount_net=Decimal("1042.27"), commission=Decimal(0),
            fees=Decimal(0))

    @staticmethod
    def transaction_transfer_security():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(),
            trans_date=datetime.date(2022, 9, 6), trans_type=TransactionType.TRANSFER,
            action_type=ActionType.TRANSFER, description="RECEIVED FROM YOU", security=SecurityMasterTests.sm_aapl(),
            quantity=Decimal(100), price=Decimal(0), amount_net=Decimal(0), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_transfer_transferred_to():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_individual(),
            trans_date=datetime.date(2022, 9, 12), trans_type=TransactionType.TRANSFER, action_type=ActionType.TRANSFER,
            description="TRANSFERRED TO VS 237-198406-1 CURRENT CONTRIBUTION", security=None, quantity=Decimal(0),
            price=Decimal(0), amount_net=Decimal("-4000.00"), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_transfer_transfer_of_assets_receive():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 6),
            trans_type=TransactionType.TRANSFER, action_type=ActionType.TRANSFER,
            description="TRANSFER OF ASSETS ACAT RECEIVE", security=None, quantity=Decimal(0), price=Decimal(0),
            amount_net=Decimal("32360.42"), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_transfer_transfer_of_assets_rescredit():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), trans_date=datetime.date(2022, 9, 7),
            trans_type=TransactionType.TRANSFER, action_type=ActionType.TRANSFER,
            description="TRANSFER OF ASSETS ACAT RES.CREDIT", security=None, quantity=Decimal(0), price=Decimal(0),
            amount_net=Decimal("2.49"), commission=Decimal(0), fees=Decimal(0))

    @staticmethod
    def transaction_transfer_wire_transfer():
        return Transaction(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_individual(),
            trans_date=datetime.date(2023, 10, 27), trans_type=TransactionType.TRANSFER,
            action_type=ActionType.TRANSFER, description="WIRE TRANS FROM BANK WR45932686", security=None,
            quantity=Decimal(0), price=Decimal(0), amount_net=Decimal("3056.87"), commission=Decimal(0),
            fees=Decimal(0))
