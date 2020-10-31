from yahoofinancials import YahooFinancials
import sys
import numpy as np

nyse_composite_index_symbol = '^NYA'
dow_index_symbol = '^DJI'
sp500_index_symbol = '^GSPC'
nasdaq_composite_symbol = '^IXIC'

def is_disturbtion_day(volume_yesterday, volume_today, price_today, price_yesterday,ma_yesterday,ma_today):

    is_disturbtion_day = False

    if ( volume_today > volume_yesterday ) and (price_today <= 0.998 * price_yesterday) :
        is_disturbtion_day = True

    return is_disturbtion_day


def calculate_ma(ma_days, map_of_prices):
    map_of_ma = {}

    j = 0
    sum = 0

    for j in range(ma_days):
        sum = sum + map_of_prices[j][1]

    first_ma = sum / ma_days
    date_of_first_ma = map_of_prices[ma_days-1][0]
    map_of_ma[ma_days] = [date_of_first_ma,first_ma]

    for i in range(ma_days + 1,len(map_of_prices)):

        current_price = map_of_prices[i-1][1]
        price_to_ommit = map_of_prices[i-1-ma_days][1]
        value_to_add_to_ma = ( current_price - price_to_ommit ) / ma_days
        date = map_of_prices[i-1][0]
        new_ma = map_of_ma[i-1][1] + value_to_add_to_ma
        map_of_ma[i] = [date,new_ma]

    return map_of_ma

def get_distribution_dict(index_symbol, ma_map):
    yahoo_stock = YahooFinancials(index_symbol)
    json = (yahoo_stock.get_historical_price_data('2020-01-01', '2020-10-25', 'daily'))
    price_yesterday = sys.maxsize
    volume_yesterday = sys.maxsize
    ma_yesterday = -1
    days_counter = 1
    days_counter_of_25_days = 0

    disturbtion_dict = {}


    for row in json[index_symbol]["prices"]:
        volume_today = row['volume']
        price_today = row['close']
        date = row['formatted_date']
        ma_today = ma_map[date]

        is_disturbtion = is_disturbtion_day(volume_yesterday, volume_today, price_today, price_yesterday,ma_yesterday,ma_today)
        if (is_disturbtion ):
            disturbtion_dict[days_counter] = [date,price_today]
            days_counter_of_25_days = 0

        volume_yesterday = volume_today
        price_yesterday = price_today
        ma_yesterday = ma_today
        days_counter = days_counter + 1
        days_counter_of_25_days = days_counter_of_25_days + 1


    return  disturbtion_dict


def get_ma_map(index_symbol,ma_days):

    yahoo_stock = YahooFinancials(index_symbol)
    json = (yahoo_stock.get_historical_price_data('2006-01-01', '2020-10-30', 'daily'))

    map_of_prices = {}

    x = 0
    for row in json[index_symbol]["prices"]:

        price_today = row['close']
        date = row['formatted_date']

        map_of_prices[x] = [date,price_today]

        x = x+ 1
    date_to_ma_with_index = calculate_ma(50, map_of_prices)

    map_date_to_ma = dict()
    for x in date_to_ma_with_index :
        map_date_to_ma[date_to_ma_with_index[x][0]] = [date_to_ma_with_index[x][1]]


    return map_date_to_ma

def sliding_window(window_size,points_num, stock_dict):

    dates_to_return = []
    number_of_points = 0
    point_compare_iter = iter(stock_dict)
    point_iter = iter(stock_dict)

    # first comparison with the element at points_num distance
    for x in range(0,points_num) :
        point_to_compare = (next(point_compare_iter))

    for point in point_iter:

        if (number_of_points < len(stock_dict)-points_num):

            if (point_to_compare-point) <= window_size:
                dates_to_return.append(stock_dict[point_to_compare][0])

            point_to_compare = (next(point_compare_iter))

        number_of_points = number_of_points + 1

    return dates_to_return

def get_common_elemtns_from_lists(list_of_all_dates_from_all_index):
       return  np.intersect1d(list_of_all_dates_from_all_index[0], list_of_all_dates_from_all_index[1],list_of_all_dates_from_all_index[2])

def flatten_list(list_of_all_dates_from_all_index, remove_duplicate_flag, sort_list_flag):

        flat_list = [item for sublist in list_of_all_dates_from_all_index for item in sublist]

        if (remove_duplicate_flag):
            flat_list = list(dict.fromkeys(flat_list))

        if (sort_list_flag):
            sortted_combined_list = (sorted(flat_list,key=lambda x :(int(x.split('-')[0]),int(x.split('-')[1]),int(x.split('-')[2]))))
            flat_list  = sortted_combined_list

        return flat_list

def clean_distribution_list(distribution_dict,map_of_all_index_date_to_price,index_symbol):

    map_of_index = map_of_all_index_date_to_price[index_symbol]
    more_than_5_precent_set = set()
    keys = list(map_of_index.keys())
    values = list(map_of_index.values())

    for date_num in distribution_dict:

        date_index = keys.index(distribution_dict[date_num][0])

        for x in range (25) :

            if (x+date_index >= len(keys) ):
                break

            if values[x+date_index] >= values[date_index] * 1.05 :

               # debugging
               # print(str(keys[date_index]) + 'is'+ str(values[date_index]) )
               # print('because')
               # print(str( keys[x+date_index] )+ 'is' + str(values[x+date_index]))
               # print()
               # print()

                more_than_5_precent_set.add(date_num)
                break

    for day_key in more_than_5_precent_set:
        del distribution_dict[day_key]

    return distribution_dict

