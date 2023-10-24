import datetime
from decimal import Decimal

from django.core.validators import ValidationError

from ...dataprovider.alphavantage import TickerSentimentLabel as AVTickerSentimentLabel, \
    TopicSentiment as AVTopicSentiment
from ...models.newssentiment import TopicSentiment, TickerSentimentLabel, TickerSentiment, NewsSentiment
from ..dataprovider.test_alphavantage import AlphaVantageTests
from .test_securitymaster import SecurityMasterTests
from util.djangomodeltestcasebase import DjangoModelTestCaseBase


class NewsSentimentTests(DjangoModelTestCaseBase):

    def equal(self, model1: NewsSentiment, model2: NewsSentiment):
        pass

    def test_topic_sentiment_relevance_score(self):
        ts = NewsSentimentTests.topic_sentiment_blockchain()

        with self.assertRaises(ValidationError):
            ts.relevance_score = Decimal(0)
            ts.clean_fields()

        with self.assertRaises(ValidationError):
            ts.relevance_score = Decimal("1.0001")
            ts.clean_fields()

    def test_topic_sentiment_alphavantage_topic_sentiment_constructor(self):
        nsts = TopicSentiment.objects.alphavantage_topic_sentiment_constructor(
            AlphaVantageTests.topic_sentiment_blockchain_obj())
        nsts_test = NewsSentimentTests.topic_sentiment_blockchain(create=False)
        self.simple_equal(nsts, nsts_test, TopicSentiment)

    def test_topic_sentiment_topic_from_alphavantage_topic_sentiment_topic(self):
        # test that all AV Topics match an NS Topic by value
        for topic in AVTopicSentiment.Topic:
            TopicSentiment.Topic(topic.value)

    def test_ticker_sentiment_label_from_alphavantage_ticker_sentiment_label(self):
        for ts in AVTickerSentimentLabel:
            TickerSentimentLabel(ts.value)

    def test_ticker_sentiment_label_validate_ticker_sentiment_score_and_label(self):
        with self.assertRaises(ValidationError):
            TickerSentimentLabel.validate_ticker_sentiment_score_and_label(TickerSentimentLabel.BEARISH, Decimal(0))

        self.assertIsNone(TickerSentimentLabel.validate_ticker_sentiment_score_and_label(
            TickerSentimentLabel.BEARISH, Decimal("-0.35")))

        self.assertIsNone(TickerSentimentLabel.validate_ticker_sentiment_score_and_label(
            TickerSentimentLabel.SOMEWHAT_BEARISH, Decimal("-0.15")))

        self.assertIsNone(TickerSentimentLabel.validate_ticker_sentiment_score_and_label(
            TickerSentimentLabel.NEUTRAL, Decimal("0.149")))

        self.assertIsNone(TickerSentimentLabel.validate_ticker_sentiment_score_and_label(
            TickerSentimentLabel.SOMEWHAT_BULLISH, Decimal("0.15")))

        self.assertIsNone(TickerSentimentLabel.validate_ticker_sentiment_score_and_label(
            TickerSentimentLabel.BULLISH, Decimal("0.35")))

    def test_ticker_sentiment_relevance_score(self):
        ts = NewsSentimentTests.ticker_sentiment_aapl()

        with self.assertRaises(ValidationError):
            ts.relevance_score = Decimal(0)
            ts.clean_fields()

        with self.assertRaises(ValidationError):
            ts.relevance_score = Decimal("1.0001")
            ts.clean_fields()

    def test_ticker_sentiment_alphavantage_ticker_sentiment_constructor(self):
        SecurityMasterTests.security_master_btc()

        # test ValidationError
        ts_btc = AlphaVantageTests.ticker_sentiment_btc_obj()
        with self.assertRaises(ValidationError):
            ts_btc.ticker_sentiment_score = Decimal("1")
            TickerSentiment.objects.alphavantage_ticker_sentiment_constructor(ts_btc)

        nsts = TickerSentiment.objects.alphavantage_ticker_sentiment_constructor(
            AlphaVantageTests.ticker_sentiment_btc_obj())
        nsts_test = NewsSentimentTests.ticker_sentiment_btc(create=False)
        self.simple_equal(nsts, nsts_test, TickerSentiment)

    def test_ticker_sentiment_save_clean(self):
        ts = NewsSentimentTests.ticker_sentiment_aapl()

        ts.ticker_sentiment_score = Decimal("-1")
        with self.assertRaises(ValidationError):
            ts.save()
        with self.assertRaises(ValidationError):
            ts.clean_fields()

    def test_news_sentiment_alphavantage_news_sentiment_constructor(self):
        SecurityMasterTests.security_master_btc()
        SecurityMasterTests.security_master_cad()
        av_ns = AlphaVantageTests.news_sentiment_1_obj()
        ns = NewsSentiment.objects.alphavantage_news_sentiment_constructor(av_ns)

        # check against av_ns. debugger stack overflow for an instantiated (but not saved) model with a manytomany field
        self.assertEqual(ns.authors, av_ns.authors)
        self.assertEqual(ns.category_within_source, av_ns.category_within_source)
        self.assertEqual(ns.overall_sentiment_label, TickerSentimentLabel(av_ns.overall_sentiment_label.value))
        self.assertEqual(ns.overall_sentiment_score, av_ns.overall_sentiment_score)
        self.assertEqual(ns.source, av_ns.source)
        self.assertEqual(ns.summary, av_ns.summary)
        self.assertEqual(ns.title, av_ns.title)
        self.assertEqual(ns.url, av_ns.url)
        topics = list(ns.topics.all())
        self.simple_equal(topics[0], NewsSentimentTests.topic_sentiment_blockchain(create=False), TopicSentiment)
        self.simple_equal(topics[1], NewsSentimentTests.topic_sentiment_finance(create=False), TopicSentiment)
        tickers = list(ns.ticker_sentiments.all())
        self.simple_equal(tickers[0], NewsSentimentTests.ticker_sentiment_btc(create=False), TickerSentiment)
        self.simple_equal(tickers[1], NewsSentimentTests.ticker_sentiment_cad(create=False), TickerSentiment)

    def test_news_sentiment_save_clean(self):
        ns = NewsSentimentTests.news_sentiment_1()
        self.assertTrue(ns.ticker_sentiments.filter(id=NewsSentimentTests.ticker_sentiment_aapl().pk).exists())

        ns.overall_sentiment_score = Decimal("1")
        with self.assertRaises(ValidationError):
            ns.save()
        with self.assertRaises(ValidationError):
            ns.clean_fields()

    @staticmethod
    def topic_sentiment_blockchain(create=True):
        ts = (TopicSentiment.objects.get_or_create if create else TopicSentiment)(
            topic=TopicSentiment.Topic.BLOCKCHAIN, relevance_score=Decimal("0.356367"))
        return ts[0] if create else ts

    @staticmethod
    def topic_sentiment_finance(create=True):
        ts = (TopicSentiment.objects.get_or_create if create else TopicSentiment)(
            topic=TopicSentiment.Topic.FINANCE, relevance_score=Decimal("1.0"))
        return ts[0] if create else ts

    @staticmethod
    def ticker_sentiment_aapl():
        return TickerSentiment.objects.get_or_create(
            security_master=SecurityMasterTests.security_master_aapl(), ticker="AAPL", relevance_score=Decimal("0.5"),
            ticker_sentiment_score=Decimal("1"), ticker_sentiment_label=TickerSentimentLabel.BULLISH)[0]

    @staticmethod
    def ticker_sentiment_msft():
        return TickerSentiment.objects.get_or_create(
            security_master=SecurityMasterTests.security_master_msft(), ticker="MSFT", relevance_score=Decimal("0.99"),
            ticker_sentiment_score=Decimal("-0.4"), ticker_sentiment_label=TickerSentimentLabel.BEARISH)[0]

    @staticmethod
    def ticker_sentiment_btc(create=True):
        ts = (TickerSentiment.objects.get_or_create if create else TickerSentiment)(
            security_master=SecurityMasterTests.security_master_btc(), ticker="BTC",relevance_score=Decimal("0.694639"),
            ticker_sentiment_score=Decimal("-0.498463"), ticker_sentiment_label=TickerSentimentLabel.BEARISH)
        return ts[0] if create else ts

    @staticmethod
    def ticker_sentiment_cad(create=True):
        ts = (TickerSentiment.objects.get_or_create if create else TickerSentiment)(
            security_master=SecurityMasterTests.security_master_cad(), ticker="CAD", relevance_score=Decimal("1.0"),
            ticker_sentiment_score=Decimal("1"),  ticker_sentiment_label=TickerSentimentLabel.BULLISH)
        return ts[0] if create else ts

    @staticmethod
    def news_sentiment_1():
        ns = NewsSentiment.objects.get_or_create(
            title="test title", url="https://www.testnewssentiment.com/",
            time_published=datetime.datetime(2022, 10, 1, 15, 58, 37), authors="test author1;test author2",
            summary="test summary", source="Test Source", category_within_source="Technology",
            overall_sentiment_score=Decimal("-0.4"), overall_sentiment_label=TickerSentimentLabel.BEARISH)[0]
        ns.topics.add(NewsSentimentTests.topic_sentiment_blockchain(), NewsSentimentTests.topic_sentiment_finance())
        ns.ticker_sentiments.add(NewsSentimentTests.ticker_sentiment_aapl(),
                                 NewsSentimentTests.ticker_sentiment_msft())
        return ns
