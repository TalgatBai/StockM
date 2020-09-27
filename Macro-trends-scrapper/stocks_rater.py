from heapq import heappush, heappop
import os.path


class Stock:

    def __init__(self, symbol, eps, eps_acceleration, income, income_acceleration, sales_list, sales_acceleration):
        self.symbol = symbol
        self.eps = eps
        self.eps_acceleration = eps_acceleration
        self.income = income
        self.income_acceleration = income_acceleration
        self.sales = sales_list
        self.sales_acceleration = sales_acceleration

    def __str__(self):
        """
        return str.format("{}, eps_acceleration: {}, eps: {},"
                          ", income_acceleration: {}, income: {}"
                          ", sales_acceleration: {}, sales: {}",
                          self.symbol, self.eps_acceleration, self.eps,
                          self.income_acceleration, self.income,
                          self.sales_acceleration, self.sales)
        """
        return str.format("{}, eps_acceleration: {}, income_acceleration: {}, sales_acceleration: {}",
                          self.symbol, self.eps_acceleration, self.income_acceleration, self.sales_acceleration)

    def __lt__(self, other):
        return other.eps_acceleration[-1] < self.eps_acceleration[-1]

    def __gt__(self, other):
        return other.__lt__(self)

    def __eq__(self, other):
        return self.eps_acceleration[-1] == other.eps_acceleration[-1]

    def __ne__(self, other):
        return not self.__eq__(other)


class StocksRater:
    total_quarters = 12
    quarters_to_follow = 2
    quarters_to_look_back = 1
    income = 'net_income'
    eps = 'eps'
    sales = 'sales'
    # growth_threshold = 50

    def __init__(self, stocks_info_file, acceleration_stocks_file):
        # self.__eps_growth_stocks_heap = []
        self.__acceleration_stocks_heap = []
        self.__stocks_info_file = stocks_info_file
        self.__acceleration_stocks_file = acceleration_stocks_file

    def calc_top_stocks(self):
        if not os.path.exists(self.__stocks_info_file):
            print("{} does not exist".format(self.__stocks_info_file))
            return

        with open(self.__stocks_info_file, 'r') as top_stocks:
            for line in top_stocks:
                stock = StocksRater.__get_stock_object(line)
                if not stock:
                    continue

                heappush(self.__acceleration_stocks_heap, stock)

    @staticmethod
    def __get_stock_object(line):
        if not line:
            return None
        stock_symbol = line.split()[0]

        eps_list, eps_acceleration = StocksRater.__calc_eps_and_eps_acceleration(line)
        if not eps_list or not eps_acceleration:
            return None

        income_list, income_acceleration = StocksRater.__calc_income_and_income_acceleration(line)
        if not income_list or not income_acceleration:
            return None

        sales_list, sales_acceleration = StocksRater.__calc_sales_and_sales_acceleration(line)
        if not sales_list or not sales_acceleration:
            return None

        return Stock(stock_symbol, eps_list, eps_acceleration, income_list, income_acceleration, sales_list, sales_acceleration)

    @staticmethod
    def __calc_eps_and_eps_acceleration(line):
        eps_list = StocksRater.__get_data_list(line, StocksRater.eps, 1, StocksRater.sales, 0)
        eps_acceleration = StocksRater.__calc_acceleration(eps_list)
        return eps_list, eps_acceleration

    @staticmethod
    def __calc_income_and_income_acceleration(line):
        income_list = StocksRater.__get_data_list(line, StocksRater.income, 1, StocksRater.eps, 0)
        income_acceleration = StocksRater.__calc_acceleration(income_list)
        return income_list, income_acceleration

    @staticmethod
    def __calc_sales_and_sales_acceleration(line):
        sales_list = StocksRater.__get_data_list(line, StocksRater.eps, 1, StocksRater.sales, 1)
        sales_acceleration = StocksRater.__calc_acceleration(sales_list)
        return sales_list, sales_acceleration

    @staticmethod
    def __get_data_list(line, first_delimiter, after_first_delimiter, second_delimiter, after_second_delimiter):
        if not line:
            return None
        data_list = []
        data_as_string = line.split(first_delimiter)[after_first_delimiter].split(second_delimiter)[after_second_delimiter]
        start_index = data_as_string.find('[')
        end_index = data_as_string.find(']')
        if end_index > start_index + 1:
            data_as_string_list = data_as_string[start_index:(end_index + 1)].strip('][').split(', ')
            data_list = StocksRater.__get_data_list_as_numbers(data_as_string_list)
        return data_list

    @staticmethod
    def __get_data_list_as_numbers(data_as_string_list):
        data_list = []
        needed_quarters = (StocksRater.total_quarters - StocksRater.quarters_to_follow - StocksRater.quarters_to_look_back)
        for data_as_string in data_as_string_list:
            data_as_number = StocksRater.__get_data_as_number(data_as_string)
            if data_as_number or len(data_list) < needed_quarters:
                data_list.append(data_as_number)
            else:
                return None
        return data_list

    @staticmethod
    def __get_data_as_number(data_as_string):
        try:
            return float(data_as_string.replace(',', '')[2:-1])
        except ValueError:
            return None

    @staticmethod
    def __calc_acceleration(data_list):
        if not data_list:
            return None
        acceleration = []
        for quarter in range(StocksRater.quarters_to_follow * (-1), 0):
            curr_q = data_list[quarter]
            prev_q = data_list[quarter - StocksRater.quarters_to_look_back]
            if prev_q >= curr_q:
                return None

            q_acceleration = round(curr_q * 100, 2) if prev_q == 0 else abs(round((curr_q - prev_q) / prev_q * 100, 2))
            if acceleration and q_acceleration <= acceleration[-1]:
                return None

            acceleration.append(q_acceleration)
        return acceleration

    def write_stocks_to_file(self):
        if os.path.exists(self.__acceleration_stocks_file):
            with open(self.__acceleration_stocks_file, 'r+') as f:
                f.truncate(0)  # need '0' when using r+

        with open(self.__acceleration_stocks_file, 'a') as top_stocks:
            while self.__acceleration_stocks_heap:
                top_stocks.write(str(heappop(self.__acceleration_stocks_heap)) + '\n')


def rate_stocks(stocks_info_file, acceleration_stocks_file):
    rater = StocksRater(stocks_info_file, acceleration_stocks_file)
    rater.calc_top_stocks()
    rater.write_stocks_to_file()


def main():
    rate_stocks("stock_db.txt", "acceleration_stocks.txt")


if __name__ == "__main__":
    main()
