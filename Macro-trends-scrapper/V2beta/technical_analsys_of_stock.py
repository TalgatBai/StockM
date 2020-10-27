from yahoofinancials import YahooFinancials
from heapq import heappush, heappop
import datetime
import pytz
import concurrent.futures
import os


class CandidateStock:

    def __init__(self, symbol, price_percent_change):
        self.symbol = symbol
        self.price_percent_change = price_percent_change

    def __str__(self):
        return str.format("{}, price_change: {}%", self.symbol, self.price_percent_change)

    def __lt__(self, other):
        return other.price_percent_change < self.price_percent_change

    def __gt__(self, other):
        return other.__lt__(self)

    def __eq__(self, other):
        return self.price_percent_change == other.price_percent_change

    def __ne__(self, other):
        return not self.__eq__(other)


technically_valid_stocks_heap = []
breakout_stocks_heap = []
stocks_info_files_list = ['acceleration_stocks.txt', 'growth_stocks.txt']
technically_valid_stocks_file = 'technically_valid_stocks.txt'
breakout_stocks_file = 'breakout_stocks.txt'


def is_market_open(nyc_datetime):
    if (nyc_datetime.hour < 8) or (nyc_datetime.hour > 15):
        return False

    if (nyc_datetime.hour == 8) and (nyc_datetime.minute < 30):
        return False

    if (nyc_datetime.hour == 15) and (nyc_datetime.minute > 0):
        return False

    return True


def get_relative_time_percentage(nyc_datetime):
    time_of_nasdaq_open_in_minutes = 390
    hour_difference = nyc_datetime.hour - 9
    hour_difference_in_minutes = hour_difference * 60
    minutes_difference = nyc_datetime.minute - 30
    sum_of_min_difference = minutes_difference + hour_difference_in_minutes
    return sum_of_min_difference / time_of_nasdaq_open_in_minutes


def detect_breakout(stock, volume_threshold, percent_threshold):
    is_breakout = False
    nyc_datetime = datetime.datetime.now(pytz.timezone('US/Eastern'))
    market_open_flag = is_market_open(nyc_datetime)

    if not market_open_flag:
        return False

    stock_current_volume = stock.get_current_volume()
    stock_3m_avg_volume = stock.get_three_month_avg_daily_volume()
    relative_time_percentage = get_relative_time_percentage(nyc_datetime)
    stock_3m_avg_relative_volume = relative_time_percentage * stock_3m_avg_volume
    stock_current_percent_change = stock.get_current_percent_change()

    if (stock_current_volume >= stock_3m_avg_relative_volume * volume_threshold) and (stock_current_percent_change >= percent_threshold):
        is_breakout = True

    return is_breakout


def validate_stock_technically(stock):
    stock_50_ma = stock.get_50day_moving_avg()
    stock_200_ma = stock.get_200day_moving_avg()
    stock_current_price = stock.get_current_price()
    stock_yearly_low = stock.get_yearly_low()
    stock_yearly_high = stock.get_yearly_high()

    if stock_50_ma <= stock_200_ma:
        return False

    if stock_current_price < (stock_50_ma * 0.9):
        return False

    if stock_yearly_low * 1.3 > stock_current_price:
        return False

    if stock_yearly_high * 0.75 > stock_current_price:
        return False

    return True


def run_yahoo_stocks(stock_symbol):
    global technically_valid_stocks_heap
    global breakout_stocks_heap
    print(stock_symbol)
    yahoo_stock = YahooFinancials(stock_symbol)
    candidate_stock = CandidateStock(stock_symbol, round(yahoo_stock.get_current_percent_change() * 100, 2))

    if validate_stock_technically(yahoo_stock):
        heappush(technically_valid_stocks_heap, candidate_stock)
        if detect_breakout(yahoo_stock, 1.2, 0.02):
            heappush(breakout_stocks_heap, candidate_stock)


def write_technically_valid_stocks():
    write_stocks_to_file(technically_valid_stocks_file, technically_valid_stocks_heap)


def write_breakthrough_stocks():
    write_stocks_to_file(breakout_stocks_file, breakout_stocks_heap)


def write_stocks_to_file(stocks_file, heap):
    if os.path.exists(stocks_file):
        with open(stocks_file, 'r+') as f:
            f.truncate(0)  # need '0' when using r+

    with open(stocks_file, 'a') as stocks_output_file:
        while heap:
            stocks_output_file.write(str(heappop(heap)) + '\n')


def main():
    stocks_set = set()
    for file in stocks_info_files_list:
        try:
            with open(file, 'r+') as f:
                for line in f:
                    stock_symbol = line.split(',')[0]
                    stocks_set.add(stock_symbol)
        except:
            print(f'Failed to read {file}')

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(stocks_set)) as executor:
        executor.map(run_yahoo_stocks, stocks_set)

    write_technically_valid_stocks()
    write_breakthrough_stocks()


if __name__ == "__main__":
    main()
