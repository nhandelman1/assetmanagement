from decimal import Decimal
import datetime

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ...models.closedposition import ClosedPosition
from ...models.investmentaccount import Broker
from ...models.position import Position
from ...models.transaction import Transaction
from .test_investmentaccount import InvestmentAccountTests
from .test_securitymaster import SecurityMasterTests
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class PositionTests(DjangoModelTestCaseBase):

    def equal(self, model1: Position, model2: Position):
        InvestmentAccountTests().equal(model1.investment_account, model2.investment_account)
        SecurityMasterTests().equal(model1.security, model2.security)
        self.simple_equal(model1, model2, Position, rem_attr_list=["investment_account", "security"])

    def test_save_clean(self):
        pos = PositionTests.position_fidelity_roth_aapl_20220907_680()
        pos.enter_date = None

        with self.assertRaises(ValidationError):
            pos.save()

        with self.assertRaises(ValidationError):
            pos.clean_fields()

    def test_generate_position_history(self):
        self.maxDiff = None

        InvestmentAccountTests.inv_acc_fidelity_roth()

        # create security masters used in the position generation
        SecurityMasterTests.sm_aapl()
        SecurityMasterTests.sm_aapl_put()
        SecurityMasterTests.sm_aapl_call()
        SecurityMasterTests.sm_msft()
        SecurityMasterTests.sm_nvda_set()
        SecurityMasterTests.sm_spaxx_set()

        # positions are generated from transactions, closed positions and transfer data file
        Transaction.load_transactions_from_file(Broker.FIDELITY, "test transactions for position.csv")
        ClosedPosition.load_closed_positions_from_file(Broker.FIDELITY, "test closed positions for position.csv")
        pos_list = Position.generate_position_history(Broker.FIDELITY,
                                                      transfer_security_file="test transfer data for position.csv")
        self.assertEqual(len(pos_list), 38)

        # test account opening day 2022-09-06. spaxx position of 0 and no other securities
        with self.subTest():
            self.equal(PositionTests.position_fidelity_roth_spaxx(datetime.date(2022, 9, 6), Decimal(0)), pos_list[0])

        # test second day 2022-09-07. aapl and spaxx positions
        with self.subTest():
            self.equal(PositionTests.position_fidelity_roth_aapl_20220907_680(), pos_list[1])
            self.equal(PositionTests.position_fidelity_roth_spaxx(datetime.date(2022, 9, 7), Decimal("6648.02")),
                       pos_list[2])

        # test 2022-09-08. aapl, aapl put and spaxx positions
        with self.subTest():
            self.equal(PositionTests.position_fidelity_roth_aapl_20220908_380(), pos_list[3])
            self.equal(PositionTests.position_fidelity_roth_aaplput_20220908_neg14(), pos_list[4])
            self.equal(PositionTests.position_fidelity_roth_spaxx(datetime.date(2022, 9, 8), Decimal("32718.87")),
                       pos_list[5])

        # test 2022-09-09. 6, 7. aapl put and spaxx positions
        with self.subTest():
            self.equal(PositionTests.position_fidelity_roth_aaplput_20220909_neg14(), pos_list[6])
            self.equal(PositionTests.position_fidelity_roth_spaxx(datetime.date(2022, 9, 9), Decimal("55202.16")),
                       pos_list[7])

        # test 2022-09-12. 8, 9, 10, 11. aapl, aapl put and spaxx positions
        with self.subTest():
            self.equal(PositionTests.position_fidelity_roth_aapl_20220912_529(), pos_list[8])
            self.equal(PositionTests.position_fidelity_roth_aapl_20220912_7(), pos_list[9])
            self.equal(PositionTests.position_fidelity_roth_aaplput_20220912_neg14(), pos_list[10])
            self.equal(PositionTests.position_fidelity_roth_spaxx(datetime.date(2022, 9, 12), Decimal("28662.6300")),
                       pos_list[11])

        # test 2022-09-13. 12, 13, 14, 15, 16
        with self.subTest():
            self.equal(PositionTests.position_fidelity_roth_aapl_20220913_1058(), pos_list[12])
            self.equal(PositionTests.position_fidelity_roth_aapl_20220913_14(), pos_list[13])
            self.equal(PositionTests.position_fidelity_roth_aaplcall_20220913_neg12(), pos_list[14])
            self.equal(PositionTests.position_fidelity_roth_aaplput_20220913_neg14(), pos_list[15])
            self.equal(PositionTests.position_fidelity_roth_spaxx(datetime.date(2022, 9, 13), Decimal("29254.4600")),
                       pos_list[16])

        # test 2022-09-14. 17, 18, 19, 20, 21
        with self.subTest():
            self.equal(PositionTests.position_fidelity_roth_aapl_20220914_1058(), pos_list[17])
            self.equal(PositionTests.position_fidelity_roth_aapl_20220914_14(), pos_list[18])
            self.equal(PositionTests.position_fidelity_roth_aaplcall_20220914_neg12(), pos_list[19])
            self.equal(PositionTests.position_fidelity_roth_aaplcall_20220914_5(), pos_list[20])
            self.equal(PositionTests.position_fidelity_roth_spaxx(datetime.date(2022, 9, 14), Decimal("28735.4100")),
                       pos_list[21])

        # no test needed for 2022-09-15. no transactions on that day 22, 23, 24, 25, 26

        # test 2022-09-16. 27, 28, 29
        with self.subTest():
            self.equal(PositionTests.position_fidelity_roth_aapl_20220916_1058(), pos_list[27])
            self.equal(PositionTests.position_fidelity_roth_aapl_20220916_14(), pos_list[28])
            self.equal(PositionTests.position_fidelity_roth_spaxx(datetime.date(2022, 9, 16), Decimal("28735.4100")),
                       pos_list[29])

        # test 2022-09-19. 30, 31, 32, 33
        with self.subTest():
            self.equal(PositionTests.position_fidelity_roth_aapl_20220919_1058(), pos_list[30])
            self.equal(PositionTests.position_fidelity_roth_aapl_20220919_14(), pos_list[31])
            self.equal(PositionTests.position_fidelity_roth_msft_20220919_100(), pos_list[32])
            self.equal(PositionTests.position_fidelity_roth_spaxx(datetime.date(2022, 9, 19), Decimal("28735.3100")),
                       pos_list[33])

        # test 2022-09-20. 34, 35, 36, 37
        with self.subTest():
            self.equal(PositionTests.position_fidelity_roth_aapl_20220920_1058(), pos_list[34])
            self.equal(PositionTests.position_fidelity_roth_aapl_20220920_14(), pos_list[35])
            self.equal(PositionTests.position_fidelity_roth_nvda_20220920_100(), pos_list[36])
            self.equal(PositionTests.position_fidelity_roth_spaxx(datetime.date(2022, 9, 20), Decimal("28735.3100")),
                       pos_list[37])

    def test_load_positions_from_fidelity_file(self):
        with self.assertRaises(NotImplementedError):
            Position.load_positions_from_file(Broker.FIDELITY, "test positions.csv")
        """
        with self.subTest():
            # accounts not created
            with self.assertRaises(ObjectDoesNotExist):
                Position.load_positions_from_file(Broker.FIDELITY, "test positions.csv")

        with self.subTest():
            # close date not in "Close Date" column
            with self.assertRaises(ValueError):
                Position.load_positions_from_file(Broker.FIDELITY, "test positions no close date.csv")

        InvestmentAccountTests.inv_acc_fidelity_individual()
        InvestmentAccountTests.inv_acc_fidelity_roth()
        aapl921_pos = PositionTests.position_fidelity_roth_aapl_lot921()
        aapl13_pos = PositionTests.position_fidelity_roth_aapl_lot13()
        msft21_pos = PositionTests.position_fidelity_roth_msft_lot21()
        msft1225_pos = PositionTests.position_fidelity_roth_msft_lot1225()
        msft19_pos = PositionTests.position_fidelity_roth_msft_lot19()

        with self.subTest():
            # a position that should be broken down by lots is not broken down by lots
            with self.assertRaises(ValidationError):
                Position.load_positions_from_file(Broker.FIDELITY, "test positions missing lots.csv")

        pos_list, sec_ns_list = Position.load_positions_from_file(Broker.FIDELITY, "test positions.csv")
        # put this line after load_positions_from_file() so the create default security function is used for SPAXX
        spaxx_pos = PositionTests.position_fidelity_individual_spaxx()

        with self.subTest():
            self.equal(pos_list[0], aapl921_pos)
        with self.subTest():
            self.equal(pos_list[1], aapl13_pos)
        with self.subTest():
            self.equal(pos_list[2], msft21_pos)
        with self.subTest():
            self.equal(pos_list[3], msft1225_pos)
        with self.subTest():
            self.equal(pos_list[4], msft19_pos)
        with self.subTest():
            self.equal(pos_list[5], spaxx_pos)

        with self.subTest():
            self.assertEqual(len(sec_ns_list), 1)
            SecurityMasterTests().equal(sec_ns_list[0], SecurityMasterTests.sm_spaxx())
        """

    @staticmethod
    def position_fidelity_roth_spaxx(eod_date, quantity):
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=eod_date,
            security=SecurityMasterTests.sm_spaxx_set(), quantity=quantity, eod_price=Decimal("1.00"),
            market_value=quantity, enter_date=None, enter_price=Decimal(1), enter_total=quantity,
            enter_price_net=Decimal(1), enter_total_net=quantity, cost_basis_price=Decimal("1.00"),
            cost_basis_total=quantity)

    @staticmethod
    def position_fidelity_roth_msft_lot19():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2023, 10, 27),
            security=SecurityMasterTests.sm_msft(), quantity=Decimal("19.0000"), eod_price=Decimal("35.97"),
            market_value=Decimal("683.43"), enter_date=datetime.date(2022, 9, 20), enter_price=Decimal("35.82"),
            enter_total=Decimal("680.58"), enter_price_net=Decimal("81.93"), enter_total_net=Decimal("55712.40"),
            cost_basis_price=Decimal("35.82"), cost_basis_total=Decimal("680.58"))

    @staticmethod
    def position_fidelity_roth_aapl_20220907_680():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 7),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("680"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-8395061.65"), enter_date=datetime.date(2022, 9, 7), enter_price=Decimal("81.93"),
            enter_total=Decimal("55712.40"), enter_price_net=Decimal("81.93"), enter_total_net=Decimal("55712.40"),
            cost_basis_price=Decimal("81.93"), cost_basis_total=Decimal("55712.40"))

    @staticmethod
    def position_fidelity_roth_aapl_20220908_380():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 8),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("380"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-4691357.98"), enter_date=datetime.date(2022, 9, 7), enter_price=Decimal("81.93"),
            enter_total=Decimal("31133.40"), enter_price_net=Decimal("81.93"), enter_total_net=Decimal("31133.40"),
            cost_basis_price=Decimal("81.93"), cost_basis_total=Decimal("31133.40"))

    @staticmethod
    def position_fidelity_roth_aapl_20220912_529():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 12),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("529"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-6530864.14"), enter_date=datetime.date(2022, 9, 12), enter_price=Decimal("60.7081"),
            enter_total=Decimal("32114.58"), enter_price_net=Decimal("60.7081"), enter_total_net=Decimal("32114.58"),
            cost_basis_price=Decimal("60.7081"), cost_basis_total=Decimal("32114.58"))

    @staticmethod
    def position_fidelity_roth_aapl_20220912_7():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 12),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("7"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-86419.75"), enter_date=datetime.date(2022, 9, 12), enter_price=Decimal("60.7070"),
            enter_total=Decimal("424.95"), enter_price_net=Decimal("60.7071"), enter_total_net=Decimal("424.95"),
            cost_basis_price=Decimal("60.7071"), cost_basis_total=Decimal("424.95"))

    @staticmethod
    def position_fidelity_roth_aapl_20220913_1058():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 13),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("1058"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-13061728.28"), enter_date=datetime.date(2022, 9, 12), enter_price=Decimal("30.3540"),
            enter_total=Decimal("32114.58"), enter_price_net=Decimal("30.3540"), enter_total_net=Decimal("32114.58"),
            cost_basis_price=Decimal("30.3540"), cost_basis_total=Decimal("32114.58"))

    @staticmethod
    def position_fidelity_roth_aapl_20220913_14():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 13),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("14"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-172839.50"), enter_date=datetime.date(2022, 9, 12), enter_price=Decimal("30.3535"),
            enter_total=Decimal("424.95"), enter_price_net=Decimal("30.3536"), enter_total_net=Decimal("424.95"),
            cost_basis_price=Decimal("30.3536"), cost_basis_total=Decimal("424.95"))

    @staticmethod
    def position_fidelity_roth_aapl_20220914_1058():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 14),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("1058"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-13061728.28"), enter_date=datetime.date(2022, 9, 12), enter_price=Decimal("30.3540"),
            enter_total=Decimal("32114.58"), enter_price_net=Decimal("30.3540"), enter_total_net=Decimal("32114.58"),
            cost_basis_price=Decimal("30.3540"), cost_basis_total=Decimal("32114.58"))

    @staticmethod
    def position_fidelity_roth_aapl_20220914_14():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 14),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("14"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-172839.50"), enter_date=datetime.date(2022, 9, 12), enter_price=Decimal("30.3535"),
            enter_total=Decimal("424.95"), enter_price_net=Decimal("30.3536"), enter_total_net=Decimal("424.95"),
            cost_basis_price=Decimal("30.3536"), cost_basis_total=Decimal("424.95"))

    @staticmethod
    def position_fidelity_roth_aapl_20220916_1058():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 16),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("1058"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-13061728.28"), enter_date=datetime.date(2022, 9, 12), enter_price=Decimal("30.3540"),
            enter_total=Decimal("32114.58"), enter_price_net=Decimal("30.3540"), enter_total_net=Decimal("32114.58"),
            cost_basis_price=Decimal("30.3540"), cost_basis_total=Decimal("32114.58"))

    @staticmethod
    def position_fidelity_roth_aapl_20220916_14():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 16),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("14"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-172839.50"), enter_date=datetime.date(2022, 9, 12), enter_price=Decimal("30.3535"),
            enter_total=Decimal("424.95"), enter_price_net=Decimal("30.3536"), enter_total_net=Decimal("424.95"),
            cost_basis_price=Decimal("30.3536"), cost_basis_total=Decimal("424.95"))

    @staticmethod
    def position_fidelity_roth_aapl_20220919_1058():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 19),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("1058"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-13061728.28"), enter_date=datetime.date(2022, 9, 12), enter_price=Decimal("30.3540"),
            enter_total=Decimal("32114.58"), enter_price_net=Decimal("30.3540"), enter_total_net=Decimal("32114.58"),
            cost_basis_price=Decimal("30.3540"), cost_basis_total=Decimal("32114.58"))

    @staticmethod
    def position_fidelity_roth_aapl_20220919_14():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 19),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("14"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-172839.50"), enter_date=datetime.date(2022, 9, 12), enter_price=Decimal("30.3535"),
            enter_total=Decimal("424.95"), enter_price_net=Decimal("30.3536"), enter_total_net=Decimal("424.95"),
            cost_basis_price=Decimal("30.3536"), cost_basis_total=Decimal("424.95"))

    @staticmethod
    def position_fidelity_roth_aapl_20220920_1058():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 20),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("1058"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-13061728.28"), enter_date=datetime.date(2022, 9, 12), enter_price=Decimal("30.3540"),
            enter_total=Decimal("32114.58"), enter_price_net=Decimal("30.3540"), enter_total_net=Decimal("32114.58"),
            cost_basis_price=Decimal("30.3540"), cost_basis_total=Decimal("32114.58"))

    @staticmethod
    def position_fidelity_roth_aapl_20220920_14():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 20),
            security=SecurityMasterTests.sm_aapl(), quantity=Decimal("14"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-172839.50"), enter_date=datetime.date(2022, 9, 12), enter_price=Decimal("30.3535"),
            enter_total=Decimal("424.95"), enter_price_net=Decimal("30.3536"), enter_total_net=Decimal("424.95"),
            cost_basis_price=Decimal("30.3536"), cost_basis_total=Decimal("424.95"))

    @staticmethod
    def position_fidelity_roth_aaplcall_20220913_neg12():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 13),
            security=SecurityMasterTests.sm_aapl_call(), quantity=Decimal("-12"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("14814814.68"), enter_date=datetime.date(2022, 9, 13), enter_price=Decimal("0.50"),
            enter_total=Decimal("600.00"), enter_price_net=Decimal("0.4932"), enter_total_net=Decimal("591.83"),
            cost_basis_price=None, cost_basis_total=None)

    @staticmethod
    def position_fidelity_roth_aaplcall_20220914_neg12():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 14),
            security=SecurityMasterTests.sm_aapl_call(), quantity=Decimal("-12"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("14814814.68"), enter_date=datetime.date(2022, 9, 13), enter_price=Decimal("0.50"),
            enter_total=Decimal("600.00"), enter_price_net=Decimal("0.4932"), enter_total_net=Decimal("591.83"),
            cost_basis_price=None, cost_basis_total=None)

    @staticmethod
    def position_fidelity_roth_aaplcall_20220914_5():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 14),
            security=SecurityMasterTests.sm_aapl_call(), quantity=Decimal("5"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-6172839.45"), enter_date=datetime.date(2022, 9, 14), enter_price=Decimal("0.7100"),
            enter_total=Decimal("355.00"), enter_price_net=Decimal("0.7149"), enter_total_net=Decimal("357.46"),
            cost_basis_price=Decimal("0.7149"), cost_basis_total=Decimal("357.46"))

    @staticmethod
    def position_fidelity_roth_aaplput_20220908_neg14():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 8),
            security=SecurityMasterTests.sm_aapl_put(), quantity=Decimal("-14"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("17283950.46"), enter_date=datetime.date(2022, 9, 8), enter_price=Decimal("0.70"),
            enter_total=Decimal("980.00"), enter_price_net=Decimal("0.6932"), enter_total_net=Decimal("970.46"),
            cost_basis_price=None, cost_basis_total=None)

    @staticmethod
    def position_fidelity_roth_aaplput_20220909_neg14():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 9),
            security=SecurityMasterTests.sm_aapl_put(), quantity=Decimal("-14"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("17283950.46"), enter_date=datetime.date(2022, 9, 8), enter_price=Decimal("0.70"),
            enter_total=Decimal("980.00"), enter_price_net=Decimal("0.6932"), enter_total_net=Decimal("970.46"),
            cost_basis_price=None, cost_basis_total=None)

    @staticmethod
    def position_fidelity_roth_aaplput_20220912_neg14():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 12),
            security=SecurityMasterTests.sm_aapl_put(), quantity=Decimal("-14"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("17283950.46"), enter_date=datetime.date(2022, 9, 8), enter_price=Decimal("0.70"),
            enter_total=Decimal("980.00"), enter_price_net=Decimal("0.6932"), enter_total_net=Decimal("970.46"),
            cost_basis_price=None, cost_basis_total=None)

    @staticmethod
    def position_fidelity_roth_aaplput_20220913_neg14():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 13),
            security=SecurityMasterTests.sm_aapl_put(), quantity=Decimal("-14"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("17283950.46"), enter_date=datetime.date(2022, 9, 8), enter_price=Decimal("0.70"),
            enter_total=Decimal("980.00"), enter_price_net=Decimal("0.6932"), enter_total_net=Decimal("970.46"),
            cost_basis_price=None, cost_basis_total=None)

    @staticmethod
    def position_fidelity_roth_msft_20220919_100():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 19),
            security=SecurityMasterTests.sm_msft(), quantity=Decimal("100"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-1234567.89"), enter_date=datetime.date(2016, 1, 28), enter_price=Decimal("23.4240"),
            enter_total=Decimal("2342.40"), enter_price_net=Decimal("23.4240"), enter_total_net=Decimal("2342.40"),
            cost_basis_price=Decimal("23.4240"), cost_basis_total=Decimal("2342.40"))

    @staticmethod
    def position_fidelity_roth_nvda_20220920_100():
        return Position(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(), eod_date=datetime.date(2022, 9, 20),
            security=SecurityMasterTests.sm_nvda_set(), quantity=Decimal("100"), eod_price=Decimal("-12345.6789"),
            market_value=Decimal("-1234567.89"), enter_date=datetime.date(2016, 1, 28), enter_price=Decimal("23.4240"),
            enter_total=Decimal("2342.40"), enter_price_net=Decimal("23.4240"), enter_total_net=Decimal("2342.40"),
            cost_basis_price=Decimal("23.4240"), cost_basis_total=Decimal("2342.40"))