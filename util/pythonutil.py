from collections import defaultdict
from typing import Optional, Union
import datetime
import textwrap

import numpy as np


def textwrap_lines(line_str, width=150, indent="  "):
    """ Wrap str to target width with specified indentation while preserving line breaks

    Args:
        line_str (str): str with line breaks that caller wishes to preserve
        width (int): target max width of each line. long words are not broken so line(s) may have width greater than
            this value. Default 150
        indent (str): prepend every line with this str. Default "  "

    Returns:
        str: line_str with line breaks preserved, indentation applied and width target per line approximated
    """
    return '\n'.join(['\n'.join(textwrap.wrap(line, width=width, break_long_words=False, replace_whitespace=False,
                                              initial_indent=indent, subsequent_indent=indent))
                      for line in line_str.splitlines() if line.strip() != ''])


def nyse_holidays(years_dates, output_type="dd"):
    """ Get list of nyse holidays based on years which can be passed as 4 digit year or date

    only set up for 2018 - 2024 inclusive. years outside this range are considered to have no holidays

    Args:
        years_dates (Union[int, datetime.date, list[int], list[datetime.date], tuple[datetime.date, datetime.date]]):
            int can either be a 4 digit year int or 8 digit YYYYMMDD date int. 2-tuple for all years in between
            (inclusive) the two elements in the tuple
        output_type (str): return holidays as datetime.date ("dd") or 8 digit YYYYMMDD int ("int"). Default "dd"

    Returns:
        list[datetime.date]: list of holidays for the given years

    Raises:
        ValueError: if years_dates is a tuple that doesn't have length 2
    """
    if isinstance(years_dates, (int, datetime.date)):
        years_dates = [years_dates]

    def get_func(test_val):
        if isinstance(test_val, datetime.date):
            return lambda x: x.year
        elif len(str(test_val)) == 4:  # 4 digit year int
            return lambda x: x
        else:  # 8 digit date int
            return lambda x: x // 10000

    if isinstance(years_dates, tuple):
        if len(years_dates) != 2:
            raise ValueError("years_dates tuple must have length 2")
        func = get_func(years_dates[0])
        years_dates = list(range(func(years_dates[0]), func(years_dates[1]) + 1))

    func = get_func(years_dates[0])
    year_set = set()
    for yd in years_dates:
        year_set.add(func(yd))

    d = defaultdict(lambda: [],
        {2018: [20180101, 20180115, 20180219, 20180330, 20180528, 20180704, 20180903, 20181122, 20181225],
         2019: [20190101, 20190121, 20190218, 20190419, 20190527, 20190704, 20190902, 20191128, 20191225],
         2020: [20200101, 20200120, 20200217, 20200410, 20200525, 20200703, 20200907, 20201126, 20201225],
         2021: [20210101, 20210118, 20210215, 20210402, 20210531, 20210705, 20210906, 20211125, 20211224],
         2022: [20220117, 20220221, 20220415, 20220530, 20220620, 20220704, 20220905, 20221124, 20221226],
         2023: [20230102, 20230116, 20230220, 20230407, 20230529, 20230619, 20230704, 20230904, 20231123, 20231225],
         2024: [20240101, 20240115, 20240219, 20240329, 20240527, 20240619, 20240704, 20240902, 20241128, 20241225]})

    holiday_list = []
    for y in year_set:
        holiday_list += d[y]

    return holiday_list if output_type == "int" else \
        [datetime.date(d // 10000, month=(d % 10000 // 100), day=(d % 100)) for d in holiday_list]


def nearest_biz_day(date, past=True):
    """ Return nearest business day.

    past == True: If Saturday or Sunday, return Friday. Otherwise, return date.
    past == False: If Saturday, return Friday. If Sunday, return Monday. Otherwise, return date.

    Args:
        date (datetime.date):
        past (boolean): Default True

    Returns:
        datetime.date: Nearest business day.
    """
    if datetime.date.weekday(date) == 5:
        return date - datetime.timedelta(days=1)
    if datetime.date.weekday(date) == 6:
        return date + datetime.timedelta(days=(-2 if past else 1))
    return date


def change_dt_date(date, days=0, months=None, years=None, biz_days=0, biz_months=None, biz_years=None, holidays=None,
                   days_in_year=365, days_in_biz_year=260):
    """ Change datetime.date instance by specified values.

    This function is day based, so year and month may not work as expected. Every year has the same number of days
    and every month has the same number of days. This applies to business years and months also.

    Negative values move date backwards.

    days, months and years are applied first. biz_days, biz_months, biz_years are applied next.

    Weekend dates are moved to the previous Friday if business days, months or years are applied.

    Args:
        date (datetime.date):
        days (int): Default 0.
        months (Optional[int, float]): A month is days_in_year/12. round() to nearest day. Default None.
        years (Optional[int, float]): round() to nearest day. Can specify number of days in year with days_in_year.
            Default None.
        biz_days (int): Default 0.
        biz_months (Optional[int, float]): business month is 260/12 business days.
            round() to nearest business day. Default None.
        biz_years (Optional[int, float]): round() to nearest business day. Can specify number of biz days in biz year
            with days_in_biz_year. Default None.
        holidays (Optional[boolean]): only implemented for nyse holidays (keep non US holidays in mind). True to skip over
            holidays. None or False to include holidays. Default None
        days_in_year (int): Default 365.
        days_in_biz_year (int): Default 260.

    Returns:
        datetime.date: date changed according to parameters
    """
    def hol_count(sd, ed):
        if sd <= ed:
            return len([x for x in nyse_holidays((sd, ed)) if sd < x <= ed])
        else:
            return -len([x for x in nyse_holidays((ed, sd)) if ed <= x < sd])

    # change by calendar days
    start_date = date

    if not isinstance(days_in_year, int):
        days_in_year = 365
    if not isinstance(days_in_biz_year, int):
        days_in_biz_year = 260

    if not isinstance(days, int):
        days = 0
    if isinstance(months, (int, float)):
        days += round(days_in_year/12 * months)
    if isinstance(years, (int, float)):
        days += round(days_in_year * years)

    date += datetime.timedelta(days=days)

    if holidays:
        # there could be holidays between date and date + count but need to avoid infinite loop
        day_chng = hol_count(start_date, date)
        if day_chng != 0:
            date = change_dt_date(date, days=day_chng, holidays=True)

    # change by business days
    start_date = date

    if not isinstance(biz_days, int):
        biz_days = 0
    if isinstance(biz_months, (int, float)):
        biz_days += round(days_in_biz_year/12 * biz_months)
    if isinstance(biz_years, (int, float)):
        biz_days += round(days_in_biz_year * biz_years)

    if biz_days != 0:
        # move weekend date to previous friday
        date = nearest_biz_day(date)
        (skip_day, skip_len, inc) = (4, 3, 1) if biz_days >= 0 else (0, -3, -1)

        for i in range(abs(biz_days)):
            if datetime.date.weekday(date) == skip_day:
                date += datetime.timedelta(days=skip_len)
            else:
                date += datetime.timedelta(days=inc)

        if holidays:
            # there could be holidays between date and date + count but need to avoid infinite loop
            day_chng = hol_count(start_date, date)
            if day_chng != 0:
                date = change_dt_date(date, biz_days=day_chng, holidays=True)

    return date


def change_dt(dt, days=0, months=None, years=None, biz_days=0, biz_months=None, biz_years=None, hours=0, minutes=0,
              seconds=0, holidays=None, days_in_year=365, days_in_biz_year=260):
    """ Change datetime.datetime instance by specified values.

    Days, months, years (both biz and not biz) applied using change_dt_date(). See function docstring

    Args:
        dt (datetime.datetime):
        hours (int): Default 0.
        minutes  (int): Default 0.
        seconds  (int): Default 0.

    Returns:
        datetime.datetime: dt changed according to parameters
    """
    if days != 0 or biz_days != 0 or any(x is not None for x in [months, years, biz_months, biz_years]):
        time = dt.time()
        date = change_dt_date(dt.date(), days=days, months=months, years=years, biz_days=biz_days,
                              biz_months=biz_months, biz_years=biz_years, holidays=holidays, days_in_year=days_in_year,
                              days_in_biz_year=days_in_biz_year)
        dt = datetime.datetime.combine(date, time)

    dt = dt + datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

    return dt


def month_str_to_int(month):
    """ Convert month string to int.

    Args:
        month (str): "1"-"12", "01"-"12", "first 3 letters", "full month name". case insensitive

    Returns:
        int: value of month (1-12)

    Raises:
        Union[TypeError, ValueError]: TypeError if month is not a str. ValueError if month is not a supported value in
            a valid format
    """
    if not isinstance(month, str):
        raise TypeError("month is not a str type")

    month = month.lower()

    if month in ("1", "01", "jan", "january"):
        month_int = 1
    elif month in ("2", "02", "feb", "february"):
        month_int = 2
    elif month in ("3", "03", "mar", "march"):
        month_int = 3
    elif month in ("4", "04", "apr", "april"):
        month_int = 4
    elif month in ("5", "05", "may", "may"):
        month_int = 5
    elif month in ("6", "06", "jun", "june"):
        month_int = 6
    elif month in ("7", "07", "jul", "july"):
        month_int = 7
    elif month in ("8", "08", "aug", "august"):
        month_int = 8
    elif month in ("9", "09", "sep", "september"):
        month_int = 9
    elif month in ("10", "oct", "october"):
        month_int = 10
    elif month in ("11", "nov", "november"):
        month_int = 11
    elif month in ("12", "dec", "december"):
        month_int = 12
    else:
        raise ValueError(month + " is not a valid month str")

    return month_int


def quarter_str_to_int(quarter):
    """ Convert quarter string to int. Also applicable for certain month strings

    Args:
        quarter (str): "1"-"4", "01"-"04", "first", "second", "third", "fourth", "1st", "2nd", "3rd", "4th",
            "first 3 letters of month", "full month name". case insensitive
    Returns:
        int: value of quarter (1-4)

    Raises:
        Union[TypeError, ValueError]: TypeError if quarter is not a str. ValueError if quarter is not a supported value
            in a valid format
    """
    if not isinstance(quarter, str):
        raise TypeError("quarter is not a str type")

    quarter = quarter.lower()

    if quarter in ("1", "01", "first", "1st", "jan", "feb", "mar", "january", "february", "march"):
        quarter_int = 1
    elif quarter in ("2", "02", "second", "2nd", "apr", "may", "jun", "april", "may", "jun"):
        quarter_int = 2
    elif quarter in ("3", "03", "third", "3rd", "jul", "aug", "sep", "july", "august", "september"):
        quarter_int = 3
    elif quarter in ("4", "04", "fourth", "4th", "oct", "nov", "dec", "october", "november", "december"):
        quarter_int = 4
    else:
        raise ValueError(quarter + " is not a valid quarter str")

    return quarter_int


def date_of_month(month, last=True):
    """ Determine first or last date of month with leap year considered every 4 years (but not 100 or 400 years).

    Args:
        month (Union[str, int, datetime.date]): case insensitive.
            str formats: "1"-"12", "01"-"12", "first 3 letters", "full month name", "YYYYMM", "YYYYMMDD"
            int formats: 1-12. Note: February is considered for the current year if str or int format is used.
        last (boolean): False for first date of month. Default True for last date of month

    Returns:
        datetime.date: for the same year and month and day = first or last day of month

    Raises:
        Union[TypeError, ValueError]: TypeError if month is not a supported type. ValueError if month is not a
            supported value in a valid format
    """
    if isinstance(month, datetime.date):
        year_int = month.year
        month_int = month.month
    elif isinstance(month, int):
        if month < 1 or month > 12:
            raise ValueError(str(month) + " is not a valid month int (1-12)")

        year_int = datetime.date.today().year
        month_int = month
    elif isinstance(month, str):
        try:
            # "1"-"12", "01"-"12", "first 3 letters", "full month name"
            month_int = month_str_to_int(month)
            year_int = datetime.date.today().year
        except ValueError:
            # "YYYYMM", "YYYYMMDD"
            if len(month) in (6, 8):
                year_int = int(month[0:4])
                month_int = int(month[4:6])
            else:
                raise ValueError(str(month) + " is not a valid month format")
    else:
        raise TypeError(type(month) + " is not a supported type")

    if last is True:
        if month_int == 12:
            month_int = 1
            year_int += 1
        else:
            month_int += 1

        return datetime.date(year=year_int, month=month_int, day=1) - datetime.timedelta(1)
    else:
        return datetime.date(year=year_int, month=month_int, day=1)


def month_to_quarter(month):
    """ Determine the quarter (1-4) for the given month

    Args:
        month (Union[str, int, datetime.date]): str formats: "1"-"12", "01"-"12", "first 3 letters", "full month name".
            int formats: 1-12.

    Returns:
        int: (1-4) for the quarter which month is in

    Raises:
        Union[TypeError, ValueError]: TypeError if month is not a supported type. ValueError if month is not a
            supported value in a valid format
    """
    if isinstance(month, datetime.date):
        month_int = month.month
    elif isinstance(month, int):
        if month < 1 or month > 12:
            raise ValueError(str(month) + " is not a valid month int")
        month_int = month
    elif isinstance(month, str):
        month_int = month_str_to_int(month)
    else:
        raise TypeError(str(type(month)) + " is not a valid month type")

    return (month_int - 1) // 3 + 1


def date_of_quarter(quarter, last=True):
    """ Determine first or last date of quarter

    Args:
        quarter (Union[str, int, datetime.date]): return first or last date for specified quarter. int formats: 1-4
            str formats: "1"-"4", "01"-"04", "first", "second", "third", "fourth", "1st", "2nd", "3rd", "4th",
                "first 3 letters of month", "full month name", "YYYYQ", "YYYYMM", "YYYYMMDD". case insensitive
        last (boolean): False for first date of quarter. Default True for last date of quarter

    Returns:
        datetime.date: for the same year and month = first or last month of quarter and day = first or last day of month

    Raises:
        Union[TypeError, ValueError]: TypeError if quarter is not a supported type. ValueError if quarter is not a
            supported value in a valid format
    """
    if isinstance(quarter, datetime.date):
        quarter_int = month_to_quarter(quarter)
        year_int = quarter.year
    elif isinstance(quarter, int):
        if quarter < 1 or quarter > 4:
            raise ValueError(str(quarter) + " is not a valid quarter int (1-4)")
        quarter_int = quarter
        year_int = datetime.date.today().year
    elif isinstance(quarter, str):
        try:
            # str formats: "1" - "4", "01" - "04", "first", "second", "third", "fourth", "1st", "2nd", "3rd", "4th",
            # "first 3 letters of month", "full month name"
            quarter_int = quarter_str_to_int(quarter)
            year_int = datetime.date.today().year
        except ValueError:
            # str formats: "YYYYQ", "YYYYMM", "YYYYMMDD"
            if len(quarter) == 5:
                quarter_int = int(quarter[4])
            elif len(quarter) in (6, 8):
                quarter_int = month_to_quarter(quarter[4:6])
            else:
                raise ValueError(str(quarter) + " is not a valid quarter str format")

            year_int = int(quarter[0:4])
    else:
        raise TypeError(str(type(quarter)) + " is not a supported type")

    if last is True:
        return date_of_month(datetime.date(year=year_int, month=(quarter_int * 3), day=1))
    else:
        return datetime.date(year=year_int, month=(quarter_int * 3 - 2), day=1)


def date_of_year(year, last=True):
    """ Determine first or last date of year

    Args:
        year (Union[str, int, datetime.date]): return first date and last date for specified year
            str formats: YYYY, YYYYMM, YYYYMMDD, int formats: 1-9999 (datetime.date limits)
        last (boolean): False for first date of year. Default True for last date of year

    Returns:
        datetime.date: for the same year and month = first or last month of year and day = first or last day of month

    Raises:
        Union[TypeError, ValueError]: TypeError if year is not a supported type. ValueError if year is not a supported
            value in a valid format
    """
    if isinstance(year, datetime.date):
        year_int = year.year
    elif isinstance(year, int):
        year_int = year
    elif isinstance(year, str):
        if len(year) in (4, 6, 8):
            year_int = year[0:4]
        else:
            raise ValueError(str(year) + " is not a valid quarter str format")
    else:
        raise TypeError(str(type(year)) + " is not a supported type")

    if last is True:
        return datetime.date(year=year_int, month=12, day=31)
    else:
        return datetime.date(year=year_int, month=1, day=1)


def previous_month_end(date, biz_day=True):
    date = date_of_month(date, last=False) - datetime.timedelta(1)
    return nearest_biz_day(date) if biz_day else date


def closest_date(date, date_list):
    return min(date_list, key=lambda d: abs(d - date))


def date_range(start, end, biz_days=True, inc_start=True, inc_end=True, inc_holidays=True):
    """ Create list of all dates between start and end

    Args:
        start (datetime.date)
        end (datetime.date)
        biz_days (boolean): True for only business days (start will be moved forward to the next business day
            if is not a business day). False for all days. Default True
        inc_start (boolean): True to include start in return list. False to remove. Default True
        inc_end (boolean): True to include end in return list. False to remove. Default True
        inc_holidays (boolean): True to include holidays. False to remove but note that if inc_start (inc_end)
            are True, then start (end) will not be removed, even if they are holidays.  Default True

    Returns:
        list[datetime.date]:
    """
    if inc_start and biz_days and datetime.date.weekday(start) in (5, 6):
        start = change_dt_date(start, biz_days=1)
    elif not inc_start:
        start = change_dt_date(start, biz_days=1) if biz_days else change_dt_date(start, days=1)
    if not inc_end:
        end = change_dt_date(end, biz_days=-1) if biz_days else change_dt_date(end, days=-1)

    dates = []
    dt = start
    if biz_days:
        while dt <= end:
            dates.append(dt)
            dt = change_dt_date(dt, biz_days=1)
    else:
        while dt <= end:
            dates.append(dt)
            dt = change_dt_date(dt, days=1)

    if not inc_holidays:
        h_dates = nyse_holidays(dates)
        if dates[0] in h_dates:
            h_dates.remove(dates[0])
        if dates[-1] in h_dates:
            h_dates.remove(dates[-1])
        dates = [x for x in dates if x not in h_dates]

    return dates


def dt_range(start, end, mkt_time=None, interval="minute", finer_to_0=True):
    """ Create list of all datetimes between start and end inclusive

    Args:
        start (datetime.datetime)
        end (datetime.datetime)
        mkt_time (Optional[str]): only keep dts for certain market time ranges. Default None for all dts.
            "US": US regular market hours Mon-Fri 9:30:00.000000 to 16:00:00.000000 PM.
        interval (str): "second", "minute", "hour", "day". Default "minute"
        finer_to_0 (boolean): False to leave the finer time values (as compared to interval) for start and end
            as they are. True to change them to 0.
            e.g. True, interval == "second" and start has time 15:59:42.126704. change start to 15:59:42.000000
            e.g. True, interval == "minute" and start has time 15:59:42.126704. change start to 15:59:00.000000
            e.g. False, interval == "hour" and start has time 15:59:42.126704. start remains to 15:59:42.126704

    Returns:
        list[datetime.datetime]:
    """
    if interval == "second":
        if finer_to_0:
            start = start.replace(microsecond=0)
            end = end.replace(microsecond=0)

        def int_func(x): return x + datetime.timedelta(seconds=1)
    elif interval == "minute":
        if finer_to_0:
            start = start.replace(second=0, microsecond=0)
            end = end.replace(second=0, microsecond=0)

        def int_func(x): return x + datetime.timedelta(minutes=1)
    elif interval == "hour":
        if finer_to_0:
            start = start.replace(minute=0, second=0, microsecond=0)
            end = end.replace(minute=0, second=0, microsecond=0)

        def int_func(x): return x + datetime.timedelta(hours=1)
    elif interval == "day":
        if finer_to_0:
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = end.replace(hour=0, minute=0, second=0, microsecond=0)

        def int_func(x): return x + datetime.timedelta(days=1)
    else:
        raise ValueError(interval + " not implemented in PyUtil.dt_range() interval")

    if mkt_time is None:
        def mkt_func(x1): return x1
    elif mkt_time == "US":
        def mkt_func(x1):
            if datetime.datetime.weekday(x1) in (5, 6) or datetime.time(16, 0) < x1.time():
                # if weekend, go to monday at 9:30.00 AM
                # if time is after 4:00.00 PM but before 00:00.00, go to next business day at 9:30.00 AM
                x1 = change_dt(x1, biz_days=1).replace(hour=9, minute=30, second=0)
            elif x1.time() < datetime.time(9, 30):
                # if time is after 00:00.00 but before 9:30.00 AM, go to same day at 9:30.00 AM
                x1 = x1.replace(hour=9, minute=30, second=0)

            return x1
    else:
        raise ValueError(mkt_time + " not implemented in PyUtil.dt_range() mkt_time")

    dts = []
    dt = mkt_func(start)

    while dt <= end:
        dts.append(dt)
        dt = int_func(dt)
        dt = mkt_func(dt)

    return dts


def date_diff_days(date1, date2, biz_days=False):
    """ Calculate number of days between date1 and date2

    Holidays are not skipped. If either date is a weekend date and biz_days is True, those date(s) are moved to the
    previous Friday. If date2 is less than date1, a negative number will be returned

    Args:
        date1 (datetime.date):
        date2 (datetime.date):
        biz_days (boolean): Default False

    Returns:
        int: number of days such that if you start counting on date 1 (and consider biz days or not),
            you will end on date2
    """
    if biz_days:
        return np.busday_count(nearest_biz_day(date1), nearest_biz_day(date2))
    else:
        return (date2 - date1).days


def html_rgd_fmt(numbers, comma=True, frac=0):
    """ Prepend $ to numbers and set font color to red if < 0 or green if >= 0

    Args:
        numbers (Union[int, float, list, tuple])
        comma (boolean): True to use comma separated thousands. False for no commas. Default True
        frac (int): number of fractional digits. Default 0

    Returns:
        list[str]: of converted numbers
    """
    if not isinstance(numbers, (list, tuple)):
        numbers = [numbers]
    fmt_str = "${0:" + ("," if comma else "") + "." + str(frac) + "f}"
    return ["<font color=" + ('red' if x < 0 else 'green') + ">" + fmt_str.format(x) + "</font>" for x in numbers]
