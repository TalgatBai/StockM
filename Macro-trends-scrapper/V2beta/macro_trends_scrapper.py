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
        self.fill_global_stock_dict()  

    def get_html_financial_data(self):
        URL = 'https://www.marketwatch.com/investing/stock/'+self.stock_name+'/financials/balance-/quarter'
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup


    def generic_get_value(self,soup,str_val, str_class, target_line_num):
        
        results = self.soup.findAll(str_val,{"class":str_class})[target_line_num]
        td_row_count = 0
        target_row_location_number = 6
        array_of_values = []
        for row in results.findAll("td")  :

            if (td_row_count == target_row_location_number):
                target_line_not_parsed = str(row).split(':')[1]
                target_line_parsed = target_line_not_parsed.split('}')[0]
                if (target_line_parsed.find('null') != -1): 
                    target_line_parsed = target_line_parsed.replace("null", "0")
                array_of_values = ast.literal_eval(target_line_parsed)
                print(array_of_values)
                return array_of_values
            
            if (td_row_count > target_row_location_number):
                break
            
            td_row_count = td_row_count + 1
        
        return array_of_values 

      

    def get_eps_growth(self):
        return self.generic_get_value(self.soup,"tr","childRow hidden",10)
        
    def get_net_income_growth(self):
        return self.generic_get_value(self.soup,"tr","childRow hidden",8)    
    
    def get_sales_growth(self):
        return self.generic_get_value(self.soup,"tr","childRow hidden",0)         


    def fill_global_stock_dict(self):
        global global_stock_dict

        global_stock_dict[self.stock_name][0] = self.get_eps_growth()
        global_stock_dict[self.stock_name][1] = self.get_net_income_growth()
        global_stock_dict[self.stock_name][2] = self.get_sales_growth()


              

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
    maximum_thrads = 100
    timout_between_threads_creation = 0.02
    
    pool = ThreadPoolExecutor(max_workers = maximum_thrads)
    for stock_symbol in stock_map:
        try:
            global global_stock_dict
            print(stock_symbol)
            global_stock_dict[stock_symbol] = ['','','']
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