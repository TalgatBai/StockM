import threading
from concurrent.futures.thread import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import sys
from yahoofinancials import YahooFinancials
from heapq import heappush, heappop
import datetime
import pytz
import concurrent.futures
import os
from functools import partial
from collections import deque
import smtplib, ssl
import yagmail
import getpass
from social_media_class import social_media_class



class backround_breakout_thread_class(object):

    def __init__(self, password):

        self.stocks_set = self.__get_set_of_stocks()
        self.breakout_stocks = set()
        self.lock = threading.Lock()
        self.social_media_obj = social_media_class(password)


        try:
            thread = threading.Thread(target=self.run)
            thread.daemon = True
            thread.start()
            while thread.isAlive():
                thread.join(1)
        except (KeyboardInterrupt, SystemExit):
            print('program closed by user')


    def run(self):

        timer_of_breakout_checking = 60 * 15
        pool = ThreadPoolExecutor(max_workers = 10)

        while True:

            with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.stocks_set)) as executor:
                executor.map(self.__run_yahoo_stock, self.stocks_set)

            time.sleep(timer_of_breakout_checking)

    def __run_yahoo_stock(self, stock_symbol_and_pivot):


        stock_symbol = stock_symbol_and_pivot.split(':')[0]
        pivot = stock_symbol_and_pivot.split(':')[1]
        yahoo_stock = YahooFinancials(stock_symbol)

        if (stock_symbol in self.breakout_stocks):
            return

        stock_volume_increase_ratio = self.__detect_breakout(yahoo_stock, 1.4, 0.023, pivot,stock_symbol)
        if (stock_volume_increase_ratio != False):
            self.lock.acquire()
            try:

                self.breakout_stocks.add(stock_symbol)
                msg_to_send = 'Buy alert for ' + stock_symbol + ' As volume is bigger by : ' + stock_volume_increase_ratio +' than the avarage'
                self.social_media_obj.send_whatsapp_message('"Stocks alerts"', msg_to_send)
                self.social_media_obj.send_gmail_message(["aradinbar91@gmail.com","shaharman5@gmail.com"],msg_to_send)
            except (KeyboardInterrupt):
                print('secondary thread closed by user')
            finally:
                self.lock.release()


    def __get_relative_time_percentage(self, nyc_datetime):

        time_of_nasdaq_open_in_minutes = 390
        hour_difference = nyc_datetime.hour - 9
        hour_difference_in_minutes = hour_difference * 60
        minutes_difference = nyc_datetime.minute - 30
        sum_of_min_difference = minutes_difference + hour_difference_in_minutes
        return sum_of_min_difference / time_of_nasdaq_open_in_minutes

    def __is_market_open(self, nyc_datetime):

        if (nyc_datetime.isoweekday() == 6) or (nyc_datetime.isoweekday() == 7):
            return False

        if (nyc_datetime.hour < 9) or (nyc_datetime.hour > 16):
            return False

        if (nyc_datetime.hour == 9) and (nyc_datetime.minute < 30):
            return False

        if (nyc_datetime.hour == 16) and (nyc_datetime.minute > 0):
            return False

        return True


    def __detect_breakout(self, stock, volume_threshold, percent_threshold, pivot_point, stock_symbol):

        msg_to_send_if_breakout = False
        nyc_datetime = datetime.datetime.now(pytz.timezone('US/Eastern'))
        market_open_flag = self.__is_market_open(nyc_datetime)

        if not market_open_flag:
            return False

        stock_current_volume = stock.get_current_volume()
        stock_3m_avg_volume = stock.get_three_month_avg_daily_volume()
        relative_time_percentage = self.__get_relative_time_percentage(nyc_datetime)
        stock_3m_avg_relative_volume = relative_time_percentage * stock_3m_avg_volume
        stock_current_percent_change = stock.get_current_percent_change()
        stock_current_price = stock.get_current_price()

        if (stock_current_volume >= stock_3m_avg_relative_volume * volume_threshold) and (stock_current_percent_change >= percent_threshold) and (float(pivot_point) <= stock_current_price ):
            print('is_breakout for :'+ stock_symbol)
            msg_to_send_if_breakout = str(stock_current_volume / (stock_3m_avg_relative_volume * volume_threshold))
        else:
            print ('no breakout so far for :' + stock_symbol)
        return msg_to_send_if_breakout

    def __get_set_of_stocks(self):

        stocks_set = set()
        file = 'technically_valid_stocks.txt'
        try:
            with open(file, 'r+') as f:
                for line in f:
                    stock_symbol = line.split(',')[0]
                    pivot_point = line.split(' ')[2].rstrip()
                    stocks_set.add(stock_symbol+":"+pivot_point)
        except:
            print('Failed to read file')

        return stocks_set


def main():

    password = getpass.getpass('Password:')
    backround_onj = backround_breakout_thread_class(password)

if __name__ == "__main__":


    main()
