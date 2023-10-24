from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy


class SecurityMasterDataManager(models.Manager):

    def create_default(self, ticker):
        """ Create default SecurityMaster object with provided ticker

        Created object is set with the next available AssetClass.NOT_SET id, ticker, AssetClass.NOT_SET,
        AssetSubclass.NOT_SET

        Args:
            ticker (str): security ticker

        Returns:
            SecurityMaster: created object as described
        """
        return SecurityMaster.objects.create(my_id=SecurityMaster.generate_my_id(AssetClass.NOT_SET), ticker=ticker,
                                             asset_class=AssetClass.NOT_SET, asset_subclass=AssetSubClass.NOT_SET)

    def get_or_create_default(self, ticker):
        """ Get SecurityMaster object for ticker or create default

        This function is intended for use in an automated process where a ticker may or may not match an existing
        SecurityMaster object. If a default object is created, it should be set correctly by another process.
        See SecurityMasterDataManager.create_default()

        Args:
            ticker (str): security ticker

        Returns:
            SecurityMaster: existing object with matching ticker or a new default object with ticker
        """
        try:
            return SecurityMaster.objects.get(ticker=ticker)
        except ObjectDoesNotExist:
            return self.create_default(ticker)

    def convert_asset_class(self, security_master, asset_class, asset_subclass):
        """ Convert existing SecurityMaster object to another AssetClass or AssetSubClass

        ticker does not change. my_id changes if asset_class changes.

        Args:
            security_master (SecurityMaster): existing SecurityMaster object
            asset_class (AssetClass): convert to this AssetClass
            asset_subclass (AssetSubClass): convert to this AssetSubClass

        Returns:
            SecurityMaster: converted and saved SecurityMaster object
        """
        if asset_class != security_master.asset_class:
            new_my_id = SecurityMaster.generate_my_id(asset_class)
            security_master.my_id = new_my_id
            security_master.asset_class = asset_class
        security_master.asset_subclass = asset_subclass
        security_master.save()
        return security_master


