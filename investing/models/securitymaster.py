from decimal import Decimal, InvalidOperation
from typing import Union
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy


class SecurityMasterDataManager(models.Manager):

    def change_ticker(self, old_ticker, new_ticker):
        """ Change old ticker to new ticker

        Args:
            old_ticker (str):
            new_ticker (str):

        Raises:
            Union[IntegrityError, ObjectDoesNotExist]: IntegrityError if a SecurityMaster with new_ticker exists,
                ObjectDoesNotExist if SecurityMaster with old_ticker does not exist
        """
        sm = SecurityMaster.objects.get(ticker=old_ticker)
        sm.ticker = new_ticker
        sm.save()

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

    def create_default(self, ticker, has_fidelity_lots=True):
        """ Create default SecurityMaster object with provided ticker

        Created object is set with the next available AssetClass.NOT_SET id, ticker, AssetClass.NOT_SET,
        AssetSubclass.NOT_SET

        Args:
            ticker (str): security ticker
            has_fidelity_lots (boolean): See SecurityMaster.has_fidelity_lots. Default True

        Returns:
            SecurityMaster: created object as described
        """
        return SecurityMaster.objects.create(
            my_id=SecurityMaster.generate_my_id(AssetClass.NOT_SET), ticker=ticker, asset_class=AssetClass.NOT_SET,
            asset_subclass=AssetSubClass.NOT_SET, has_fidelity_lots=has_fidelity_lots)

    def get_or_create_default(self, ticker, has_fidelity_lots=True):
        """ Get SecurityMaster object for ticker or create default

        This function is intended for use in an automated process where a ticker may or may not match an existing
        SecurityMaster object. If a default object is created, it should be set correctly by another process.
        See SecurityMasterDataManager.create_default()

        Args:
            ticker (str): security ticker
            has_fidelity_lots (boolean): See create_default(). Default True

        Returns:
            SecurityMaster: existing object with matching ticker or a new default object with ticker
        """
        try:
            return SecurityMaster.objects.get(ticker=ticker)
        except ObjectDoesNotExist:
            return self.create_default(ticker, has_fidelity_lots=has_fidelity_lots)

    def field_to_security_dict(self, key_field, keys):
        """ Create dict of key_field to security with that key_field value

        Args:
            key_field (str): field of SecurityMaster whose values are the return dict keys, if a SecurityMaster object
                with that value for key_field is found. one of "pk", "my_id", "ticker"
            keys (list[Union[int, str]]): e.g. [1, 2], ["EQ_0000001", "OP_0000001"], ["AAPL", "MSFT"]

        Returns:
            dict: key_field (keys) to SecurityMaster object (values).
                e.g. {1: AAPL object}, {"EQ_0000001": AAPL object}, {"AAPL": AAPL object},

        Raises:
            ValueError: if key_field is not one of "pk", "my_id", "ticker"
        """
        if key_field not in ("pk", "my_id", "ticker"):
            raise ValueError("key_field must be one of 'pk', 'my_id', 'ticker'")
        d = {key_field + "__in": keys}
        return {getattr(sec, key_field): sec for sec in SecurityMaster.objects.filter(**d)}


