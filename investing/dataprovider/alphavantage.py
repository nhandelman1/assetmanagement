from decimal import Decimal
from enum import Enum
from io import StringIO
from json import JSONDecodeError
from typing import Any, Optional, Union
import datetime
import logging
import requests

import numpy as np
import pandas as pd

from .dataproviderexception import DataProviderException


class Endpoints(Enum):
    TIME_SERIES_INTRADAY = "TIME_SERIES_INTRADAY"
    TIME_SERIES_DAILY = "TIME_SERIES_DAILY"
    TIME_SERIES_DAILY_ADJUSTED = "TIME_SERIES_DAILY_ADJUSTED"
    TIME_SERIES_WEEKLY = "TIME_SERIES_WEEKLY"
    TIME_SERIES_WEEKLY_ADJUSTED = "TIME_SERIES_WEEKLY_ADJUSTED"
    TIME_SERIES_MONTHLY = "TIME_SERIES_MONTHLY"
    TIME_SERIES_MONTHLY_ADJUSTED = "TIME_SERIES_MONTHLY_ADJUSTED"

    NEWS_SENTIMENT = "NEWS_SENTIMENT"
    TOP_GAINERS_LOSERS = "TOP_GAINERS_LOSERS"

    OVERVIEW = "OVERVIEW"
    INCOME_STATEMENT = "INCOME_STATEMENT"
    BALANCE_SHEET = "BALANCE_SHEET"
    CASH_FLOW = "CASH_FLOW"
    EARNINGS = "EARNINGS"
    LISTING_STATUS = "LISTING_STATUS"
    EARNINGS_CALENDAR = "EARNINGS_CALENDAR"
    IPO_CALENDAR = "IPO_CALENDAR"

    REAL_GDP = "REAL_GDP"
    REAL_GDP_PER_CAPITA = "REAL_GDP_PER_CAPITA"
    TREASURY_YIELD = "TREASURY_YIELD"
    FEDERAL_FUNDS_RATE = "FEDERAL_FUNDS_RATE"
    CPI = "CPI"
    INFLATION = "INFLATION"
    RETAIL_SALES = "RETAIL_SALES"
    DURABLES = "DURABLES"
    UNEMPLOYMENT = "UNEMPLOYMENT"
    NONFARM_PAYROLL = "NONFARM_PAYROLL"


class IntradayInterval(Enum):
    """
    Time interval between two consecutive data points in the time series
    """
    M1 = "1min"
    M5 = "5min"
    M15 = "15min"
    M30 = "30min"
    M60 = "60min"


class OutputSize(Enum):
    """
    COMPACT: return latest 100 datapoints for query
    FULL: return all datapoints for query
    """
    COMPACT = "compact"
    FULL = "full"


class DataType(Enum):
    JSON = "json"
    CSV = "csv"


class ListingStatus(Enum):
    """
    ACTIVE: active symbols
    DELISTED: delisted symbols
    """
    ACTIVE = "active"
    DELISTED = "delisted"


class EarningsHorizon(Enum):
    M3 = "3month"
    M6 = "6month"
    M12 = "12month"


class EcoInterval(Enum):
    QUARTER = "quarterly"
    ANNUAL = "annual"


