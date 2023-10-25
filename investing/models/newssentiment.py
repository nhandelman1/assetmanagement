from decimal import Decimal
import datetime

from django.core.validators import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy

from .securitymaster import SecurityMaster
from ..dataprovider.alphavantage import NewsSentiment as AVNewsSentiment, TickerSentiment as AVTickerSentiment, \
    TopicSentiment as AVTopicSentiment


def validate_relevance_score_0_1(relevance_score):
    if relevance_score <= Decimal(0) or relevance_score > Decimal(1):
        raise ValidationError("relevance_score " + str(relevance_score) +
                              " is invalid. Must be between 0 (exclusive) and 1 (inclusive)")


class TopicSentimentDataManager(models.Manager):

    def alphavantage_topic_sentiment_constructor(self, av_topic):
        """ Create a new TopicSentiment object from an AlphaVantage TopicSentiment object

        Args:
            av_topic (AVTopicSentiment):

        Returns:
            TopicSentiment: created object

        Raises:
            KeyError: if topic does not match a label in TopicSentiment.Topic
        """
        return self.get_or_create(
            topic=TopicSentiment.Topic(av_topic.topic.value), relevance_score=av_topic.relevance_score)[0]


class TopicSentiment(models.Model):
    """ Topic Sentiment Model

    Attributes:
            topic (str): topic on which the article is about
            relevance_score (Decimal): a score of how relevant the article is to the topic, "0 < x <= 1, with a higher
                score indicating higher relevance.
    """
    class Topic(models.TextChoices):
        BLOCKCHAIN = "blockchain", gettext_lazy("Blockchain")
        EARNINGS = "earnings", gettext_lazy("Earnings")
        ECONOMY_FISCAL = "economy_fiscal", gettext_lazy("Economy - Fiscal")
        ECONOMY_MACRO = "economy_macro", gettext_lazy("Economy - Macro")
        ECONOMY_MONETARY = "economy_monetary", gettext_lazy("Economy - Monetary")
        ENERGY_TRANSPORTATION = "energy_transportation", gettext_lazy("Energy & Transportation")
        FINANCE = "finance", gettext_lazy("Finance")
        FINANCIAL_MARKETS = "financial_markets", gettext_lazy("Financial Markets")
        IPO = "ipo", gettext_lazy("IPO")
        LIFE_SCIENCES = "life_sciences", gettext_lazy("Life Sciences")
        MANUFACTURING = "manufacturing", gettext_lazy("Manufacturing")
        MERGERS_ACQUISITIONS = "mergers_and_acquisitions", gettext_lazy("Mergers & Acquisitions")
        REAL_ESTATE_CONSTRUCTION = "real_estate", gettext_lazy("Real Estate & Construction")
        RETAIL_WHOLESALE = "retail_wholesale", gettext_lazy("Retail & Wholesale")
        TECHNOLOGY = "technology", gettext_lazy("Technology")

    topic = models.CharField(max_length=30, choices=Topic.choices)
    relevance_score = models.DecimalField(max_digits=7, decimal_places=6, validators=[validate_relevance_score_0_1])

    objects = TopicSentimentDataManager()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        """ __str__ override

        Format:
            self.topic, str(self.relevance_score)

        Returns:
            str: as described by Format
        """
        return self.topic + ", " + str(self.relevance_score)


