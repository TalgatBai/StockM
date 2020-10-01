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


global_stock_dict = {}

# class yahoo_generic:

    # def __init__(self,stock_symbol, company_name, operation):
        # #Private methods and members
        # self.__symbol = stock_symbol
        # self.__company_name = company_name
        # self.__operation = operation
        # self.__yahoo_list = []


    # def run(self):
        # self.__soup = self.__get_html_profile_data()
        # self.__fill_yahoo_list(self.__soup)
        # self.fill_global_stock_dict()

    # def __get_html_profile_data(self):
        # URL = 'https://finance.yahoo.com/quote/'+self.__symbol+'/analysis?p='+self.__symbol
        # page = requests.get(URL)
        # soup = BeautifulSoup(page.content, 'html.parser')
        # return soup
    
            
    # def __fill_yahoo_list(self,soup):
        # results = soup.findAll('span')
        # j = 0 
        # for res in results:
            # if (res.getText() == 'EPS Actual'):
                # for i in range(4):
                    # res = res.find_next('td')
                    # self.__yahoo_list.insert(0,res.text)

        
    
    
    # def get_list_func(self):
        # return self.__yahoo_list
        
    # def fill_global_stock_dict(self):
        # global global_stock_dict

        # if (self.__operation == 'eps'):
            # global_stock_dict[self.__symbol][0] = self.__yahoo_list
        # elif (self.__operation == 'net-income'):
            # global_stock_dict[self.__symbol][1] = self.__yahoo_list
        # else:
            # global_stock_dict[self.__symbol][2] = self.__yahoo_list



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


    def generic_get_value(self,soup,str_val,str_class,num):
        results = self.soup.findAll(str_val,{"class":str_class})[num]
        count = 0
        for row in results.findAll("td"):
            if (count >=6):
                a= str(row).split(':')[1]
                b = a.split('}')[0]
                if (b.find('null') != -1): 
                    b = b.replace("null", "0")
                res = ast.literal_eval(b) 
            count = count + 1
        return res 

      

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

    if os.path.exists(db_file):
        with open(db_file, 'r+') as f:
            f.truncate(0)  # need '0' when using r+

    for key in global_stock_dict:

        eps_growth_array = global_stock_dict[key][0]
        net_income_growth_array = global_stock_dict[key][1]
        sales_growth_array = global_stock_dict[key][2]

        # open output file for writing
        with open('stock_db.txt', 'a') as filehandle:
            filehandle.write(key +' net_income_growth ')
            json.dump(net_income_growth_array, filehandle)
            filehandle.write(' eps_growth ')
            json.dump(eps_growth_array, filehandle)
            filehandle.write(' sales_growth ')
            json.dump(sales_growth_array, filehandle)
            filehandle.write('\n')



    
def iteatre_over_stock_map(stock_map):

    i = 1
    start = time.time()
    pool = ThreadPoolExecutor(max_workers=100)
    for stock_symbol in stock_map:
        try:
            global global_stock_dict
            print(stock_symbol)
            global_stock_dict[stock_symbol] = ['','','']
            sem = threading.Semaphore(4)

            obj1 = MarketWatch_Scrapper_Financials(stock_symbol)
            # obj2 = macrotrends_generic(stock_symbol,stock_map[stock_symbol],'eps-earnings-per-share-diluted')
            # obj3 = macrotrends_generic(stock_symbol,stock_map[stock_symbol],'revenue')
            t1 =  pool.submit(obj1.run) 
            # t2 =  pool.submit(obj2.run) 
            # t3 =  pool.submit(obj3.run) 

            time.sleep(0.02)
            if (i % 20 == 0):
                time.sleep(0.05)
            i = i + 1


        except:
            print ('didnt work for'+ stock_symbol)
            pass
    end = time.time()
    print(end - start)
    pool.shutdown(wait=True)
            
def main():
    
    # stock1 = MarketWatch_Scrapper_Financials('prsc')
    # stock1.run()
    stock_map = read_stock_file("all_stocks.txt")
    iteatre_over_stock_map(stock_map)
    write_db()
    
    
if __name__== "__main__":
    main()