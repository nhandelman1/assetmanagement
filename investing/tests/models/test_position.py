from decimal import Decimal
import datetime

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ...models.investmentaccount import Broker
from ...models.position import Position
from .test_investmentaccount import InvestmentAccountTests
from .test_securitymaster import SecurityMasterTests
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class PositionTests(DjangoModelTestCaseBase):

    def equal(self, model1: Position, model2: Position):
        InvestmentAccountTests().equal(model1.investment_account, model2.investment_account)
        SecurityMasterTests().equal(model1.security, model2.security)
        self.simple_equal(model1, model2, Position, rem_attr_list=["investment_account", "security"])

    def test_save_clean(self):
        pos = PositionTests.position_fidelity_roth_aapl_lot921()
        pos.purchase_date = None

        with self.assertRaises(ValidationError):
            pos.save()

        with self.assertRaises(ValidationError):
            pos.clean_fields()

    def test_load_positions_from_fidelity_file(self):
        with self.subTest():
            # accounts not created
            with self.assertRaises(ObjectDoesNotExist):
                Position.load_positions_from_file(Broker.FIDELITY, "test positions.csv")

        with self.subTest():
            # close date not in "Close Date" column
            with self.assertRaises(ValueError):
                Position.load_positions_from_file(Broker.FIDELITY, "test positions no close date.csv")

        InvestmentAccountTests.investment_account_fidelity_individual()
        InvestmentAccountTests.investment_account_fidelity_roth()
        aapl921_pos = PositionTests.position_fidelity_roth_aapl_lot921()
        aapl13_pos = PositionTests.position_fidelity_roth_aapl_lot13()
        msft21_pos = PositionTests.position_fidelity_roth_msft_lot21()
        msft1225_pos = PositionTests.position_fidelity_roth_msft_lot1225()
        msft19_pos = PositionTests.position_fidelity_roth_msft_lot19()
        spaxx_pos = PositionTests.position_fidelity_individual_spaxx()
        pos_list = Position.load_positions_from_file(Broker.FIDELITY, "test positions.csv")

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

    @staticmethod
    def position_fidelity_individual_spaxx():
        return Position(
            investment_account=InvestmentAccountTests.investment_account_fidelity_individual(),
            close_date=datetime.date(2023, 10, 27), security=SecurityMasterTests.security_master_spaxx(),
            quantity=Decimal("3423.5300"), close_price=Decimal("1.00"), market_value=Decimal("3423.5300"),
            purchase_date=None, cost_basis_price=Decimal("1.00"), cost_basis_total=Decimal("3423.5300"))

    @staticmethod
    def position_fidelity_roth_msft_lot21():
        return Position(
            investment_account=InvestmentAccountTests.investment_account_fidelity_roth(),
            close_date=datetime.date(2023, 10, 27), security=SecurityMasterTests.security_master_msft(),
            quantity=Decimal("21.0000"), close_price=Decimal("35.97"), market_value=Decimal("755.37"),
            purchase_date=datetime.date(2023, 2, 21), cost_basis_price=Decimal("36.29"),
            cost_basis_total=Decimal("762.09"))

    @staticmethod
    def position_fidelity_roth_msft_lot19():
        return Position(
            investment_account=InvestmentAccountTests.investment_account_fidelity_roth(),
            close_date=datetime.date(2023, 10, 27), security=SecurityMasterTests.security_master_msft(),
            quantity=Decimal("19.0000"), close_price=Decimal("35.97"), market_value=Decimal("683.43"),
            purchase_date=datetime.date(2022, 9, 20), cost_basis_price=Decimal("35.82"),
            cost_basis_total=Decimal("680.58"))

    @staticmethod
    def position_fidelity_roth_msft_lot1225():
        return Position(
            investment_account=InvestmentAccountTests.investment_account_fidelity_roth(),
            close_date=datetime.date(2023, 10, 27), security=SecurityMasterTests.security_master_msft(),
            quantity=Decimal("1225.0000"), close_price=Decimal("35.97"), market_value=Decimal("44063.25"),
            purchase_date=datetime.date(2022, 9, 12), cost_basis_price=Decimal("43.47"),
            cost_basis_total=Decimal("53250.75"))

    @staticmethod
    def position_fidelity_roth_aapl_lot13():
        return Position(
            investment_account=InvestmentAccountTests.investment_account_fidelity_roth(),
            close_date=datetime.date(2023, 10, 27), security=SecurityMasterTests.security_master_aapl(),
            quantity=Decimal("13.0000"), close_price=Decimal("35.97"), market_value=Decimal("467.61"),
            purchase_date=datetime.date(2022, 9, 20), cost_basis_price=Decimal("35.92"),
            cost_basis_total=Decimal("466.96"))

    @staticmethod
    def position_fidelity_roth_aapl_lot921():
        return Position(
            investment_account=InvestmentAccountTests.investment_account_fidelity_roth(),
            close_date=datetime.date(2023, 10, 27), security=SecurityMasterTests.security_master_aapl(),
            quantity=Decimal("921.0000"), close_price=Decimal("35.97"), market_value=Decimal("33128.37"),
            purchase_date=datetime.date(2022, 9, 12), cost_basis_price=Decimal("43.47"),
            cost_basis_total=Decimal("40035.87"))
