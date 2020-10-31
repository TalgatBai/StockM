import concurrent.futures
import json
import os.path
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Manager

from marketwatch_stock_financials_class import marketwatch_stock_financials_class


def multi_process_write_db(manager_dict):
    db_file = 'stock_db.txt'
    failed_stocks_file = 'failed_stocks.txt'

    if os.path.exists(db_file):
        with open(db_file, 'r+') as f:
            f.truncate(0)  # need '0' when using r+

    if os.path.exists(failed_stocks_file):
        with open(failed_stocks_file, 'r+') as f:
            f.truncate(0)  # need '0' when using r+

    for stock_symbol in manager_dict:

        eps_growth_array = manager_dict[stock_symbol][0]
        net_income_growth_array = manager_dict[stock_symbol][1]
        sales_growth_array = manager_dict[stock_symbol][2]

        if (not eps_growth_array) and (not net_income_growth_array) and (not sales_growth_array):
            with open(failed_stocks_file, 'a') as filehandle:
                filehandle.write(stock_symbol + '\n')

        else:

            # open output file for writing
            with open(db_file, 'a') as filehandle:
                filehandle.write(stock_symbol + ' net_income_growth ')
                json.dump(net_income_growth_array, filehandle)
                filehandle.write(' eps_growth ')
                json.dump(eps_growth_array, filehandle)
                filehandle.write(' sales_growth ')
                json.dump(sales_growth_array, filehandle)
                filehandle.write('\n')


def multi_process_fill_global_stock_dict_with_stock(params):
    manager_dict = params[0]
    stock_symbol = params[1]
    stock = marketwatch_stock_financials_class(stock_symbol)
    manager_dict[stock_symbol] = [stock.get_q_eps_growth_array(),
                                  stock.get_q_net_income_growth_array(),
                                  stock.get_q_sales_growth_array()]


def multi_process_iterate_over_stock_map(manager_dict, stocks_map):
    maximum_threads = 200
    timeout_between_threads_creation = 0.02

    pool = ThreadPoolExecutor(max_workers=maximum_threads)
    for stock_symbol in stocks_map:
        try:
            print(stock_symbol)
            manager_dict[stock_symbol] = [[], [], []]
            args = (manager_dict, stock_symbol)
            pool.submit(multi_process_fill_global_stock_dict_with_stock, args)
            time.sleep(timeout_between_threads_creation)

        except:
            pass
    pool.shutdown(wait=True)


def multi_process_read_stock_file(file_path):
    stock_map = {}
    f = open(file_path, "r")
    for stock in f:
        stock_array = stock.split()
        if (len(stock_array) > 1):
            # clean the stock name
            if ((stock_array[1][-1] == '-') or (stock_array[1][-1] == '.')):
                stock_array[1] = stock_array[1][:-1]
            # build hash map
            stock_map[stock_array[0]] = stock_array[1]

    return stock_map


def multi_process_for_file(params):
    manager_dict = params[0]
    file_name = params[1]
    print(f'Running file {file_name}')
    stocks_map = multi_process_read_stock_file(file_name)
    multi_process_iterate_over_stock_map(manager_dict, stocks_map)


def multi_process_main():
    stock_symbols_files = [
        "all_stocks_1.txt",
        "all_stocks_2.txt",
        "all_stocks_3.txt"
    ]

    start = time.time()
    with Manager() as manager:
        stocks_dict = manager.dict()
        with concurrent.futures.ProcessPoolExecutor() as executor:
            args = ((stocks_dict, file) for file in stock_symbols_files)
            executor.map(multi_process_for_file, args)
        multi_process_write_db(stocks_dict)

    end = time.time()
    total_minutes = round((end - start) / 60, 2)
    print(f'Scrapper took {total_minutes} minutes')


if __name__ == "__main__":
    # main()
    multi_process_main()