class SecurityMaster(models.Model):
    """ Security Master Model

    Attributes:
        my_id (str): must have format "[a-Z][a-Z]_[0-9][0-9][0-9][0-9][0-9][0-9][0-9]"
            (i.e. two letters, underscore, 7 digits)
        ticker (str): common ticker for security
        asset_class (SecurityMaster.AssetClass):
        asset_subclass (SecurityMaster.AssetSubClass):
        underlying_security (SecurityMaster): required for options but other asset classes are optional
        expiration_date (datetime.date): required for options but other asset classes are optional
        option_type (OptionType): required for options but other asset classes are optional
        strike_price (Decimal): required for options but other asset classes are optional
        contract_size (int): required for options but other asset classes are optional. number of underlying securities
            covered by derivatives contract.
        has_fidelity_lots (boolean): True if broker FIDELITY breaks a Position in this security into lots. False if
            it does not. Default True
    """
    class AssetClass(models.TextChoices):
        """ Major class of this investment security.
        Classes: bond, crypto, equity, index, fx, mutual fund, not_set, option
        not_set is not an actual class. it indicates that this security needs to have its asset class set
        """
        BOND = "BOND", gettext_lazy("BOND")
        CRYPTO = "CRYPTO", gettext_lazy("CRYPTO")
        EQUITY = "EQUITY", gettext_lazy("EQUITY")
        INDEX = "INDEX", gettext_lazy("INDEX")
        FX = "FX", gettext_lazy("FX")
        MUTUAL_FUND = "MUTUAL_FUND", gettext_lazy("MUTUAL_FUND")
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
            elif asset_class == AssetClass.INDEX:
                return "IN_"
            elif asset_class == AssetClass.MUTUAL_FUND:
                return "MF_"
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
            elif asset_class == AssetClass.INDEX:
                return AssetSubClass.INDEX,
            elif asset_class == AssetClass.MUTUAL_FUND:
                return AssetSubClass.MONEY_MARKET,
            elif asset_class == AssetClass.NOT_SET:
                return AssetSubClass.NOT_SET,
            elif asset_class == AssetClass.OPTION:
                return AssetSubClass.EQUITY_OPTION, AssetSubClass.INDEX_OPTION
            else:
                raise ValueError(str(asset_class) + " not set in SecurityMaster.AssetClass.get_subclasses()")

    class AssetSubClass(models.TextChoices):
        """ Minor class of this investment security.
        bonds: corporate bond, government bond, municipal bond
        crypto: crypto
        equities: common stock, etf
        fx: fx
        index: index
        mutual fund: money market
        not_set is not an actual subclass. it indicates that this security needs to have its asset subclass set
        options: equity option, index option
        """
        COMMON_STOCK = "COMMON_STOCK", gettext_lazy("COMMON_STOCK")
        CORP_BOND = "CORP_BOND", gettext_lazy("CORP_BOND")
        CRYPTO = "CRYPTO", gettext_lazy("CRYPTO")
        EQUITY_OPTION = "EQUITY_OPTION", gettext_lazy("EQUITY_OPTION")
        ETF = "ETF", gettext_lazy("ETF")
        FX = "FX", gettext_lazy("FX")
        GOV_BOND = "GOV_BOND", gettext_lazy("GOV_BOND")
        INDEX = "INDEX", gettext_lazy("INDEX")
        INDEX_OPTION = "INDEX_OPTION", gettext_lazy("INDEX_OPTION")
        MONEY_MARKET = "MONEY_MARKET", gettext_lazy("MONEY_MARKET")
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
            elif asset_subclass in (AssetSubClass.INDEX,):
                return AssetClass.INDEX
            elif asset_subclass in (AssetSubClass.MONEY_MARKET,):
                return AssetClass.MUTUAL_FUND
            elif asset_subclass in (AssetSubClass.NOT_SET,):
                return AssetClass.NOT_SET
            elif asset_subclass in (AssetSubClass.EQUITY_OPTION, AssetSubClass.INDEX_OPTION):
                return AssetClass.OPTION
            else:
                raise ValueError(str(asset_subclass) + " not set in SecurityMaster.AssetSubClass.get_class()")

    class OptionType(models.TextChoices):
        AMERICAN_CALL = "AMERICAN_CALL", gettext_lazy("AMERICAN_CALL")
        AMERICAN_PUT = "AMERICAN_PUT", gettext_lazy("AMERICAN_PUT")
        EUROPEAN_CALL = "EUROPEAN_CALL", gettext_lazy("EUROPEAN_CALL")
        EUROPEAN_PUT = "EUROPEAN_PUT", gettext_lazy("EUROPEAN_PUT")

    # noinspection PyMethodParameters
    def validate_my_id(my_id):
        SecurityMaster.validate_my_id_partial(my_id)

    my_id = models.CharField(max_length=10, unique=True, validators=[validate_my_id], default="NS_0000000")
    ticker = models.CharField(max_length=30, unique=True)
    asset_class = models.CharField(max_length=20, choices=AssetClass.choices)
    asset_subclass = models.CharField(max_length=20, choices=AssetSubClass.choices)
    underlying_security = models.ForeignKey("self", on_delete=models.PROTECT, blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    option_type = models.CharField(max_length=15, choices=OptionType.choices, blank=True, null=True)
    strike_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    contract_size = models.PositiveIntegerField(blank=True, null=True)
    has_fidelity_lots = models.BooleanField(default=True)

    objects = SecurityMasterDataManager()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        """ __str__ override

        Format:
            self.ticker, self.asset_class, self.asset_subclass

        Returns:
            str: as described by Format
        """
        return self.ticker + ", " + self.asset_class + ", " + self.asset_subclass

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        self._validate_my_id_full()
        self._validate_asset_sub_class_for_asset_class()
        self._validate_option_data()

    def save(self, *args, **kwargs):
        self._validate_my_id_full()
        self._validate_asset_sub_class_for_asset_class()
        self._validate_option_data()
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

    def _validate_option_data(self):
        if AssetClass(self.asset_class) == AssetClass.OPTION and \
                (self.underlying_security is None or self.expiration_date is None or self.option_type is None or
                 self.strike_price is None or self.contract_size is None):
            raise ValidationError("Options must have fields: 'underlying security', 'expiration date', 'option type',"
                                  " 'strike price' and 'contract_size' set.")

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

    @classmethod
    def get_option_data_from_ticker(cls, ticker):
        """ Get underlying security, expiration date, option type, strike price and contract size from ticker

        This function assumes all options are American Call or American Put and assumes the ticker is in Fidelity
        format and assumes contract size is 100. Will need to update if any of these assumptions are wrong.

        Args:
            ticker (str): option ticker expected to have Fidelity format: underlyingtickerYYMMDD[C,P]strikeprice
                option type is determined from the last 'C' or 'P'
                expiration date is the 6 numbers before the last 'C' or 'P'
                underlying ticker is the characters before the expiration date
                strike price is the decimal number after the last 'C' or 'P'
                e.g. AAPL220916C41.5, MSFT220916P325

        Returns:
            tuple[SecurityMaster, datetime.date, OptionType, Decimal, int]: underlying security, expiration date,
                option type, strike price, contract size

        Raises:
            InvalidOperation: if strike price in ticker does not convert to a Decimal
            ObjectDoesNotExist: if underlying security does not exist
            ValueError: if expiration date in ticker is not 6 numbers, if option type in ticker is not 'C' or 'P'
        """
        cp_ind = max(ticker.rfind("C"), ticker.rfind("P"))
        if cp_ind == -1:
            raise ValueError(ticker + " - option type must be 'C' or 'P'.")

        underlying_security = ticker[:cp_ind - 6]
        try:
            underlying_security = SecurityMaster.objects.get(ticker=underlying_security)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist(ticker + " - Underlying Security with ticker " + underlying_security +
                                     " does not exist.")
        exp_date = ticker[cp_ind - 6: cp_ind]
        if len(exp_date) != 6:
            raise ValueError(ticker + " - expiration date " + exp_date + " must have 6 numbers.")
        exp_date = datetime.date(int("20" + exp_date[:2]), int(exp_date[2:4]), int(exp_date[4:]))
        opt_type = OptionType.AMERICAN_CALL if ticker[cp_ind] == "C" else OptionType.AMERICAN_PUT
        strike_price = Decimal(ticker[cp_ind+1:])
        return underlying_security, exp_date, opt_type, strike_price, 100

    @staticmethod
    def validate_my_id_partial(my_id):
        RegexValidator(regex=r'^[a-zA-Z]{2}_[0-9]{7}$',
                       message="my_id: " + my_id + " must have 10 characters total, '_' at third character and " +
                               "all characters after '_' must be digits 0-9.")(my_id)


class TickerHistory(models.Model):
    """ Ticker History

    Track ticker changes due to merger, ticker change, etc.

    Attributes:
        security (SecurityMaster): object on which the change happened. note that it is possible that after subsequent
            changes, the ticker on this object might not be new_ticker
        new_ticker (str): ticker being changed to
        old_ticker (str): ticker being changed from
        change_date (datetime.date): date on which the change happened
        change_type (ChangeType):
    """
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["security", "change_date", "change_type"],
                                    name="unique_%(app_label)s_%(class)s_sm_cd_ct"),
        ]

    class ChangeType(models.TextChoices):
        MERGER = "MERGER", gettext_lazy("Merger")

    security = models.ForeignKey(SecurityMaster, on_delete=models.PROTECT)
    new_ticker = models.CharField(max_length=30)
    old_ticker = models.CharField(max_length=30)
    change_date = models.DateField()
    change_type = models.CharField(max_length=11, choices=ChangeType.choices)


AssetClass = SecurityMaster.AssetClass
AssetSubClass = SecurityMaster.AssetSubClass
ChangeType = TickerHistory.ChangeType
OptionType = SecurityMaster.OptionType