def get_sucess_rate_per_index(major_index_set,number_of_distribution_date_to_look_for,number_of_days_of_of_total_distribution,number_of_days_to_check_for_down,precent_down):

    map_of_all_index_date_to_price = get_yahoo_finance_historical_price_data ()

    for index_symbol in major_index_set:
        print(index_symbol)
        ma_map = get_ma_map(index_symbol, 50)
        distribution_dict = get_distribution_dict(index_symbol, ma_map)
        distribution_dict = clean_distribution_list(distribution_dict,map_of_all_index_date_to_price, index_symbol)
        final_dates_lst = sliding_window(number_of_days_of_of_total_distribution,number_of_distribution_date_to_look_for,distribution_dict)
        print(final_dates_lst)
        print('for index'+ index_symbol)
        validate_tops(number_of_days_to_check_for_down,precent_down,final_dates_lst,index_symbol,map_of_all_index_date_to_price)

def get_all_lists_combined(major_index_set,number_of_distribution_dates_to_look_for,number_of_days_of_of_total_distribution):

    list_of_all_dates_from_all_index = []
    for index_symbol in major_index_set:
        ma_map = get_ma_map(index_symbol, 50)
        distribution_list = get_distribution_dict(index_symbol, ma_map)
        final_dates_lst = sliding_window(number_of_days_of_of_total_distribution,number_of_distribution_dates_to_look_for,distribution_list)
        list_of_all_dates_from_all_index.append((final_dates_lst))

    return list_of_all_dates_from_all_index

def get_map_of_date_to_price(yahoo_stock,index_symbol):

    map_to_price = {}
    json = (yahoo_stock.get_historical_price_data('2010-01-01', '2020-10-25', 'daily'))

    for row in json[index_symbol]["prices"]:
        price_today = row['close']
        date_today = row['formatted_date']
        map_to_price[date_today] = price_today

    return map_to_price

def get_yahoo_finance_historical_price_data():

    map_of_all_index_date_to_price = {}

    nyse_map = get_map_of_date_to_price( YahooFinancials(nyse_composite_index_symbol), nyse_composite_index_symbol )
    dow_map = get_map_of_date_to_price( YahooFinancials(dow_index_symbol), dow_index_symbol )
    nasdaq_map = get_map_of_date_to_price( YahooFinancials(nasdaq_composite_symbol), nasdaq_composite_symbol )
    sp500_map = get_map_of_date_to_price( YahooFinancials(sp500_index_symbol), sp500_index_symbol )

    map_of_all_index_date_to_price[nyse_composite_index_symbol] = nyse_map
    map_of_all_index_date_to_price[dow_index_symbol] = dow_map
    map_of_all_index_date_to_price[nasdaq_composite_symbol] = nasdaq_map
    map_of_all_index_date_to_price[sp500_index_symbol] = sp500_map

    return map_of_all_index_date_to_price

def does_the_market_got_down(date,precent_down, time_after_date,index_symbol,map_of_all_index_date_to_price):

    map_of_index = map_of_all_index_date_to_price[index_symbol]

    keys = list(map_of_index.keys())
    values = list(map_of_index.values())
    date_index = keys.index(date)


    for x in range (1,time_after_date+1) :

        if (x+date_index >= len(keys) ):
            break

        if values[x+date_index] <= values[date_index] * (1-precent_down) :
            return True
    return False

    return False

def validate_tops(time_after_date, precent_down,list_of_all_dist_days,index_symbol,map_of_all_index_date_to_price):


    no_count = 0
    yes_count = 0
    for date in list_of_all_dist_days:
        if does_the_market_got_down(date,precent_down,time_after_date,index_symbol,map_of_all_index_date_to_price):
            yes_count  = yes_count + 1
        else:
            no_count  = no_count + 1
    print('sucees rate is')
    print ( yes_count /( yes_count+no_count))

    print()


def market_top_main():

    number_of_distribution_dates_to_look_for = 4
    number_of_days_of_of_total_distribution = 25
    number_of_days_to_check_for_down = 10
    precent_down = 0.02

    major_index_set = set()
    major_index_set.add(nyse_composite_index_symbol)
    major_index_set.add(dow_index_symbol)
    major_index_set.add(sp500_index_symbol)
    major_index_set.add(nasdaq_composite_symbol)

    # getting the success rate for every index
    get_sucess_rate_per_index(major_index_set,number_of_distribution_dates_to_look_for,number_of_days_of_of_total_distribution,number_of_days_to_check_for_down,precent_down)

    # combining the whole 4 index to one list than optional sort and remove duplicate
    #list_of_all_dates_from_all_index = get_all_lists_combined(major_index_set,number_of_distribution_dates_to_look_for,number_of_days_of_of_total_distribution)
    #common_elements = get_common_elemtns_from_lists(list_of_all_dates_from_all_index)
    #flat_list =  flatten_list(list_of_all_dates_from_all_index, True , True)


if __name__ == "__main__":
    market_top_main()
