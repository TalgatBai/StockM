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
from marketwatch_stock_financials_class import marketwatch_stock_financials_class

# the keys are stock symbols and the values are eps , net-icome and sales growths arrays.
global_stock_dict = {}

            

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

    if os.path.exists(failed_stocks_file):
        with open(failed_stocks_file, 'r+') as f:
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

def fill_global_stock_dict_with_stock(stock_symbol):

    stock = marketwatch_stock_financials_class(stock_symbol)
    global_stock_dict[stock_symbol][0] = stock.get_q_eps_growth_array()
    global_stock_dict[stock_symbol][1] = stock.get_q_net_income_growth_array()
    global_stock_dict[stock_symbol][2] = stock.get_q_sales_growth_array()

    
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

            t1 =  pool.submit(fill_global_stock_dict_with_stock, stock_symbol) 
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