class TickerSentimentLabel(models.TextChoices):
    """ Label for ticker sentiment
    Sentiment labels: Bearish, Somewhat-Bearish, Neutral, Somewhat-Bullish, Bullish
    ticker sentiment score and label: x <= -0.35: Bearish; -0.35 < x <= -0.15: Somewhat-Bearish;
        -0.15 < x < 0.15: Neutral; 0.15 <= x < 0.35: Somewhat_Bullish; x >= 0.35: Bullish
    """
    BEARISH = "Bearish", gettext_lazy("Bearish")
    SOMEWHAT_BEARISH = "Somewhat-Bearish", gettext_lazy("Somewhat-Bearish")
    NEUTRAL = "Neutral", gettext_lazy("Neutral")
    SOMEWHAT_BULLISH = "Somewhat-Bullish", gettext_lazy("Somewhat-Bullish")
    BULLISH = "Bullish", gettext_lazy("Bullish")

    @staticmethod
    def validate_ticker_sentiment_score_and_label(ticker_sentiment_label, ticker_sentiment_score):
        """ Check that score is in the correct range for the label

        Args:
            ticker_sentiment_label (TickerSentimentLabel):
            ticker_sentiment_score (Decimal):

        Raises:
            ValidationError: if score is not the correct range for the label
        """
        msg = None
        if ticker_sentiment_label == TickerSentimentLabel.BEARISH:
            if Decimal("-0.35") < ticker_sentiment_score:
                msg = " must have ticker sentiment score less than or equal to -0.35"
        elif ticker_sentiment_label == TickerSentimentLabel.SOMEWHAT_BEARISH:
            if not Decimal("-0.35") < ticker_sentiment_score <= Decimal("-0.15"):
                msg = " must have ticker sentiment score greater than -0.35 but less than or equal to -0.15"
        elif ticker_sentiment_label == TickerSentimentLabel.NEUTRAL:
            if not Decimal("-0.15") < ticker_sentiment_score < Decimal("0.15"):
                msg = " must have ticker sentiment score greater than -0.15 but less than 0.15"
        elif ticker_sentiment_label == TickerSentimentLabel.SOMEWHAT_BULLISH:
            if not Decimal("0.15") <= ticker_sentiment_score < Decimal("0.35"):
                msg = " must have ticker sentiment score greater than or equal to 0.15 but less than 0.35"
        elif ticker_sentiment_label == TickerSentimentLabel.BULLISH:
            if not Decimal("0.35") <= ticker_sentiment_score:
                msg = " must have ticker sentiment score greater than or equal to 0.35"
        else:
            msg = " is not set in TickerSentimentLabel.validate_ticker_sentiment_score_and_label()"

        if msg is not None:
            raise ValidationError(ticker_sentiment_label + msg)


class TickerSentimentDataManager(models.Manager):

    def alphavantage_ticker_sentiment_constructor(self, av_ts):
        """ Create a new TickerSentiment object from an AlphaVantage TickerSentiment object

        Args:
            av_ts (AVTickerSentiment):

        Returns:
            TickerSentiment: created object

        Raises:
            Union[KeyError, ValidationError]:
                KeyError if ticker_sentiment_label does not match a label in TickerSentimentLabel
                ValidationError if ticker_sentiment_score is not in the correct range for the ticker_sentiment_label
        """
        return self.get_or_create(
            security_master=SecurityMaster.objects.get_or_create_default(ticker=av_ts.ticker), ticker=av_ts.ticker,
            relevance_score=av_ts.relevance_score, ticker_sentiment_score=av_ts.ticker_sentiment_score,
            ticker_sentiment_label=TickerSentimentLabel(av_ts.ticker_sentiment_label.value))[0]


class TickerSentiment(models.Model):
    """ Ticker Sentiment Model

    Attributes:
        security_master (SecurityMaster): permanent id for security on which the article is about
        ticker (str): ticker on which the article is about. might not match ticker in security_master
        relevance_score (Decimal): a score of how relevant the article is to the ticker
            "0 < x <= 1, with a higher score indicating higher relevance.
        ticker_sentiment_score (Decimal): score of the sentiment the article implies for the ticker
        ticker_sentiment_label (TickerSentimentLabel): label of the sentiment the article implies for the ticker
    """
    security_master = models.ForeignKey(SecurityMaster, models.PROTECT)
    ticker = models.CharField(max_length=20)
    relevance_score = models.DecimalField(max_digits=7, decimal_places=6, validators=[validate_relevance_score_0_1])
    ticker_sentiment_score = models.DecimalField(max_digits=7, decimal_places=6)
    ticker_sentiment_label = models.CharField(max_length=20, choices=TickerSentimentLabel.choices)

    objects = TickerSentimentDataManager()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        """ __str__ override

        Format:
            Ticker: self.ticker, str(self.relevance_score),
                str(self.ticker_sentiment_score) -> self.ticker_sentiment_label

        Returns:
            str: as described by Format
        """
        return self.ticker + ", " + str(self.relevance_score) + ", " + str(self.ticker_sentiment_score) + " -> " + \
            self.ticker_sentiment_label

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        TickerSentimentLabel.validate_ticker_sentiment_score_and_label(
            TickerSentimentLabel(self.ticker_sentiment_label), self.ticker_sentiment_score)

    def save(self, *args, **kwargs):
        TickerSentimentLabel.validate_ticker_sentiment_score_and_label(
            TickerSentimentLabel(self.ticker_sentiment_label), self.ticker_sentiment_score)
        return super().save(*args, **kwargs)