class SecurityMaster(models.Model):
    """ Security Master Model

    Attributes:
        my_id (str): must have format "[a-Z][a-Z]_[0-9][0-9][0-9][0-9][0-9][0-9][0-9]"
            (i.e. two letters, underscore, 7 digits)
        ticker (str): common ticker for security
        asset_class (SecurityMaster.AssetClass):
        asset_subclass (SecurityMaster.AssetSubClass):
    """
    class AssetClass(models.TextChoices):
        """ Major class of this investment security.
        Classes: bond, equity, not_set, option
        not_set is not an actual class. it indicates that this security needs to have its asset class set
        """
        BOND = "BOND", gettext_lazy("BOND")
        CRYPTO = "CRYPTO", gettext_lazy("CRYPTO")
        EQUITY = "EQUITY", gettext_lazy("EQUITY")
        FX = "FX", gettext_lazy("FX")
        NOT_SET = "NOT_SET", gettext_lazy("NOT_SET")
        OPTION = "OPTION", gettext_lazy("OPTION")

        @staticmethod
        def get_my_id_prefix(asset_class):
            """ Get 3 character prefix of my_id for asset_class

            Prefix has the format [a-Z][a-Z]_. Typically, the first 2 letters of the asset class (e.g. BOND -> BO_) or
            the first letter of the first two words of the asset class (e.g. NOT_SET -> NS_) but this is not enforced

            Args:
                asset_class (AssetClass): get 3 character prefix of my_id for this class

            Returns:
                str: 3 characters

            Raises:
                ValueError: if asset_class is not set in this function
            """
            if asset_class == AssetClass.BOND:
                return "BO_"
            elif asset_class == AssetClass.CRYPTO:
                return "CR_"
            elif asset_class == AssetClass.EQUITY:
                return "EQ_"
            elif asset_class == AssetClass.FX:
                return "FX_"
            elif asset_class == AssetClass.NOT_SET:
                return "NS_"
            elif asset_class == AssetClass.OPTION:
                return "OP_"
            else:
                raise ValueError(str(asset_class) + " not set in SecurityMaster.AssetClass.get_my_id_prefix()")

        @staticmethod
        def get_subclasses(asset_class):
            """ Get valid subclasses of asset_class

            Args:
                asset_class (AssetClass): get subclasses for this class

            Returns:
                tuple[AssetSubClass]: valid subclasses of asset_class

            Raises:
                ValueError: if asset_class is not set in this function
            """
            if asset_class == AssetClass.BOND:
                return AssetSubClass.CORP_BOND, AssetSubClass.GOV_BOND, AssetSubClass.MUNI_BOND
            elif asset_class == AssetClass.CRYPTO:
                return AssetSubClass.CRYPTO,
            elif asset_class == AssetClass.EQUITY:
                return AssetSubClass.COMMON_STOCK, AssetSubClass.ETF
            elif asset_class == AssetClass.FX:
                return AssetSubClass.FX,
            elif asset_class == AssetClass.NOT_SET:
                return AssetSubClass.NOT_SET,
            elif asset_class == AssetClass.OPTION:
                return AssetSubClass.EQUITY_OPTION, AssetSubClass.INDEX_OPTION
            else:
                raise ValueError(str(asset_class) + " not set in SecurityMaster.AssetClass.get_subclasses()")

    class AssetSubClass(models.TextChoices):
        """ Minor class of this investment security.
        bonds: corporate bond, government bond, municipal bond
        equities: common stock, etf
        options: equity option, index option
        not_set is not an actual subclass. it indicates that this security needs to have its asset subclass set
        """
        COMMON_STOCK = "COMMON_STOCK", gettext_lazy("COMMON_STOCK")
        CORP_BOND = "CORP_BOND", gettext_lazy("CORP_BOND")
        CRYPTO = "CRYPTO", gettext_lazy("CRYPTO")
        EQUITY_OPTION = "EQUITY_OPTION", gettext_lazy("EQUITY_OPTION")
        ETF = "ETF", gettext_lazy("ETF")
        FX = "FX", gettext_lazy("FX")
        GOV_BOND = "GOV_BOND", gettext_lazy("GOV_BOND")
        INDEX_OPTION = "INDEX_OPTION", gettext_lazy("INDEX_OPTION")
        MUNI_BOND = "MUNI_BOND", gettext_lazy("MUNI_BOND")
        NOT_SET = "NOT_SET", gettext_lazy("NOT_SET")

        @staticmethod
        def get_class(asset_subclass):
            """ Get major asset class of asset_subclass

            Args:
                asset_subclass (AssetSubClass): get major asset class for this sub class

            Returns:
                AssetClass: major asset class for this sub class

            Raises:
                ValueError: if asset_subclass is not set in this function
            """
            if asset_subclass in (AssetSubClass.CORP_BOND, AssetSubClass.GOV_BOND, AssetSubClass.MUNI_BOND):
                return AssetClass.BOND
            if asset_subclass in (AssetSubClass.CRYPTO,):
                return AssetClass.CRYPTO
            elif asset_subclass in (AssetSubClass.COMMON_STOCK, AssetSubClass.ETF):
                return AssetClass.EQUITY
            elif asset_subclass in (AssetSubClass.FX,):
                return AssetClass.FX
            elif asset_subclass in (AssetSubClass.NOT_SET,):
                return AssetClass.NOT_SET
            elif asset_subclass in (AssetSubClass.EQUITY_OPTION, AssetSubClass.INDEX_OPTION):
                return AssetClass.OPTION
            else:
                raise ValueError(str(asset_subclass) + " not set in SecurityMaster.AssetSubClass.get_class()")

    # noinspection PyMethodParameters
    def validate_my_id(my_id):
        SecurityMaster.validate_my_id_partial(my_id)

    my_id = models.CharField(max_length=10, unique=True, validators=[validate_my_id])
    ticker = models.CharField(max_length=30, unique=True)
    asset_class = models.CharField(max_length=20, choices=AssetClass.choices)
    asset_subclass = models.CharField(max_length=20, choices=AssetSubClass.choices)

    objects = SecurityMasterDataManager()

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        self._validate_my_id_full()
        self._validate_asset_sub_class_for_asset_class()

    def save(self, *args, **kwargs):
        self._validate_my_id_full()
        self._validate_asset_sub_class_for_asset_class()
        return super().save(*args, **kwargs)

    def _validate_asset_sub_class_for_asset_class(self):
        if AssetClass(self.asset_class) != AssetSubClass.get_class(AssetSubClass(self.asset_subclass)):
            raise ValidationError(self.asset_class + " must have one of the following subclasses: " +
                                  str(AssetClass.get_subclasses(AssetClass(self.asset_class))))

    def _validate_my_id_full(self):
        SecurityMaster.validate_my_id_partial(self.my_id)
        has_prefix = self.my_id[:3]
        must_have_prefix = AssetClass.get_my_id_prefix(AssetClass(self.asset_class))
        if self.my_id[:3] != must_have_prefix:
            raise ValidationError(str(self.asset_class) + " security my_id must have prefix '" + must_have_prefix +
                                  "' but has prefix '" + has_prefix + "'.")

    @classmethod
    def generate_my_id(cls, asset_class):
        """ Generate next available my_id for this asset class

        The letters after the _ are all digits. Find the max of these and add 1 to it. If no securities for asset class
        found, the digits are set to "0000001"

        Args:
            asset_class (AssetClass): generate next available my_id for this asset class

        Returns:
            str: next available my_id for this asset class
        """
        max_my_id = SecurityMaster.objects.filter(asset_class=asset_class).aggregate(models.Max("my_id"))["my_id__max"]
        if max_my_id is None:
            max_my_id = AssetClass.get_my_id_prefix(asset_class) + "0000000"
        return AssetClass.get_my_id_prefix(asset_class) + str(int(max_my_id[3:]) + 1).zfill(7)

    @staticmethod
    def validate_my_id_partial(my_id):
        RegexValidator(regex=r'^[a-zA-Z]{2}_[0-9]{7}$',
                       message="my_id: " + my_id + " must have 10 characters total, '_' at third character and " +
                               "all characters after '_' must be digits 0-9.")(my_id)


AssetClass = SecurityMaster.AssetClass
AssetSubClass = SecurityMaster.AssetSubClass
