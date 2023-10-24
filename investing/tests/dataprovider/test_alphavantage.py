from decimal import Decimal
from unittest import skip
from unittest.mock import patch
import datetime
import requests

from ...dataprovider.alphavantage import AlphaVantage, Endpoints, NewsSentiment, TickerSentiment, TickerSentimentLabel,\
    TopicSentiment
from ...dataprovider.dataproviderexception import DataProviderException
from util.testcasebase import TestCaseBase


# TODO finish API tests
class AlphaVantageTests(TestCaseBase):
    """ Test AlphaVantage API and data structures

    Tests that use the AlphaVantage API are skipped by default since AlphaVantage has a API request limit.
    """
    def equal(self, obj1: object, obj2: object):
        pass

    def test_topic_sentiment_from_label(self):
        with self.assertRaises(ValueError):
            TopicSentiment.Topic.from_label("asdf")

        self.assertEqual(TopicSentiment.Topic.from_label("Blockchain"), TopicSentiment.Topic.BLOCKCHAIN)

    def test_topic_sentiment_json_dict_constructor(self):
        with self.assertRaises(ValueError):
            TopicSentiment.json_dict_constructor({"topic": "asdf", "relevance_score": 0.356367})

        ts = TopicSentiment.json_dict_constructor(AlphaVantageTests.topic_sentiment_blockchain_dict())
        ts_test = AlphaVantageTests.topic_sentiment_blockchain_obj()
        self.simple_equal(ts, ts_test, TopicSentiment)

        ts = TopicSentiment.json_dict_constructor(AlphaVantageTests.topic_sentiment_finance_dict())
        ts_test = AlphaVantageTests.topic_sentiment_finance_obj()
        self.simple_equal(ts, ts_test, TopicSentiment)

    def test_ticker_sentiment_label_from_label(self):
        with self.assertRaises(ValueError):
            TickerSentimentLabel.from_label("asdf")

        self.assertEqual(TickerSentimentLabel.from_label("Somewhat-Bullish"), TickerSentimentLabel.SOMEWHAT_BULLISH)

    def test_ticker_sentiment_json_dict_constructor(self):
        with self.assertRaises(ValueError):
            TickerSentiment.json_dict_constructor({"ticker": "AAPL", "relevance_score": 0.694639,
                                                   "ticker_sentiment_score": -0.4, "ticker_sentiment_label": "asdf"})

        # test ticker conversion from "CRYPTO:BTC" to "BTC" and other attributes
        ts1 = TickerSentiment.json_dict_constructor(AlphaVantageTests.ticker_sentiment_btc_dict())
        ts1_test = AlphaVantageTests.ticker_sentiment_btc_obj()
        self.simple_equal(ts1, ts1_test, TickerSentiment)

        ts1 = TickerSentiment.json_dict_constructor(AlphaVantageTests.ticker_sentiment_cad_dict())
        ts1_test = AlphaVantageTests.ticker_sentiment_cad_obj()
        self.simple_equal(ts1, ts1_test, TickerSentiment)

    def test_news_sentiment_json_dict_constructor(self):
        # test invalid Topic
        ns_dict = AlphaVantageTests.news_sentiment_1_dict()
        ns_dict["topics"][0]["topic"] = "asdf"
        with self.assertRaises(ValueError):
            NewsSentiment.json_dict_constructor(ns_dict)

        # test invalid TickerSentimentLabel
        ns_dict = AlphaVantageTests.news_sentiment_1_dict()
        ns_dict["ticker_sentiment"][0]["ticker_sentiment_label"] = "asdf"
        with self.assertRaises(ValueError):
            NewsSentiment.json_dict_constructor(ns_dict)

        ns = NewsSentiment.json_dict_constructor(AlphaVantageTests.news_sentiment_1_dict())
        ns_test = AlphaVantageTests.news_sentiment_1_obj()
        for topic, topic_test in zip(ns.topics, ns_test.topics):
            self.simple_equal(topic, topic_test, TopicSentiment)
        for ts, ts_test in zip(ns.ticker_sentiments, ns_test.ticker_sentiments):
            self.simple_equal(ts, ts_test, TickerSentiment)
        self.simple_equal(ns, ns_test, NewsSentiment, rem_attr_list=["topics", "ticker_sentiments"])

    def test_base_create_url(self):
        """
        Test param_dict values get converted appropriately according to docstring
        """
        param_dict = {
            "1": None, "2": TickerSentimentLabel.BULLISH, "3": True, "4": datetime.datetime(2020, 1, 2, 3, 4),
            "5": datetime.date(2021, 9, 8), "6": 0.567, "7": "test", "8": [],
            "9": [TickerSentimentLabel.SOMEWHAT_BULLISH, TickerSentimentLabel.BEARISH], "10": (True, False),
            "11": [datetime.datetime(2022, 5, 6, 7, 8), datetime.datetime(2023, 10, 11, 12, 13)],
            "12": (datetime.date(2024, 12, 12), datetime.date(2025, 1, 1)), "13": [0.0084, 1], "14": ["asdf", "1.067"]}

        param_str = "&2=Bullish&3=true&4=20200102T0304&5=2021-09-08&6=0.567&7=test&9=Somewhat-Bullish,Bearish" \
                    "&10=true,false&11=20220506T0708,20231011T1213&12=2024-12-12,2025-01-01&13=0.0084,1&14=asdf,1.067"

        av = AlphaVantage()
        url = av._base_create_url(Endpoints.CPI, param_dict)
        url_test = AlphaVantage._URL_BASE + "function=" + Endpoints.CPI.value + param_str + "&apikey=" + av.api_key
        self.assertEqual(url, url_test)

    @patch("requests.get")
    def test_base_request(self, mock_requests_get):
        with self.subTest():
            # test status code 200 exception
            mock_response = requests.Response()
            mock_response.status_code = 300
            mock_response.reason = "test 300"
            mock_requests_get.return_value = mock_response
            with self.assertRaises(DataProviderException):
                AlphaVantage()._base_request(Endpoints.TIME_SERIES_INTRADAY, {})

        with self.subTest():
            # test "Error Message" in response content
            mock_response = requests.Response()
            mock_response.url = "https://test.test.test/"
            mock_response.status_code = 200
            mock_response._content = str.encode('{"Error Message":"test error"}')
            mock_requests_get.return_value = mock_response
            with self.assertRaises(DataProviderException):
                AlphaVantage()._base_request(Endpoints.TIME_SERIES_INTRADAY, {})

        with self.subTest():
            # test "Information" in response content
            mock_response._content = str.encode('{"Information":"test information"}')
            with self.assertRaises(DataProviderException):
                AlphaVantage()._base_request(Endpoints.TIME_SERIES_INTRADAY, {})

        with self.subTest():
            # test response content is not JSON format. this can happen if response content is a CSV
            # expectation is that the response is returned without issue
            mock_response._content = str.encode('asdf')
            AlphaVantage()._base_request(Endpoints.TIME_SERIES_INTRADAY, {})

    @skip
    def test_alphavantage_intraday(self):
        pass

    @skip
    def test_alphavantage_daily(self):
        pass

    @skip
    def test_alphavantage_top_gain_lose_active(self):
        pass

    @skip
    def test_alphavantage_company_overview(self):
        pass

    @skip
    def test_alphavantage_income_statement(self):
        pass

    @skip
    def test_alphavantage_balance_sheet(self):
        pass

    @skip
    def test_alphavantage_cash_flow_statement(self):
        pass

    @skip
    def test_alphavantage_earnings(self):
        pass

    @skip
    def test_alphavantage_listing_status(self):
        pass

    @skip
    def test_alphavantage_earnings_calendar(self):
        pass

    @skip
    def test_alphavantage_ipo_calendar(self):
        pass

    @skip
    def test_alphavantage_real_gdp(self):
        pass

    @skip
    def test_alphavantage_real_gdp_per_capita(self):
        pass

    @skip
    def test_alphavantage_treasury_yield(self):
        pass

    @skip
    def test_alphavantage_fed_funds_rate(self):
        pass

    @skip
    def test_alphavantage_cpi(self):
        pass

    @skip
    def test_alphavantage_inflation(self):
        pass

    @skip
    def test_alphavantage_retail_sales(self):
        pass
    @skip
    def test_alphavantage_durable_goods_orders(self):
        pass

    @skip
    def test_alphavantage_unemployment_rate(self):
        pass

    @skip
    def test_alphavantage_nonfarm_payroll(self):
        pass

    @skip("API request limit")
    def test_alphavantage_newssentiment(self):
        av = AlphaVantage()

        with self.assertRaises(DataProviderException):
            av.news_and_sentiment(stock_ticker="fake ticker")

        ns_list = av.news_and_sentiment(
            stock_ticker="MSTR", crypto_ticker="BTC", forex_ticker="USD", topics_list=[TopicSentiment.Topic.TECHNOLOGY],
            start_dt=datetime.datetime(2020, 5, 6, 16, 50, 55), end_dt=datetime.datetime(2023, 1, 7, 4, 48, 2))
        self.assertGreaterEqual(len(ns_list), 1)
        self.assertIsInstance(ns_list[0].overall_sentiment_label, TickerSentimentLabel)
        self.assertIsInstance(ns_list[0].overall_sentiment_score, Decimal)
        self.assertGreaterEqual(len(ns_list[0].topics), 1)
        self.assertIsInstance(ns_list[0].topics[0], TopicSentiment)
        self.assertGreaterEqual(len(ns_list[0].ticker_sentiments), 1)
        self.assertIsInstance(ns_list[0].ticker_sentiments[0], TickerSentiment)
        self.assertIsInstance(ns_list[0].time_published, datetime.datetime)

    @staticmethod
    def topic_sentiment_blockchain_dict():
        return {"topic": "Blockchain", "relevance_score": 0.356367}

    @staticmethod
    def topic_sentiment_blockchain_obj():
        return TopicSentiment(TopicSentiment.Topic.BLOCKCHAIN, Decimal("0.356367"))

    @staticmethod
    def topic_sentiment_finance_dict():
        return {"topic": "Finance", "relevance_score": "1.0"}

    @staticmethod
    def topic_sentiment_finance_obj():
        return TopicSentiment(TopicSentiment.Topic.FINANCE, Decimal("1.0"))

    @staticmethod
    def ticker_sentiment_btc_dict():
        return {"ticker": "CRYPTO:BTC", "relevance_score": 0.694639, "ticker_sentiment_score": -0.498463,
                "ticker_sentiment_label": "Bearish"}

    @staticmethod
    def ticker_sentiment_btc_obj():
        return TickerSentiment("BTC", Decimal("0.694639"), Decimal("-0.498463"), TickerSentimentLabel.BEARISH)

    @staticmethod
    def ticker_sentiment_cad_dict():
        return {"ticker": "FOREX:CAD", "relevance_score": "1.0", "ticker_sentiment_score": "1",
                "ticker_sentiment_label": "Bullish"}

    @staticmethod
    def ticker_sentiment_cad_obj():
        return TickerSentiment("CAD", Decimal("1.0"), Decimal("1"), TickerSentimentLabel.BULLISH)

    @staticmethod
    def news_sentiment_1_dict():
        return {"title": "test title", "url": "https://test.test.test/", "time_published": "20231001T015809",
                "authors": ["test author1", "test author2"], "summary": "test summary", "source": "test source",
                "category_within_source": "test category within source",
                "topics": [AlphaVantageTests.topic_sentiment_blockchain_dict(),
                           AlphaVantageTests.topic_sentiment_finance_dict()],
                "overall_sentiment_score": 0.178957, "overall_sentiment_label": "Somewhat-Bullish",
                "ticker_sentiment": [AlphaVantageTests.ticker_sentiment_btc_dict(),
                                     AlphaVantageTests.ticker_sentiment_cad_dict()]}

    @staticmethod
    def news_sentiment_1_obj():
        return NewsSentiment(
            "test title", "https://test.test.test/", datetime.datetime(2023, 10, 1, 1, 58, 9),
            "test author1;test author2", "test summary", "test source", "test category within source",
            [AlphaVantageTests.topic_sentiment_blockchain_obj(), AlphaVantageTests.topic_sentiment_finance_obj()],
            Decimal("0.178957"), TickerSentimentLabel.SOMEWHAT_BULLISH,
            [AlphaVantageTests.ticker_sentiment_btc_obj(), AlphaVantageTests.ticker_sentiment_cad_obj()])