class NewsSentimentDataManager(models.Manager):

    def alphavantage_news_sentiment_constructor(self, av_ns):
        """ Create a new NewsSentiment object from an AlphaVantage NewsSentiment object

        Args:
            av_ns (AVNewsSentiment):

        Returns:
            NewsSentiment: created object

        Raises:
            Union[KeyError, ValidationError]:
                KeyError if overall_sentiment_label does not match a label in TickerSentimentLabel or if either
                    TickerSentiment.alphavantage_ticker_sentiment_constructor() or
                    TopicSentiment.alphavantage_topic_sentiment_constructor() raises a KeyError
                ValidationError if overall_sentiment_score is not in the correct range for the overall_sentiment_label
                    or if TickerSentiment.alphavantage_ticker_sentiment_constructor() raises a ValidationError
        """
        ns = self.get_or_create(
            title=av_ns.title, url=av_ns.url, time_published=av_ns.time_published, authors=av_ns.authors,
            summary=av_ns.summary, source=av_ns.source, category_within_source=av_ns.category_within_source,
            overall_sentiment_score=av_ns.overall_sentiment_score,
            overall_sentiment_label=TickerSentimentLabel(av_ns.overall_sentiment_label.value))[0]
        ns.topics.set([TopicSentiment.objects.alphavantage_topic_sentiment_constructor(t) for t in av_ns.topics])
        ns.ticker_sentiments.set(
            [TickerSentiment.objects.alphavantage_ticker_sentiment_constructor(t) for t in av_ns.ticker_sentiments])
        return ns


class NewsSentiment(models.Model):
    """ Market news & sentiment data

    This class is designed based on the data returned by AlphaVantage Market News & Sentiment endpoint. This class and
    documentation may need to change if other sources are used.

    Attributes:
        title (str): article title
        url (str): article url
        time_published (datetime.datetime):
        authors (str): article authors
        summary (str): article summary
        source (str): article source
        category_within_source (str): the category that the source puts the article into
        topics (models.ManyToManyField[TopicSentiment]):
        overall_sentiment_score (Decimal):
        overall_sentiment_label (TickerSentimentLabel):
        ticker_sentiments (models.ManyToManyField[TickerSentiment]):
    """
    title = models.CharField(max_length=200)
    url = models.URLField()
    time_published = models.DateTimeField()
    authors = models.CharField(max_length=200)
    summary = models.TextField(max_length=200)
    source = models.CharField(max_length=50)
    category_within_source = models.CharField(max_length=50)
    topics = models.ManyToManyField(TopicSentiment)
    overall_sentiment_score = models.DecimalField(max_digits=7, decimal_places=6)
    overall_sentiment_label = models.CharField(max_length=20, choices=TickerSentimentLabel.choices)
    ticker_sentiments = models.ManyToManyField(TickerSentiment)

    objects = NewsSentimentDataManager()

    def __repr__(self):
        """ __repr__ override

        Format:
            Title: self.title
            URL: self.url
            Source: self.source, Category Within Source: self.category_within_source
            Time Published: str(self.time_published)
            Authors: str(self.authors)
            Summary: self.summary
            Overall Sentiment Score -> Label: str(self.overall_sentiment_score) -> self.overall_sentiment_label
            [For each topic in self.topics]
            str(topic)
            [For each ts in self.ticker_sentiment]
            str(ts)

        Returns:
            str: as described by Format
        """
        ret_str = "Title: " + self.title + \
            "\nURL: " + self.url + \
            "\nSource: " + self.source + ", Category Within Source: " + self.category_within_source + \
            "\nTime Published: " + str(self.time_published) + \
            "\nAuthors: " + str(self.authors) + \
            "\nSummary: " + self.summary + \
            "\nOverall Sentiment Score -> Label: " + str(self.overall_sentiment_score) + " -> " + \
                str(self.overall_sentiment_label)
        for topic in list(self.topics):
            ret_str += "\n" + str(topic)
        for ts in list(self.ticker_sentiments):
            ret_str += "\n" + str(ts)

        return ret_str

    def __str__(self):
        return self.title + ", " + str(self.time_published)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        TickerSentimentLabel.validate_ticker_sentiment_score_and_label(
            TickerSentimentLabel(self.overall_sentiment_label), self.overall_sentiment_score)

    def save(self, *args, **kwargs):
        TickerSentimentLabel.validate_ticker_sentiment_score_and_label(
            TickerSentimentLabel(self.overall_sentiment_label), self.overall_sentiment_score)
        return super().save(*args, **kwargs)
