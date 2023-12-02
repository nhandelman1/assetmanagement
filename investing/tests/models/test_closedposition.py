from decimal import Decimal
import datetime

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ...models.investmentaccount import Broker
from ...models.closedposition import ClosedPosition
from .test_investmentaccount import InvestmentAccountTests
from .test_securitymaster import SecurityMasterTests
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class ClosedPositionTests(DjangoModelTestCaseBase):

    def equal(self, model1: ClosedPosition, model2: ClosedPosition):
        InvestmentAccountTests().equal(model1.investment_account, model2.investment_account)
        SecurityMasterTests().equal(model1.security, model2.security)
        self.simple_equal(model1, model2, ClosedPosition, rem_attr_list=["investment_account", "security"])

    def test_save_clean(self):
        pos = ClosedPositionTests.closedposition_fidelity_individual_aaplput_long()
        pos.short_term_pnl = Decimal(1)
        with self.assertRaises(ValidationError):
            pos.save()
        with self.assertRaises(ValidationError):
            pos.clean_fields()

        pos = ClosedPositionTests.closedposition_fidelity_individual_aaplput_long()
        pos.short_term_pnl_unadj = Decimal(1)
        with self.assertRaises(ValidationError):
            pos.save()
        with self.assertRaises(ValidationError):
            pos.clean_fields()

    def test_load_closed_positions_from_fidelity_file(self):
        self.maxDiff = None

        with self.subTest():
            # accounts not created
            with self.assertRaises(ObjectDoesNotExist):
                ClosedPosition.load_closed_positions_from_file(Broker.FIDELITY, "test closedpositions.csv")

        inv_acc_fid_ind = InvestmentAccountTests.inv_acc_fidelity_individual()
        InvestmentAccountTests.inv_acc_fidelity_roth()
        SecurityMasterTests.sm_aapl_put()

        with self.subTest():
            # at least one position that should be broken down by lots is not broken down by lots
            with self.assertRaises(ValueError):
                ClosedPosition.load_closed_positions_from_file(Broker.FIDELITY, "test closedpositions missing lots.csv")

        pos_list, sec_ns_list, exist_inv_acc_dates_set = ClosedPosition.load_closed_positions_from_file(
            Broker.FIDELITY, "test closedpositions.csv")

        with self.subTest():
            self.equal(pos_list[0], ClosedPositionTests.closedposition_fidelity_individual_spaxx_lot23())
        with self.subTest():
            self.equal(pos_list[1], ClosedPositionTests.closedposition_fidelity_individual_spaxx_lot11177())
        with self.subTest():
            self.equal(pos_list[2], ClosedPositionTests.closedposition_fidelity_individual_aaplput_short())
        with self.subTest():
            self.equal(pos_list[3], ClosedPositionTests.closedposition_fidelity_individual_aaplput_long())
        with self.subTest():
            self.assertEqual(len(sec_ns_list), 1)
            SecurityMasterTests().equal(sec_ns_list[0], SecurityMasterTests.sm_spaxx(has_fidelity_lots=True))
        with self.subTest():
            self.assertEqual(len(exist_inv_acc_dates_set), 0)

        pos_list, sec_ns_list, exist_inv_acc_dates_set = ClosedPosition.load_closed_positions_from_file(
            Broker.FIDELITY, "test closedpositions duplicate.csv")

        with self.subTest():
            self.assertEqual(len(pos_list), 1)
        with self.subTest():
            self.assertEqual(len(sec_ns_list), 0)
        with self.subTest():
            # update when "test closedpositions.csv" changes
            self.assertEqual(len(exist_inv_acc_dates_set), 1)
            self.assertEqual(list(exist_inv_acc_dates_set)[0], (inv_acc_fid_ind, datetime.date(2022, 9, 29)))

    @staticmethod
    def closedposition_fidelity_individual_spaxx_lot23():
        return ClosedPosition(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_individual(),
            enter_date=datetime.date(2022, 9, 12), close_date=datetime.date(2022, 9, 29),
            security=SecurityMasterTests.sm_spaxx(has_fidelity_lots=True), quantity=Decimal("0.23"),
            enter_price_net=Decimal("81.913"), close_price_net=Decimal("57.347"), cost_basis_price=Decimal("57.347"),
            cost_basis_total=Decimal("13.190"), proceeds_price=Decimal("57.347"), proceeds_total=Decimal("13.190"),
            short_term_pnl=Decimal("0"), long_term_pnl=Decimal("0"), cost_basis_price_unadj=Decimal("81.913"),
            cost_basis_total_unadj=Decimal("18.84"), short_term_pnl_unadj=Decimal("-5.65"),
            long_term_pnl_unadj=Decimal("0"))

    @staticmethod
    def closedposition_fidelity_individual_spaxx_lot11177():
        return ClosedPosition(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_individual(),
            enter_date=datetime.date(2022, 9, 1), close_date=datetime.date(2022, 9, 20),
            security=SecurityMasterTests.sm_spaxx(has_fidelity_lots=True), quantity=Decimal("111.77"),
            enter_price_net=Decimal("81.93"), close_price_net=Decimal("57.336"), cost_basis_price=Decimal("74.872"),
            cost_basis_total=Decimal("8368.55"), proceeds_price=Decimal("57.336"), proceeds_total=Decimal("6408.47"),
            short_term_pnl=Decimal("-1960.08"), long_term_pnl=Decimal("0"), cost_basis_price_unadj=Decimal("81.93"),
            cost_basis_total_unadj=Decimal("9157.32"), short_term_pnl_unadj=Decimal("-2748.85"),
            long_term_pnl_unadj=Decimal("0"))

    @staticmethod
    def closedposition_fidelity_individual_aaplput_short():
        return ClosedPosition(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(),
            enter_date=datetime.date(2022, 9, 8), close_date=datetime.date(2022, 9, 12),
            security=SecurityMasterTests.sm_aapl_put(), quantity=Decimal("8.0"),
            enter_price_net=Decimal("0.693"), close_price_net=Decimal("0.14"), cost_basis_price=Decimal("0.14"),
            cost_basis_total=Decimal("112.23"), proceeds_price=Decimal("0.693"), proceeds_total=Decimal("554.55"),
            short_term_pnl=Decimal("0"), long_term_pnl=Decimal("442.32"), cost_basis_price_unadj=Decimal("0.14"),
            cost_basis_total_unadj=Decimal("112.23"), short_term_pnl_unadj=Decimal("0"),
            long_term_pnl_unadj=Decimal("442.32"))

    @staticmethod
    def closedposition_fidelity_individual_aaplput_long():
        return ClosedPosition(
            investment_account=InvestmentAccountTests.inv_acc_fidelity_roth(),
            enter_date=datetime.date(2022, 10, 1), close_date=datetime.date(2022, 10, 15),
            security=SecurityMasterTests.sm_aapl_put(), quantity=Decimal("2.0"),
            enter_price_net=Decimal("0.30"), close_price_net=Decimal("0.496"), cost_basis_price=Decimal("0.30"),
            cost_basis_total=Decimal("60.00"), proceeds_price=Decimal("0.496"), proceeds_total=Decimal("99.20"),
            short_term_pnl=Decimal("0"), long_term_pnl=Decimal("39.20"), cost_basis_price_unadj=Decimal("0.30"),
            cost_basis_total_unadj=Decimal("60.00"), short_term_pnl_unadj=Decimal("0"),
            long_term_pnl_unadj=Decimal("39.20"))