class TreasuryInterval(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TreasuryMaturity(Enum):
    M3 = "3month"
    Y2 = "2year"
    Y5 = "5year"
    Y7 = "7year"
    Y10 = "10year"
    Y30 = "30year"


class CPIInterval(Enum):
    MONTHLY = "monthly"
    SEMIANNUAL = "semiannual"


class TopicSentiment:
    """ Topic Sentiment

    Attributes must match models.newssentiment.TopicSentiment attributes.

    Attributes:
            topic (str): topic on which the article is about
            relevance_score (Decimal): a score of how relevant the article is to the topic, "0 < x <= 1, with a higher
                score indicating higher relevance.
    """
    class Topic(Enum):
        """
        Enums must match models.newssentiment.TopicSentiment.Topic enums.
        """
        BLOCKCHAIN = "blockchain"
        EARNINGS = "earnings"
        ECONOMY_FISCAL = "economy_fiscal"
        ECONOMY_MACRO = "economy_macro"
        ECONOMY_MONETARY = "economy_monetary"
        ENERGY_TRANSPORTATION = "energy_transportation"
        FINANCE = "finance"
        FINANCIAL_MARKETS = "financial_markets"
        IPO = "ipo"
        LIFE_SCIENCES = "life_sciences"
        MANUFACTURING = "manufacturing"
        MERGERS_ACQUISITIONS = "mergers_and_acquisitions"
        REAL_ESTATE_CONSTRUCTION = "real_estate"
        RETAIL_WHOLESALE = "retail_wholesale"
        TECHNOLOGY = "technology"

        @staticmethod
        def from_label(label):
            """ Get Topic associated with AlphaVantage label

            Labels must match models.newssentiment.TopicSentiment.Topic labels.

            Args:
                label (str):

            Returns:
                TopicSentiment.Topic: Topic associated with label
            """
            if label == "Blockchain":
                return TopicSentiment.Topic.BLOCKCHAIN
            elif label == "Earnings":
                return TopicSentiment.Topic.EARNINGS
            elif label == "Economy - Fiscal":
                return TopicSentiment.Topic.ECONOMY_FISCAL
            elif label == "Economy - Macro":
                return TopicSentiment.Topic.ECONOMY_MACRO
            elif label == "Economy - Monetary":
                return TopicSentiment.Topic.ECONOMY_MONETARY
            elif label == "Energy & Transportation":
                return TopicSentiment.Topic.ENERGY_TRANSPORTATION
            elif label == "Finance":
                return TopicSentiment.Topic.FINANCE
            elif label == "Financial Markets":
                return TopicSentiment.Topic.FINANCIAL_MARKETS
            elif label == "IPO":
                return TopicSentiment.Topic.IPO
            elif label == "Life Sciences":
                return TopicSentiment.Topic.LIFE_SCIENCES
            elif label == "Manufacturing":
                return TopicSentiment.Topic.MANUFACTURING
            elif label == "Mergers & Acquisitions":
                return TopicSentiment.Topic.MERGERS_ACQUISITIONS
            elif label == "Real Estate & Construction":
                return TopicSentiment.Topic.REAL_ESTATE_CONSTRUCTION
            elif label == "Retail & Wholesale":
                return TopicSentiment.Topic.RETAIL_WHOLESALE
            elif label == "Technology":
                return TopicSentiment.Topic.TECHNOLOGY
            else:
                raise ValueError(label + " does not match a TopicSentiment.Topic")

    def __init__(self, topic, relevance_score):
        self.topic = topic
        self.relevance_score = relevance_score

    @staticmethod
    def json_dict_constructor(topic_dict):
        """ Create TopicSentiment instance from topic_dict

        Args:
            topic_dict (dict[str, Union[str, float]]): "topic": "topic label", "relevance_score": Union[float, str]

        Returns:
            TopicSentiment: created instance

        Raises:
            ValueError: if topic does not match a label in TopicSentiment.Topic
        """
        return TopicSentiment(topic=TopicSentiment.Topic.from_label(topic_dict["topic"]),
                              relevance_score=Decimal(str(topic_dict["relevance_score"])))


class TickerSentimentLabel(Enum):
    """ Label for ticker sentiment
    Sentiment labels: Bearish, Somewhat-Bearish, Neutral, Somewhat-Bullish, Bullish
    ticker sentiment score and label: x <= -0.35: Bearish; -0.35 < x <= -0.15: Somewhat-Bearish;
        -0.15 < x < 0.15: Neutral; 0.15 <= x < 0.35: Somewhat_Bullish; x >= 0.35: Bullish
    Enums must match models.newssentiment.TickerSentimentLabel enums.
    """
    BEARISH = "Bearish"
    SOMEWHAT_BEARISH = "Somewhat-Bearish"
    NEUTRAL = "Neutral"
    SOMEWHAT_BULLISH = "Somewhat-Bullish"
    BULLISH = "Bullish"

    @staticmethod
    def from_label(label):
        """ Get TickerSentimentLabel associated with AlphaVantage label

        Args:
            label (str):

        Returns:
            TickerSentimentLabel.Topic: TickerSentimentLabel associated with label

        Raises:
            ValueError if label is not associated with a TickerSentimentLabel
        """
        return TickerSentimentLabel(label)


class TickerSentiment:
    """ Ticker Sentiment

    Attributes:
        ticker (str): ticker on which the article is about. might not match ticker in security_master
        relevance_score (Decimal): a score of how relevant the article is to the ticker
            "0 < x <= 1, with a higher score indicating higher relevance.
        ticker_sentiment_score (Decimal): score of the sentiment the article implies for the ticker
        ticker_sentiment_label (TickerSentimentLabel): label of the sentiment the article implies for the ticker
    """
    def __init__(self, ticker, relevance_score, ticker_sentiment_score, ticker_sentiment_label):
        self.ticker = ticker
        self.relevance_score = relevance_score
        self.ticker_sentiment_score = ticker_sentiment_score
        self.ticker_sentiment_label = ticker_sentiment_label

    @staticmethod
    def json_dict_constructor(ts_dict):
        """ Create TickerSentiment instance from ts_dict

        Args:
            ts_dict (dict[str, Union[str, float]]): "ticker": "ticker", "relevance_score": Union[float, str],
                "ticker_sentiment_score": Union[float, str], "ticker_sentiment_label": "label"
                Prefixes "CRYPTO:" and "FOREX:" are removed from "ticker" in this function

        Returns:
            TickerSentiment: created instance

        Raises:
            ValueError: ValueError if ticker sentiment label does not match a label in TickerSentimentLabel
        """
        ticker = ts_dict["ticker"]
        return TickerSentiment(
            ticker[7:] if ticker[:7] == "CRYPTO:" else ticker[6:] if ticker[:6] == "FOREX:" else ticker,
            Decimal(str(ts_dict["relevance_score"])), Decimal(str(ts_dict["ticker_sentiment_score"])),
            TickerSentimentLabel(ts_dict["ticker_sentiment_label"]))


class NewsSentiment:
    """ Market news & sentiment data

    This class is designed based on the data returned by AlphaVantage Market News & Sentiment endpoint. This class and
    documentation may need to change if other sources are used.

    Attributes:
        title (str): article title
        url (str): article url
        time_published (datetime.datetime):
        authors (str): article authors. ; delimited
        summary (str): article summary
        source (str): article source
        category_within_source (str): the category that the source puts the article into
        topics (list[TopicSentiment]):
        overall_sentiment_score (Decimal):
        overall_sentiment_label (TickerSentimentLabel):
        ticker_sentiments (list[TickerSentiment]):
    """
    def __init__(self, title, url, time_published, authors, summary, source, category_within_source, topics,
                 overall_sentiment_score, overall_sentiment_label, ticker_sentiments):
        self.title = title
        self.url = url
        self.time_published = time_published
        self.authors = authors
        self.summary = summary
        self.source = source
        self.category_within_source = category_within_source
        self.topics = topics
        self.overall_sentiment_score = overall_sentiment_score
        self.overall_sentiment_label = overall_sentiment_label
        self.ticker_sentiments = ticker_sentiments

    @staticmethod
    def json_dict_constructor(ns_dict):
        """ Create NewsSentiment instance from ns_dict

        Args:
            ns_dict (dict[str, str]): "title": str, "url": url str, "time_published": YYYYMMDDTHHMMSS str,
                "authors": list[str], "summary": str, "source": str, "category_within_source": str,
                "topics": list[dict[str, Union[str, float]]], "overall_sentiment_score": Union[str, float],
                "overall_sentiment_label": str, "ticker_sentiment": list[dict[str, Union[str, float]]]

        Returns:
            NewsSentiment: created instance

        Raises:
            ValueError: ValueError if either TickerSentiment.json_dict_constructor() or
                TopicSentiment.json_dict_constructor()  raises a ValueError
        """
        return NewsSentiment(
            ns_dict["title"], ns_dict["url"], datetime.datetime.strptime(ns_dict["time_published"], "%Y%m%dT%H%M%S"),
            ";".join(ns_dict["authors"]), ns_dict["summary"], ns_dict["source"], ns_dict["category_within_source"],
            [TopicSentiment.json_dict_constructor(d) for d in ns_dict["topics"]],
            Decimal(str(ns_dict["overall_sentiment_score"])), TickerSentimentLabel(ns_dict["overall_sentiment_label"]),
            [TickerSentiment.json_dict_constructor(d) for d in ns_dict["ticker_sentiment"]])


class AlphaVantage:
    """ Access AlphaVantage API using requests package and return data as pandas dataframes

    Class Attributes:
        _URL_BASE (str): base of url for all API endpoints

    Attributes:
        api_key (str): API key for access to API
        logger (logging.Logger):
    """
    _URL_BASE = "https://www.alphavantage.co/query?"

    def __init__(self):
        self.api_key = "QH8F7RKNS3R4VXP7"
        self.logger = logging.getLogger(__name__)

    def _base_create_url(self, endpoint, param_dict):
        """ See _base_request()

        This functionality is split into its own function so it can be tested without sending a request to the API

        Args:
            See _base_request()

        Returns:
            str: alphavantage url
        """
        def to_str_or_none(val1):
            if val1 is None:
                return None

            if isinstance(val1, Enum):
                val1 = val1.value
            elif isinstance(val1, bool):
                val1 = str(val1).lower()
            elif isinstance(val1, datetime.datetime):
                # must put datetime.datetime check before datetime.date since datetime is a subclass of date
                val1 = val1.strftime("%Y%m%dT%H%M")
            elif isinstance(val1, datetime.date):
                val1 = val1.strftime("%Y-%m-%d")

            return str(val1)

        param_str = ""
        for param, val in param_dict.items():
            if isinstance(val, (list, tuple)):
                val = None if len(val) == 0 else ",".join([to_str_or_none(x) for x in val])
            else:
                val = to_str_or_none(val)

            if val is not None:
                param_str += ("&" + param + "=" + val)

        return AlphaVantage._URL_BASE + "function=" + endpoint.value + param_str + "&apikey=" + self.api_key

    def _base_request(self, endpoint, param_dict):
        """ Compile AlphaVantage URL, send request and handle response

        Args:
            endpoint (Endpoints):
            param_dict (dict[str, Any]): keys are url parameter names. values are API parameter values and are handled
                as follows: Enum -> .value, bool -> str(bool).lower(), datetime.datetime -> str format YYYYMMDDTHHMM,
                datetime.date -> str format YYYY-MM-DD, list/tuple -> conversions for scalar elements applied to each
                element and all elements joined with ",", all others -> str(value)

        Returns:
            requests.Response: callers of this function handle the response

        Raises:
            DataProviderException: if response status code is not 200 or response text is an error or information
                message. exception message is logged and exception is raised
        """
        url = self._base_create_url(endpoint, param_dict)

        response = requests.get(url)

        if response.status_code != 200:
            self.logger.exception("Status Code: " + str(response.status_code) + ", Reason: " + response.reason)
            raise DataProviderException("Status Code: " + str(response.status_code) + ", Reason: " + response.reason +
                                        ", See log for full trace.")
        else:
            try:
                # status code can be 200 but response still indicates an error
                res_dict = response.json()
                if any([x in res_dict for x in ["Error Message", "Information"]]):
                    self.logger.exception("URL: " + response.url + ", Text: " + response.text)
                    raise DataProviderException("URL: " + response.url + ", Text: " + response.text +
                                                " See log for full trace.")
            except JSONDecodeError:
                # response is not JSON format. this is ok (probably requested CSV format)
                pass

        return response

    def intraday(self, symbol, interval=IntradayInterval.M1, adjusted=True, extended_hours=True, month=None,
                 output_size=OutputSize.FULL):
        """ Current and 20+ years of historical intraday OHLCV time series of the equity specified

        Args:
            symbol (str): e.g. IBM
            interval (IntradayInterval): Default IntradayInterval.M1
            adjusted (boolean):  False for raw (as-traded) intraday values. Default True for output time series is
                adjusted by historical split and dividend events (all ohlcv are adjusted)
            extended_hours (boolean): False for regular trading hours (9:30am to 4:00pm US Eastern Time) only. Default
                True for output time series will include both the regular trading hours and the extended trading hours
                (4:00am to 8:00pm Eastern Time for the US market).
            month (Optional[datetime.date]): get data for this month. Must be year 2000 or greater. Default None to get
                most recent 30 trading days
            output_size (OutputSize): Default OutputSize.FULL

        Returns:
            pd.DataFrame: columns as follows: timestamp (datetime.datetime), open/high/low/close (float64),
                volume (int64)

        Raises:
            Union[ValueError, DataProviderException]: ValueError if month is earlier than 2000. DataProviderException
                if api request returns an error
        """
        if month is not None and month < datetime.date(2000, 1, 1):
            raise ValueError("month must be in year 2000 or more recent")

        param_dict = {
            "symbol": symbol,
            "interval": interval,
            "adjusted": adjusted,
            "extended_hours": extended_hours,
            "month": None,
            "outputsize": output_size,
            "datatype": DataType.CSV
        }
        if isinstance(month, datetime.date):
            param_dict["month"] = datetime.date.strftime(month, "%Y-%m")

        response = self._base_request(Endpoints.TIME_SERIES_INTRADAY, param_dict)

        df = pd.read_csv(StringIO(response.text))
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df

    def daily(self, symbol, adjusted=True, output_size=OutputSize.FULL):
        """ Current and 20+ years of historical daily OHLCV time series of the equity specified

        Args:
            symbol (str): e.g. IBM
            adjusted (boolean):  False for raw (as-traded) daily values. Default True to include daily adjusted close,
                dividend amount and split coefficient values (adjusted data requires premium API service
            output_size (OutputSize): Default OutputSize.FULL

        Returns:
            pd.DataFrame: columns as follows: timestamp (datetime.date), open/high/low/close
                (float64), adjusted_close (float64, adjusted only), volume (int64),
                dividend_amount/split_coefficient (float64, adjusted only)

        Raises:
            DataProviderException: if api request returns an error
        """
        param_dict = {
            "symbol": symbol,
            "outputsize": output_size,
            "datatype": DataType.CSV
        }
        endpoint = Endpoints.TIME_SERIES_DAILY_ADJUSTED if adjusted else Endpoints.TIME_SERIES_DAILY
        response = self._base_request(endpoint, param_dict)
        df = pd.read_csv(StringIO(response.text))
        if adjusted:
            df = df.astype({"dividend_amount": "float64", "split_coefficient": "float64"})
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.date

        return df

    def news_and_sentiment(self, stock_ticker=None, crypto_ticker=None, forex_ticker=None, topics_list=(),
                           start_dt=None, end_dt=None):
        """ Live and historical market news & sentiment data

        Live and historical market news & sentiment data from a large & growing selection of premier news outlets
        around the world, covering stocks, cryptocurrencies, forex, and a wide range of topics such as fiscal policy,
        mergers & acquisitions, IPOs, etc.
        Articles returned will mention all of the symbols in stock_ticker, crypto_ticker and/or forex_ticker.

        Args:
            stock_ticker (Optional[str]): articles that mention this ticker. Default None for all tickers
            crypto_ticker (Optional[str]): articles that mention this crypto. This function prepends "CRYPTO:".
                Default None for all cryptos
            forex_ticker (Optional[str]): articles that mention this FX. This function prepends "FOREX:".
                Default () for all FXs
            topics_list (list[TopicSentiment.Topic]): articles that mention all of these news topics.
                Default () for all topics
            start_dt (Optional[datetime.datetime]): articles published on or after this datetime. Default None for no
                lower datetime limit.
            end_dt (Optional[datetime.datetime]): articles published on or before this datetime. Default None for no
                upper datetime limit.

        Returns:
            list[NewsSentiment]: NewsSentiment objects are unsaved

        Raises:
            Union[ValueError, DataProviderException]: DataProviderException if api request returns an error
        """

        crypto_ticker = None if crypto_ticker is None else "CRYPTO:" + crypto_ticker
        forex_ticker = None if forex_ticker is None else "FOREX:" + forex_ticker

        param_dict = {
            "tickers": [x for x in [stock_ticker, crypto_ticker, forex_ticker] if x is not None],
            "topics": topics_list,
            "time_from": start_dt,
            "time_to": end_dt,
        }
        response = self._base_request(Endpoints.NEWS_SENTIMENT, param_dict)
        feed_list = response.json()["feed"]

        return [NewsSentiment.json_dict_constructor(d) for d in feed_list]

    def top_gain_lose_active(self):
        """ Top 20 gainers, losers, and the most active traded tickers in the US market

        In return dataframe, first 20 rows are top gainers, next 20 rows are top losers and last 20 rows are most
        actively traded.

        Returns:
            pd.DataFrame: columns as follows: date (datetime.date), category (category, "Gainer"/"Loser"/"Active"),
                symbol (str), price (float64), chng_amt (float64), chng_pct (float64, percent), volume (int64)

        Raises:
            DataProviderException: if api request returns an error
        """
        response = self._base_request(Endpoints.TOP_GAINERS_LOSERS, {})
        d = response.json()

        def to_df(key, category):
            df1 = pd.DataFrame.from_records(d[key])
            df1.insert(0, "category", category)
            return df1

        df = pd.concat([to_df("top_gainers", "Gainer"), to_df("top_losers", "Loser"),
                        to_df("most_actively_traded", "Active")], ignore_index=True)
        df = df.rename(columns={"ticker": "symbol", "change_amount": "chng_amt", "change_percentage": "chng_pct"})
        # insert traded date to dataframe
        df.insert(0, "date", datetime.datetime.strptime(d["last_updated"][:10], "%Y-%m-%d").date())
        # remove % symbol at end of string
        df["chng_pct"] = df["chng_pct"].str[:-1]
        df = df.astype({"category": "category", "price": "float64", "chng_amt": "float64", "chng_pct": "float64",
                        "volume": "int64"})

        return df

    def company_overview(self, symbol):
        """ Company information, financial ratios, and other key metrics for the equity specified.

        Data is generally refreshed on the same day a company reports its latest earnings and financials

        Args:
            symbol (str): e.g. IBM

        Returns:
            dict[str, str]: keys are data types (e.g. Symbol). values are data values (e.g. IBM)

        Raises:
            DataProviderException: if api request returns an error
        """
        param_dict = {
            "symbol": symbol,
        }

        response = self._base_request(Endpoints.OVERVIEW, param_dict)

        return response.json()

    def _financial_statement(self, endpoint, symbol):
        param_dict = {
            "symbol": symbol,
        }

        response = self._base_request(endpoint, param_dict)
        d = response.json()

        def to_df(key, rep_period):
            df1 = pd.DataFrame.from_records(d[key])
            df1.insert(0, "Report Period", rep_period)
            return df1

        df = pd.concat([to_df("annualReports", "Annual"), to_df("quarterlyReports", "Quarterly")], ignore_index=True)
        df.insert(0, "Symbol", symbol)
        df["fiscalDateEnding"] = pd.to_datetime(df["fiscalDateEnding"]).dt.date
        df.iloc[:, 4:] = df.iloc[:, 4:].replace("None", 0)
        df = df.astype({col: "int64" for col in df.columns if col not in
                        ["Symbol", "Report Period", "fiscalDateEnding", "reportedCurrency"]})

        return df

    def income_statement(self, symbol):
        """ annual and quarterly income statements for the company of interest

        With normalized fields mapped to GAAP and IFRS taxonomies of the SEC.
        Data is generally refreshed on the same day a company reports its latest earnings and financials.
        Seems to be 5 most recent annual statements and 20 most recent quarterly statements
        API returns "None" for income statement fields missing a value. This function converts these to 0

        Args:
            symbol (str): e.g. IBM

        Returns:
            pd.DataFrame: columns as follows: Symbol (str), Report Period ("Annual" or "Quarterly"),
                fiscalDateEnding (datetime.date), reportedCurrency (str), all others (int64).

        Raises:
            DataProviderException: if api request returns an error
        """
        return self._financial_statement(Endpoints.INCOME_STATEMENT, symbol)

    def balance_sheet(self, symbol):
        """ annual and quarterly balance sheets for the company of interest

        With normalized fields mapped to GAAP and IFRS taxonomies of the SEC.
        Data is generally refreshed on the same day a company reports its latest earnings and financials.
        Seems to be 5 most recent annual statements and 20 most recent quarterly statements
        API returns "None" for balance sheet fields missing a value. This function converts these to 0

        Args:
            symbol (str): e.g. IBM

        Returns:
            pd.DataFrame: columns as follows: Symbol (str), Report Period ("Annual" or "Quarterly"),
                fiscalDateEnding (datetime.date), reportedCurrency (str), all others (int64).

        Raises:
            DataProviderException: if api request returns an error
        """
        return self._financial_statement(Endpoints.BALANCE_SHEET, symbol)

    def cash_flow_statement(self, symbol):
        """ annual and quarterly cash flow statements for the company of interest

        With normalized fields mapped to GAAP and IFRS taxonomies of the SEC.
        Data is generally refreshed on the same day a company reports its latest earnings and financials.
        Seems to be 5 most recent annual statements and 20 most recent quarterly statements
        API returns "None" for income statement fields missing a value. This function converts these to 0

        Args:
            symbol (str): e.g. IBM

        Returns:
            pd.DataFrame: columns as follows: Symbol (str), Report Period ("Annual" or "Quarterly"),
                fiscalDateEnding (datetime.date), reportedCurrency (str), all others (int64).

        Raises:
            DataProviderException: if api request returns an error
        """
        return self._financial_statement(Endpoints.CASH_FLOW, symbol)

    def earnings(self, symbol):
        """ Annual and quarterly EPS related data for the company of interest.

        Quarterly data also includes analyst estimates and surprise metrics.
        Not guaranteed full history but seems to go back 20+ years
        Current year annual EPS is for YTD

        Args:
            symbol (str): e.g. IBM

        Returns:
            pd.DataFrame: columns as follows: Symbol (str), Earnings Period ("Annual" or "Quarterly"),
                fiscalDateEnding (datetime.date), reportedEPS (float64), reportedDate (pd.NaT or datetime.date),
                all others (float64)

        Raises:
            DataProviderException: if api request returns an error
        """
        param_dict = {
            "symbol": symbol,
        }

        response = self._base_request(Endpoints.EARNINGS, param_dict)
        d = response.json()

        def to_df(key, rep_type):
            df1 = pd.DataFrame.from_records(d[key])
            df1.insert(0, "Earnings Period", rep_type)
            return df1

        df = pd.concat([to_df("annualEarnings", "Annual"), to_df("quarterlyEarnings", "Quarterly")], ignore_index=True)
        df.insert(0, "Symbol", symbol)
        df["fiscalDateEnding"] = pd.to_datetime(df["fiscalDateEnding"]).dt.date
        df["reportedDate"] = pd.to_datetime(df["reportedDate"]).dt.date
        df = df.astype({col: "float64" for col in df.columns if col not in
                        ["Symbol", "Earnings Period", "fiscalDateEnding", "reportedDate"]})

        return df

    def listing_status(self, on_date, listing_status):
        """ Find all symbols by listing status on provided date

        Args:
            on_date (datetime.date): get listing status of symbols on this date. must be 2010-01-01 or more recent
            listing_status (ListingStatus): get symbols with this listing status

        Returns:
            pd.DataFrame: columns as follows: name (str), exchange (str), assetType (str), ipoDate (datetime.date).
                if listing_status == ListingStatus.DELISTED also include column delistingDate (datetime.date)

        Raises:
            Union[ValueError, DataProviderException]: ValueError if on_date < 2020-01-01. DataProviderException if api
                request returns an error
        """
        if on_date < datetime.date(2010, 1, 1):
            raise ValueError

        param_dict = {
            "date": on_date,
            "state": listing_status
        }

        response = self._base_request(Endpoints.LISTING_STATUS, param_dict)
        df = pd.read_csv(StringIO(response.text)).drop(columns=["status"])
        df["ipoDate"] = pd.to_datetime(df["ipoDate"]).dt.date
        if listing_status == ListingStatus.ACTIVE:
            df = df.drop(columns=["delistingDate"])
        else:  # delisted
            df["delistingDate"] = pd.to_datetime(df["delistingDate"]).dt.date

        return df

    def earnings_calendar(self):
        """ Query all upcoming company (quarterly?) earnings releases for the next 12 months

        The API allows for specification of a symbol or horizon (3, 6, 12 months). Use 12 month horizon since it
        is considered as only 1 API call.
        It looks like most symbols have 4 earnings releases provided, but some have up to 3 earnings releases provided.
        However, estimate in the returned dataframe is provided only for the soonest earnings release per symbol

        Returns:
            pd.DataFrame: columns as follows: symbol (str), name (str), reportDate (datetime.date),
                fiscalDateEnding (datetime.date), estimate (float64), currency (str)

        Raises:
            DataProviderException: DataProviderException if API request returns an error
        """
        param_dict = {
            "horizon": EarningsHorizon.M12
        }

        response = self._base_request(Endpoints.EARNINGS_CALENDAR, param_dict)
        df = pd.read_csv(StringIO(response.text)).astype({"estimate": "float64"})
        df["reportDate"] = pd.to_datetime(df["reportDate"]).dt.date
        df["fiscalDateEnding"] = pd.to_datetime(df["fiscalDateEnding"]).dt.date

        return df

    def ipo_calendar(self):
        """ Query all upcoming IPOs for the next 3

        Returns:
            pd.DataFrame: columns as follows: symbol (str), name (str), ipoDate (datetime.date),
                priceRangeLow (float64), priceRangeHigh (float64), currency (str), exchange (str)

        Raises:
            DataProviderException: DataProviderException if API request returns an error
        """
        response = self._base_request(Endpoints.IPO_CALENDAR, {})
        df = pd.read_csv(StringIO(response.text)).astype({"priceRangeLow": "float64", "priceRangeHigh": "float64"})
        df["ipoDate"] = pd.to_datetime(df["ipoDate"]).dt.date

        return df

    def real_gdp(self, interval):
        """ annual or quarterly Real GDP of the United States.

        U.S. Bureau of Economic Analysis, Real Gross Domestic Product. Retrieved from FRED.
        Possibly from here: https://fred.stlouisfed.org/series/GDPC1. In chained 2012 dollars (could this change?)

        Args:
            interval (EcoInterval): get real gdp for this interval
                QUARTER: quarterly data going back to first quarter 2002
                ANNUAL: annual data going back to 1929

        Returns:
            pd.DataFrame: columns as follows: year (str, YYYY) or qtr (str, YYYY-MM, quarter starts in this year-month),
                gdp (float64, in chained 2012 dollars),

        Raises:
            DataProviderException: DataProviderException if API request returns an error
        """
        param_dict = {
            "interval": interval,
            "datatype": DataType.CSV
        }
        response = self._base_request(Endpoints.REAL_GDP, param_dict)
        df = pd.read_csv(StringIO(response.text))
        if interval == EcoInterval.ANNUAL:
            df = df.rename(columns={"timestamp": "year", "value": "gdp"})
            df["year"] = df["year"].str[:4]
        else:  # interval == EcoInterval.QUARTER
            df = df.rename(columns={"timestamp": "qtr", "value": "gdp"})
            df["qtr"] = df["qtr"].str[:7]
        df["gdp"] = df["gdp"] * 1000000000

        return df

    def real_gdp_per_capita(self):
        """ quarterly Real GDP per capita data of the United States.

        U.S. Bureau of Economic Analysis, Real gross domestic product per capita. Retrieved from FRED.
        Possibly from here: https://fred.stlouisfed.org/series/A939RX0Q048SBEA In chained 2012 dollars
            (could this change?)

        Returns:
            pd.DataFrame: columns as follows: qtr (str, YYYY-MM, quarter starts in this year-month),
                gdp_per_capita (float64, in chained 2012 dollars),

        Raises:
            DataProviderException: DataProviderException if API request returns an error
        """
        param_dict = {
            "datatype": DataType.CSV
        }
        response = self._base_request(Endpoints.REAL_GDP_PER_CAPITA, param_dict)
        df = pd.read_csv(StringIO(response.text)).rename(columns={"timestamp": "qtr", "value": "gdp_per_capita"})
        df["qtr"] = df["qtr"].str[:7]

        return df

    def treasury_yield(self, maturity):
        """ Daily US treasury yield of a given maturity timeline (e.g., 5 year, 30 year, etc).

        Board of Governors of the Federal Reserve System (US), Market Yield on U.S. Treasury Securities, Constant
        Maturities, Quoted on an Investment Basis
        3-month: https://fred.stlouisfed.org/series/DGS3MO. history begins at 1981-09-01
        2-year: https://fred.stlouisfed.org/series/DGS2. history begins at 1976-06-01
        5-year: https://fred.stlouisfed.org/series/DGS5. history begins at 1962-01-02
        7-year: https://fred.stlouisfed.org/series/DGS7. history begins at 1969-07-01
        10-year: https://fred.stlouisfed.org/series/DGS10. history begins at 1962-01-02
        30-year: https://fred.stlouisfed.org/series/DGS30. history begins at 1977-02-15
        Weekly and monthly yields also available from API
        Holidays do not have a yield value

        Args:
            maturity (TreasuryMaturity): get treasury yield for this maturity

        Returns:
            pd.DataFrame: columns as follows: date (datetime.date), yield_pct (float64, percent),

        Raises:
            DataProviderException: DataProviderException if API request returns an error
        """
        param_dict = {
            "interval": TreasuryInterval.DAILY,
            "maturity": maturity,
            "datatype": DataType.CSV
        }
        response = self._base_request(Endpoints.TREASURY_YIELD, param_dict)
        df = pd.read_csv(StringIO(response.text)).rename(columns={"timestamp": "date", "value": "yield_pct"})
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df["yield_pct"] = df["yield_pct"].replace(".", np.nan).astype("float64")

        return df

    def fed_funds_rate(self):
        """ Daily federal funds rate (interest rate) of the United States

        Board of Governors of the Federal Reserve System (US), Federal Funds Effective Rate
        From FRED: https://fred.stlouisfed.org/series/FEDFUNDS
        Weekly and monthly yields also available from API

        Returns:
            pd.DataFrame: columns as follows: date (datetime.date), yield_pct (float64, percent),

        Raises:
            DataProviderException: DataProviderException if API request returns an error
        """
        param_dict = {
            "interval": TreasuryInterval.DAILY,
            "datatype": DataType.CSV
        }
        response = self._base_request(Endpoints.FEDERAL_FUNDS_RATE, param_dict)
        df = pd.read_csv(StringIO(response.text)).rename(columns={"timestamp": "date", "value": "yield_pct"})
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df["yield_pct"] = df["yield_pct"].astype("float64")

        return df

    def cpi(self, interval):
        """ Monthly or semiannual consumer price index (CPI) of the United States

        U.S. Bureau of Labor Statistics, Consumer Price Index for All Urban Consumers: All Items in U.S. City Average
        From FRED: https://fred.stlouisfed.org/series/CPIAUCSL
        CPI Units of measure: Index 1982-1984=100

        Args:
            interval (CPIInterval): get cpi over this interval
                MONTHLY: monthly data going back to 1913-01-01 (monthly since 1913)
                SEMIANNUAL: semiannual data going back to 1984-01-01 (semiannual since 1984)

        Returns:
            pd.DataFrame: columns as follows: month (str, YYYY-MM) or semiannual (str, YYYY-MM, semiannual starts in
                this year-month), cpi (float64)

        Raises:
            DataProviderException: DataProviderException if API request returns an error
        """
        param_dict = {
            "interval": interval,
            "datatype": DataType.CSV
        }
        response = self._base_request(Endpoints.CPI, param_dict)
        df = pd.read_csv(StringIO(response.text))
        df["timestamp"] = df["timestamp"].str[:7]
        if interval == CPIInterval.MONTHLY:
            df = df.rename(columns={"timestamp": "month", "value": "cpi"})
        else:
            df = df.rename(columns={"timestamp": "semiannual", "value": "cpi"})

        df["cpi"] = df["cpi"].astype("float64")

        return df

    def inflation(self):
        """ Annual inflation rates (consumer prices) of the United States

        World Bank, Inflation, consumer prices for the United States
        From FRED: https://fred.stlouisfed.org/series/FPCPITOTLZGUSA
        Yearly inflation starting from 1960.

        Returns:
            pd.DataFrame: columns as follows: year (str, YYYY), inflation_pct (float64, percent)

        Raises:
            DataProviderException: DataProviderException if API request returns an error
        """
        param_dict = {
            "datatype": DataType.CSV
        }
        response = self._base_request(Endpoints.INFLATION, param_dict)
        df = pd.read_csv(StringIO(response.text)).rename(columns={"timestamp": "year", "value": "inflation_pct"})
        df["year"] = df["year"].str[:4]
        df["inflation_pct"] = df["inflation_pct"].astype("float64")

        return df

    def retail_sales(self):
        """ Monthly Advance Retail Sales: Retail Trade data of the United States

        U.S. Census Bureau, Advance Retail Sales: Retail Trade
        From FRED: https://fred.stlouisfed.org/series/RSXFS
        Monthly starting from 1992-01

        Returns:
            pd.DataFrame: columns as follows: month (str, YYYY-MM), retail_sales (float64, dollars)

        Raises:
            DataProviderException: DataProviderException if API request returns an error
        """
        param_dict = {
            "datatype": DataType.CSV
        }
        response = self._base_request(Endpoints.RETAIL_SALES, param_dict)
        df = pd.read_csv(StringIO(response.text)).rename(columns={"timestamp": "month", "value": "retail_sales"})
        df["month"] = df["month"].str[:7]
        df["retail_sales"] = df["retail_sales"].astype("float64") * 1000000

        return df

    def durable_goods_orders(self):
        """ Monthly manufacturers' new orders of durable goods in the United States

        U.S. Census Bureau, Manufacturers' New Orders: Durable Goods
        From FRED: https://fred.stlouisfed.org/series/DGORDER
        Monthly starting from 1992-02

        Returns:
            pd.DataFrame: columns as follows: month (str, YYYY-MM), durable_orders (float64, dollars)

        Raises:
            DataProviderException: DataProviderException if API request returns an error
        """
        param_dict = {
            "datatype": DataType.CSV
        }
        response = self._base_request(Endpoints.DURABLES, param_dict)
        df = pd.read_csv(StringIO(response.text)).rename(columns={"timestamp": "month", "value": "durable_orders"})
        df["month"] = df["month"].str[:7]
        df["durable_orders"] = df["durable_orders"].astype("float64") * 1000000

        return df

    def unemployment_rate(self):
        """ Monthly unemployment data of the United States

        The unemployment rate represents the number of unemployed as a percentage of the labor force. Labor force data
        are restricted to people 16 years of age and older, who currently reside in 1 of the 50 states or the District
        of Columbia, who do not reside in institutions (e.g., penal and mental facilities, homes for the aged), and who
        are not on active duty in the Armed Forces
        U.S. Bureau of Labor Statistics, Unemployment Rate
        From FRED: https://fred.stlouisfed.org/series/UNRATE
        Monthly starting from 1948-01

        Returns:
            pd.DataFrame: columns as follows: month (str, YYYY-MM), unemployment_rate (float64, percent)

        Raises:
            DataProviderException: DataProviderException if API request returns an error
        """
        param_dict = {
            "datatype": DataType.CSV
        }
        response = self._base_request(Endpoints.UNEMPLOYMENT, param_dict)
        df = pd.read_csv(StringIO(response.text)).rename(columns={"timestamp": "month", "value": "unemployment_rate"})
        df["month"] = df["month"].str[:7]
        df["unemployment_rate"] = df["unemployment_rate"].astype("float64")

        return df

    def nonfarm_payroll(self):
        """ Monthly US All Employees: Total Nonfarm (commonly known as Total Nonfarm Payroll)

        A measure of the number of U.S. workers in the economy that excludes proprietors, private household employees,
        unpaid volunteers, farm employees, and the unincorporated self-employed.
        U.S. Bureau of Labor Statistics, All Employees, Total Nonfarm
        From FRED: https://fred.stlouisfed.org/series/PAYEMS
        Monthly starting from 1939-01

        Returns:
            pd.DataFrame: columns as follows: month (str, YYYY-MM), people (int64)

        Raises:
            DataProviderException: DataProviderException if API request returns an error
        """
        param_dict = {
            "datatype": DataType.CSV
        }
        response = self._base_request(Endpoints.NONFARM_PAYROLL, param_dict)
        df = pd.read_csv(StringIO(response.text)).rename(columns={"timestamp": "month", "value": "people"})
        df["month"] = df["month"].str[:7]
        df["people"] = df["people"].astype("int64") * 1000

        return df
