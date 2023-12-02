from decimal import Decimal, InvalidOperation
import datetime

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, transaction

from ...models.securitymaster import AssetClass, AssetSubClass, OptionType, SecurityMaster
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class SecurityMasterTests(DjangoModelTestCaseBase):

    def equal(self, model1: SecurityMaster, model2: SecurityMaster):
        if model1.underlying_security is not None or model2.underlying_security is not None:
            SecurityMasterTests().equal(model1.underlying_security, model2.underlying_security)
        self.simple_equal(model1, model2, SecurityMaster, rem_attr_list=["underlying_security"])

    def test_asset_class_get_my_id_prefix(self):
        # all AssetClass enums are set in get_my_id_prefix()
        for asset_class in AssetClass:
            AssetClass.get_my_id_prefix(asset_class)

        # check get_my_id_prefix() return format
        self.assertEqual(AssetClass.get_my_id_prefix(AssetClass.BOND), "BO_")

    def test_asset_class_get_subclasses(self):
        # all AssetClass enums are set in get_subclasses()
        for asset_class in AssetClass:
            AssetClass.get_subclasses(asset_class)

        # check get_subclasses() return format
        bond_subclasses = AssetClass.get_subclasses(AssetClass.BOND)
        self.assertEqual(bond_subclasses, (AssetSubClass.CORP_BOND, AssetSubClass.GOV_BOND, AssetSubClass.MUNI_BOND))

    def test_asset_subclass_get_class(self):
        # check all AssetSubClass enums are set in get_class()
        for asset_subclass in AssetSubClass:
            AssetSubClass.get_class(asset_subclass)

        # check get_class() return format
        equity = AssetSubClass.get_class(AssetSubClass.COMMON_STOCK)
        self.assertEqual(equity, AssetClass.EQUITY)

    def test_change_ticker(self):
        # old ticker does not exist
        with transaction.atomic():
            with self.assertRaises(ObjectDoesNotExist):
                SecurityMaster.objects.change_ticker("AAPL", "MSFT")

        # new ticker already exists
        aapl = SecurityMasterTests.sm_aapl()
        SecurityMasterTests.sm_msft()
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                SecurityMaster.objects.change_ticker("AAPL", "MSFT")

        # no issues. my_id does not change but ticker changes
        aapl_id = aapl.my_id
        SecurityMaster.objects.change_ticker("AAPL", "NVDA")
        sm = SecurityMaster.objects.get(ticker="NVDA")
        self.assertEqual(sm.my_id, aapl_id)
        self.assertEqual(sm.ticker, "NVDA")

    def test_convert_asset_class(self):
        sm_new = SecurityMaster.objects.convert_asset_class(
            SecurityMasterTests.sm_nvda(), AssetClass.EQUITY, AssetSubClass.COMMON_STOCK)
        sm_test = SecurityMasterTests.sm_nvda()
        sm_test.my_id = "EQ_0000001"
        sm_test.asset_class = AssetClass.EQUITY
        sm_test.asset_subclass = AssetSubClass.COMMON_STOCK
        self.simple_equal(sm_new, sm_test, SecurityMaster)

    def test_create_default(self):
        sm = SecurityMaster.objects.create_default("NVDA")
        self.equal(sm, SecurityMasterTests.sm_nvda())

    def test_get_or_create_default(self):
        # test get existing object. create object first then call get_or_create_default
        self.equal(SecurityMasterTests.sm_aapl(), SecurityMaster.objects.get_or_create_default("AAPL"))

        # test create default object. create default object then test equality to ensure it is a default object
        self.equal(SecurityMaster.objects.get_or_create_default("NVDA"), SecurityMasterTests.sm_nvda())

    def test_field_to_security_dict(self):
        with self.assertRaises(ValueError):
            SecurityMaster.objects.field_to_security_dict("fail", [])

        sm1 = SecurityMasterTests.sm_aapl()
        sm2 = SecurityMasterTests.sm_msft()

        d = SecurityMaster.objects.field_to_security_dict("pk", [sm1.pk, sm2.pk])
        with self.subTest():
            self.assertEqual(list(d), [sm1.pk, sm2.pk])
            self.equal(d[sm1.pk], sm1)
            self.equal(d[sm2.pk], sm2)

        d = SecurityMaster.objects.field_to_security_dict("my_id", [sm1.my_id, sm2.my_id])
        with self.subTest():
            self.assertEqual(list(d), [sm1.my_id, sm2.my_id])
            self.equal(d[sm1.my_id], sm1)
            self.equal(d[sm2.my_id], sm2)

        d = SecurityMaster.objects.field_to_security_dict("ticker", [sm1.ticker, sm2.ticker])
        with self.subTest():
            self.assertEqual(list(d), [sm1.ticker, sm2.ticker])
            self.equal(d[sm1.ticker], sm1)
            self.equal(d[sm2.ticker], sm2)

    def test_my_id(self):
        # no validation error
        sm_create = SecurityMasterTests.sm_aapl()

        # validation error - length of my_id not equal 10
        sm_create.my_id = "EQ_000001"
        with self.subTest():
            with self.assertRaises(ValidationError):
                sm_create.save()
        with self.subTest():
            with self.assertRaises(ValidationError):
                sm_create.clean_fields()

        # validation error - _ not at third characters
        sm_create.my_id = "EQ#0000001"
        with self.subTest():
            with self.assertRaises(ValidationError):
                sm_create.save()
        with self.subTest():
            with self.assertRaises(ValidationError):
                sm_create.clean_fields()

        # validation error - characters after _ are not all digits
        sm_create.my_id = "EQ_00000a1"
        with self.subTest():
            with self.assertRaises(ValidationError):
                sm_create.save()
        with self.subTest():
            with self.assertRaises(ValidationError):
                sm_create.clean_fields()

        # wrong prefix for EQUITY asset class
        sm_create.my_id = "AA_0000001"
        with self.subTest():
            with self.assertRaises(ValidationError):
                sm_create.save()
        with self.subTest():
            with self.assertRaises(ValidationError):
                sm_create.clean_fields()

    def test_generate_my_id(self):
        # no equities in security master
        self.assertEqual(SecurityMaster.generate_my_id(AssetClass.EQUITY), "EQ_0000001")

        # one equity in security master
        SecurityMasterTests.sm_aapl()
        self.assertEqual(SecurityMaster.generate_my_id(AssetClass.EQUITY), "EQ_0000002")

        # two equities in security master
        SecurityMasterTests.sm_msft()
        self.assertEqual(SecurityMaster.generate_my_id(AssetClass.EQUITY), "EQ_1000002")

    def test_get_option_data_from_ticker(self):
        # underlying security does not exist
        with self.subTest():
            with self.assertRaises(ObjectDoesNotExist):
                SecurityMaster.get_option_data_from_ticker("AAPL220916C41.5")

        aapl = SecurityMasterTests.sm_aapl()
        SecurityMasterTests.sm_msft()

        # expiration date invalid
        with self.subTest():
            with self.assertRaises(ValueError):
                SecurityMaster.get_option_data_from_ticker("AAPL22a916C41.5")

        # option type not found
        with self.subTest():
            with self.assertRaises(ValueError):
                SecurityMaster.get_option_data_from_ticker("MSFT220916D41.5")

        # cant parse strike price
        with self.subTest():
            with self.assertRaises(InvalidOperation):
                SecurityMaster.get_option_data_from_ticker("MSFT220916C41.5a")

        underlying_security, exp_date, opt_type, strike_price, contract_size = \
            SecurityMaster.get_option_data_from_ticker("AAPL220916C41.5")
        self.equal(underlying_security, aapl)
        self.assertEqual(exp_date, datetime.date(2022, 9, 16))
        self.assertEqual(opt_type, OptionType.AMERICAN_CALL)
        self.assertEqual(strike_price, Decimal("41.5"))
        self.assertEqual(contract_size, 100)

    def test_save_clean(self):
        # no validation error
        sm = SecurityMasterTests.sm_aapl()

        # should raise ValidationError
        with self.subTest():
            sm.asset_subclass = AssetSubClass.INDEX_OPTION
            with self.assertRaises(ValidationError):
                sm.save()

        # no validation error
        sm = SecurityMasterTests.sm_aapl(create=False)

        # should raise ValidationError
        with self.subTest():
            sm.asset_subclass = AssetSubClass.INDEX_OPTION
            with self.assertRaises(ValidationError):
                sm.clean_fields()

        with self.subTest():
            sm = SecurityMasterTests.sm_aapl_call()
            sm.underlying_security = None
            with self.assertRaises(ValidationError):
                sm.save()
            with self.assertRaises(ValidationError):
                sm.clean_fields()

        with self.subTest():
            sm = SecurityMasterTests.sm_aapl_call()
            sm.expiration_date = None
            with self.assertRaises(ValidationError):
                sm.save()
            with self.assertRaises(ValidationError):
                sm.clean_fields()

        with self.subTest():
            sm = SecurityMasterTests.sm_aapl_call()
            sm.option_type = None
            with self.assertRaises(ValidationError):
                sm.save()
            with self.assertRaises(ValidationError):
                sm.clean_fields()

        with self.subTest():
            sm = SecurityMasterTests.sm_aapl_call()
            sm.strike_price = None
            with self.assertRaises(ValidationError):
                sm.save()
            with self.assertRaises(ValidationError):
                sm.clean_fields()

    @staticmethod
    def sm_aapl(create=True):
        sm = (SecurityMaster.objects.get_or_create if create else SecurityMaster)(
            my_id="EQ_0000001", ticker="AAPL", asset_class=AssetClass.EQUITY,
            asset_subclass=AssetSubClass.COMMON_STOCK, has_fidelity_lots=True)
        return sm[0] if create else sm

    @staticmethod
    def sm_aapl_call(create=True):
        sm = (SecurityMaster.objects.get_or_create if create else SecurityMaster)(
            my_id="OP_0000001", ticker="AAPL220916C41.5", asset_class=AssetClass.OPTION,
            asset_subclass=AssetSubClass.EQUITY_OPTION, underlying_security=SecurityMasterTests.sm_aapl(),
            expiration_date=datetime.date(2022, 9, 16), option_type=OptionType.AMERICAN_CALL,
            strike_price=Decimal("41.5"), contract_size=100, has_fidelity_lots=True)
        return sm[0] if create else sm

    @staticmethod
    def sm_aapl_put(create=True):
        sm = (SecurityMaster.objects.get_or_create if create else SecurityMaster)(
            my_id="OP_0000002", ticker="AAPL220916P37.5", asset_class=AssetClass.OPTION,
            asset_subclass=AssetSubClass.EQUITY_OPTION, underlying_security=SecurityMasterTests.sm_aapl(),
            expiration_date=datetime.date(2022, 9, 16), option_type=OptionType.AMERICAN_PUT,
            strike_price=Decimal("37.5"), contract_size=100, has_fidelity_lots=True)
        return sm[0] if create else sm

    @staticmethod
    def sm_btc():
        return SecurityMaster.objects.get_or_create(
            my_id="CR_0000001", ticker="BTC", asset_class=AssetClass.CRYPTO, asset_subclass=AssetSubClass.CRYPTO,
            has_fidelity_lots=True)[0]

    @staticmethod
    def sm_cad():
        return SecurityMaster.objects.get_or_create(
            my_id="FX_0000001", ticker="CAD", asset_class=AssetClass.FX, asset_subclass=AssetSubClass.FX,
            has_fidelity_lots=False)[0]

    @staticmethod
    def sm_msft(create=True):
        sm = (SecurityMaster.objects.get_or_create if create else SecurityMaster)(
            my_id="EQ_1000001", ticker="MSFT", asset_class=AssetClass.EQUITY,
            asset_subclass=AssetSubClass.COMMON_STOCK, has_fidelity_lots=True)
        return sm[0] if create else sm

    @staticmethod
    def sm_nvda():
        return SecurityMaster(my_id="NS_0000001", ticker="NVDA", asset_class=AssetClass.NOT_SET,
                              asset_subclass=AssetSubClass.NOT_SET, has_fidelity_lots=True)

    @staticmethod
    def sm_nvda_set(create=True):
        sm = (SecurityMaster.objects.get_or_create if create else SecurityMaster)(
            my_id="EQ_2000001", ticker="NVDA", asset_class=AssetClass.EQUITY,
            asset_subclass=AssetSubClass.COMMON_STOCK, has_fidelity_lots=True)
        return sm[0] if create else sm

    @staticmethod
    def sm_spaxx(has_fidelity_lots=False):
        return SecurityMaster.objects.get_or_create(
            my_id="NS_0000001", ticker="SPAXX", asset_class=AssetClass.NOT_SET,
            asset_subclass=AssetSubClass.NOT_SET, has_fidelity_lots=has_fidelity_lots)[0]

    @staticmethod
    def sm_spaxx_set():
        return SecurityMaster.objects.get_or_create(
            my_id="MF_0000001", ticker="SPAXX", asset_class=AssetClass.MUTUAL_FUND,
            asset_subclass=AssetSubClass.MONEY_MARKET, has_fidelity_lots=False)[0]
