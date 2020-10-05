import requests
import re
from bs4 import BeautifulSoup
import array as arr
import ast
from operator import eq, add, sub
import sqlite3 
from threading import Thread
import threading
import time
import json
from multiprocessing import Process, Value
from concurrent.futures import ThreadPoolExecutor
import os.path
import requests
import re

# the keys are stock symbols and the values are eps , net-icome and sales growths arrays.
global_stock_dict = {}



class MarketWatch_Scrapper_Financials:

    def __init__(self,stock_name):
        self.stock_name = stock_name
    
    def run(self):
        self.soup = self.get_html_financial_data()
        self.generic_get_value()  

    def get_html_financial_data(self):
        URL = 'https://www.marketwatch.com/investing/stock/'+self.stock_name+'/financials/balance-/quarter'
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup


    def get_growth_array(self, row, number_of_quarters):
        
        array_of_values = []
        next_tag = row
        x = 0
        for x in range(number_of_quarters+1):
            new_tag = next_tag.find_next("td")
            value_to_insert_to_array = new_tag.text
            if ( value_to_insert_to_array == '-'):
                value_to_insert_to_array = '0%'
            array_of_values.append(value_to_insert_to_array)
            next_tag = new_tag

        return array_of_values

    def generic_get_value(self):
        

        soup_results_array = self.soup.findAll("tr",{"class":"childRow hidden"})
        number_of_quarters = 4
        for soup_result in soup_results_array :        
          
          for row in soup_result.findAll("td")  :

            if (row.text == "EPS (Basic) Growth"):
                global_stock_dict[self.stock_name][0] = self.get_growth_array(row, number_of_quarters)
            
            if (row.text == "Net Income Growth"):
                global_stock_dict[self.stock_name][1] = self.get_growth_array(row, number_of_quarters)            
            
            if (row.text == "Sales Growth"):
                global_stock_dict[self.stock_name][2] = self.get_growth_array(row, number_of_quarters)
           


              

def read_stock_file(file_path):
    stock_map = {}
    f = open(file_path, "r")
    for stock in f:
        stock_array = stock.split()
        if (len(stock_array) > 1) :
            # clean the stock name
            if ((stock_array[1][-1] == '-') or (stock_array[1][-1] == '.')):
                stock_array[1] = stock_array[1][:-1]
            # build hash map 
            stock_map[stock_array[0]] = stock_array[1]

    return stock_map
    
    
def write_db():
    db_file = 'stock_db.txt'
    failed_stocks_file = 'failed_stocks.txt'

    if os.path.exists(db_file):
        with open(db_file, 'r+') as f:
            f.truncate(0)  # need '0' when using r+

    for stock_symbol in global_stock_dict:

        eps_growth_array = global_stock_dict[stock_symbol][0]
        net_income_growth_array = global_stock_dict[stock_symbol][1]
        sales_growth_array = global_stock_dict[stock_symbol][2]

        if ( not eps_growth_array ) and ( not net_income_growth_array ) and ( not sales_growth_array):
            with open(failed_stocks_file, 'a') as filehandle:
                filehandle.write(stock_symbol+'\n')
        
        else :
        
            # open output file for writing
            with open(db_file, 'a') as filehandle:
                filehandle.write(stock_symbol +' net_income_growth ')
                json.dump(net_income_growth_array, filehandle)
                filehandle.write(' eps_growth ')
                json.dump(eps_growth_array, filehandle)
                filehandle.write(' sales_growth ')
                json.dump(sales_growth_array, filehandle)
                filehandle.write('\n')



    
def iteatre_over_stock_map(stock_map):

    start = time.time()
    maximum_thrads = 200
    timout_between_threads_creation = 0.02
    
    pool = ThreadPoolExecutor(max_workers = maximum_thrads)
    for stock_symbol in stock_map:
        try:
            global global_stock_dict
            print(stock_symbol)
            global_stock_dict[stock_symbol] = [[],[],[]]
            sem = threading.Semaphore(4)

            market_watch_object = MarketWatch_Scrapper_Financials(stock_symbol)

            t1 =  pool.submit(market_watch_object.run) 
            time.sleep(timout_between_threads_creation)

        except:
            pass
            
    end = time.time()
    print(end - start)
    pool.shutdown(wait=True)
            
def main():
    
    stock_symbols_file = "all_stocks.txt"
    
    stock_map = read_stock_file(stock_symbols_file)
    iteatre_over_stock_map(stock_map)
    write_db()
    
    
if __name__== "__main__":
    main()