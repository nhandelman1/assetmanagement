from django.core.exceptions import ValidationError

from ...models.securitymaster import AssetClass, AssetSubClass, SecurityMaster
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class SecurityMasterTests(DjangoModelTestCaseBase):

    def equal(self, model1: SecurityMaster, model2: SecurityMaster):
        self.simple_equal(model1, model2, SecurityMaster)

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

    def test_create_default(self):
        sm = SecurityMaster.objects.create_default("NVDA")
        self.equal(sm, SecurityMasterTests.security_master_nvda())

    def test_get_or_create_default(self):
        # test get existing object
        self.equal(SecurityMasterTests.security_master_aapl(), SecurityMaster.objects.get_or_create_default("AAPL"))

        # test create default object
        self.equal(SecurityMasterTests.security_master_nvda(), SecurityMaster.objects.get_or_create_default("NVDA"))

    def test_convert_asset_class(self):
        sm_new = SecurityMaster.objects.convert_asset_class(
            SecurityMasterTests.security_master_nvda(), AssetClass.EQUITY, AssetSubClass.COMMON_STOCK)
        sm_test = SecurityMasterTests.security_master_nvda()
        sm_test.my_id = "EQ_0000001"
        sm_test.asset_class = AssetClass.EQUITY
        sm_test.asset_subclass = AssetSubClass.COMMON_STOCK
        self.simple_equal(sm_new, sm_test, SecurityMaster)

    def test_my_id(self):
        # no validation error
        sm_create = SecurityMasterTests.security_master_aapl()

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
        SecurityMasterTests.security_master_aapl()
        self.assertEqual(SecurityMaster.generate_my_id(AssetClass.EQUITY), "EQ_0000002")

        # two equities in security master
        SecurityMasterTests.security_master_msft()
        self.assertEqual(SecurityMaster.generate_my_id(AssetClass.EQUITY), "EQ_1000002")

    def test_save_clean(self):
        # no validation error
        sm = SecurityMasterTests.security_master_aapl()

        # should raise ValidationError
        with self.assertRaises(ValidationError):
            sm.asset_subclass = AssetSubClass.INDEX_OPTION
            sm.save()

        # no validation error
        sm = SecurityMasterTests.security_master_aapl(create=False)

        # should raise ValidationError
        with self.assertRaises(ValidationError):
            sm.asset_subclass = AssetSubClass.INDEX_OPTION
            sm.clean_fields()

    @staticmethod
    def security_master_aapl(create=True):
        sm = (SecurityMaster.objects.get_or_create if create else SecurityMaster)(
            my_id="EQ_0000001", ticker="AAPL", asset_class=AssetClass.EQUITY,
            asset_subclass=AssetSubClass.COMMON_STOCK)
        return sm[0] if create else sm

    @staticmethod
    def security_master_msft(create=True):
        sm = (SecurityMaster.objects.get_or_create if create else SecurityMaster)(
            my_id="EQ_1000001", ticker="MSFT", asset_class=AssetClass.EQUITY,
            asset_subclass=AssetSubClass.COMMON_STOCK)
        return sm[0] if create else sm

    @staticmethod
    def security_master_nvda():
        return SecurityMaster(my_id="NS_0000001", ticker="NVDA", asset_class=AssetClass.NOT_SET,
                              asset_subclass=AssetSubClass.NOT_SET)

    @staticmethod
    def security_master_btc():
        return SecurityMaster.objects.get_or_create(
            my_id="CR_0000001", ticker="BTC", asset_class=AssetClass.CRYPTO, asset_subclass=AssetSubClass.CRYPTO)[0]

    @staticmethod
    def security_master_cad():
        return SecurityMaster.objects.get_or_create(
            my_id="FX_0000001", ticker="CAD", asset_class=AssetClass.FX, asset_subclass=AssetSubClass.FX)[0]
