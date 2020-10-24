from yahoofinancials import YahooFinancials
from pandas.tseries.offsets import BDay
from pandas import bdate_range
from datetime import datetime, timedelta, date, time
from enum import Enum
import holidays
import pytz

NASDAQ_COMPOSITE_SYMBOL = '^IXIC'
US_EASTERN = 'US/Eastern'
START_OF_TODAY = datetime.combine(date.today(), time())
MARKET_START_TIME = START_OF_TODAY.replace(hour=9, minute=30, second=0)
MARKET_END_TIME = START_OF_TODAY.replace(hour=16, minute=0, second=0)


class MarketStatus(Enum):
    BEFORE_MARKET_OPEN = 'before market open'
    TRADING_TIME = 'trading time'
    AFTER_MARKET_CLOSED = 'after market closed'


class NasdaqComposite:
    def __init__(self, ma_3, ma_3_change, ma_7, ma_7_change):
        self.ma_3 = ma_3
        self.ma_3_change = ma_3_change
        self.ma_7 = ma_7
        self.ma_7_change = ma_7_change


def check_ma_3_and_ma_7_percentage_changes(ma_3_change, ma_7_change, market_notes):
    if not ma_3_change > 0:
        market_notes.append('MA(3) change <= 0')
    if not ma_7_change > 0:
        market_notes.append('MA(7) change <= 0')
    if not ma_3_change > ma_7_change:
        market_notes.append('MA(3) <= MA(7)')


def check_ma_3_and_ma_7(ma_3, ma_7, market_notes):
    if not ma_3 > ma_7:
        market_notes.append('MA(3) <= MA(7)')


def get_last_ma_change(first_ma, second_ma):
    return round((second_ma - first_ma) / first_ma * 100, 2)


def calc_ma_by_parameter(historical_prices, ma_parameter):
    sum_of_prices = 0
    for i in range(ma_parameter):
        price = historical_prices[i]['close']
        sum_of_prices += price
    return sum_of_prices / ma_parameter


def calc_historical_prices(stock, ma_calc_end_range, trading_days_to_reach):
    business_days_to_go_back = trading_days_to_reach
    while True:
        ma_calc_start_range = ma_calc_end_range - BDay(business_days_to_go_back)
        historical_prices = stock.get_historical_price_data(start_date=ma_calc_start_range.strftime('%Y-%m-%d'),
                                                            end_date=ma_calc_end_range.strftime('%Y-%m-%d'),
                                                            time_interval='daily')[NASDAQ_COMPOSITE_SYMBOL]['prices']
        if len(historical_prices) < trading_days_to_reach:
            business_days_to_go_back += 1
        else:
            return historical_prices


def get_moving_avg_by_parameter_and_last_trading_day(stock, ma_parameter, day_to_calc_ma_for):
    try:
        historical_prices = calc_historical_prices(stock, day_to_calc_ma_for + timedelta(days=1), ma_parameter)
        ma_by_parameter = calc_ma_by_parameter(historical_prices, ma_parameter)
        return round(ma_by_parameter, 2)
    except Exception as e:
        print(str(e))


def get_3day_moving_avg(stock, day):
    return get_moving_avg_by_parameter_and_last_trading_day(stock, 3, day)


def get_7day_moving_avg(stock, day):
    return get_moving_avg_by_parameter_and_last_trading_day(stock, 7, day)


def is_trading_day(date_to_check):
    is_business_day = len(bdate_range(date_to_check, date_to_check)) == 1
    is_holiday = date_to_check in holidays.USA()
    return is_business_day and not is_holiday


def get_current_market_status():
    if not is_trading_day(datetime.today()):
        return None

    wall_street_timezone = pytz.timezone(US_EASTERN)
    wallstreet_local_time_now = datetime.now(wall_street_timezone).replace(tzinfo=None)
    if wallstreet_local_time_now < MARKET_START_TIME:
        return MarketStatus.BEFORE_MARKET_OPEN
    elif wallstreet_local_time_now <= MARKET_END_TIME:
        return MarketStatus.MARKET_OPEN
    else:
        return MarketStatus.AFTER_MARKET_CLOSED


def calc_last_trading_day(day):
    if not is_trading_day(day) or get_current_market_status() == MarketStatus.BEFORE_MARKET_OPEN:
        day -= BDay(1)
        while not is_trading_day(day):
            day -= BDay(1)
    return day


def is_market_in_a_buy_situation(stock):
    market_notes = []

    last_active_trading_day = calc_last_trading_day(datetime.today())
    previous_active_trading_day = calc_last_trading_day(last_active_trading_day - BDay(1))

    current_ma_3 = get_3day_moving_avg(stock, last_active_trading_day)
    current_ma_7 = get_7day_moving_avg(stock, last_active_trading_day)

    previous_ma_3 = get_3day_moving_avg(stock, previous_active_trading_day)
    previous_ma_7 = get_7day_moving_avg(stock, previous_active_trading_day)

    current_ma_3_percentage_change = get_last_ma_change(previous_ma_3, current_ma_3)
    current_ma_7_percentage_change = get_last_ma_change(previous_ma_7, current_ma_7)

    check_ma_3_and_ma_7(current_ma_3, current_ma_7, market_notes)
    check_ma_3_and_ma_7_percentage_changes(current_ma_3_percentage_change, current_ma_7_percentage_change, market_notes)

    print(f'Last active trading day: {last_active_trading_day.strftime("%d-%m-%Y")}')
    print(f'Previous active trading day: {previous_active_trading_day.strftime("%d-%m-%Y")}\n')
    print(f'Current MA(3) = {current_ma_3}')
    print(f'Current MA(7) = {current_ma_7}\n')
    print(f'Previous MA(3) = {previous_ma_3}')
    print(f'Previous MA(7) = {previous_ma_7}\n')
    print(f'Current MA(3) change = {current_ma_3_percentage_change}%')
    print(f'Current MA(7) change = {current_ma_7_percentage_change}%\n')

    return market_notes


def main():
    yahoo_stock = YahooFinancials(NASDAQ_COMPOSITE_SYMBOL)
    market_notes = is_market_in_a_buy_situation(yahoo_stock)
    if not market_notes:
        print('BUY')
    else:
        print('DO NOT BUY due to the following reasons:')
        for note in market_notes:
            print(f'* {note}')


if __name__ == "__main__":
    main()
