from heapq import heappush, heappop
import os.path


class AcceleratedStock:

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


class GrowthStock:

    def __init__(self, symbol, eps, eps_growth):
        self.symbol = symbol
        self.eps = eps
        self.eps_growth = eps_growth

    def __str__(self):
        """
        return str.format("{}, eps_growth: {}, eps: {}", self.symbol, self.eps_growth, self.eps)
        """
        return str.format("{}, eps_growth: {}", self.symbol, self.eps_growth)

    def __lt__(self, other):
        return other.eps_growth[-1] < self.eps_growth[-1]

    def __gt__(self, other):
        return other.__lt__(self)

    def __eq__(self, other):
        return self.eps_growth[-1] == other.eps_growth[-1]

    def __ne__(self, other):
        return not self.__eq__(other)


class StocksRater:
    total_quarters = 4
    quarters_to_follow_growth = 3
    quarters_to_follow_acceleration = 2
    income = 'net_income_growth'
    eps = 'eps_growth'
    sales = 'sales_growth'
    growth_threshold = 35
    delimiters = ['"', '%', ',']

    def __init__(self, stocks_info_file, acceleration_stocks_file, growth_stocks_file):
        self.growth_stocks_heap = []
        self.acceleration_stocks_heap = []
        self.stocks_info_file = stocks_info_file
        self.acceleration_stocks_file = acceleration_stocks_file
        self.growth_stocks_file = growth_stocks_file

    def calc_top_stocks(self):
        if not os.path.exists(self.stocks_info_file):
            print("{} does not exist".format(self.stocks_info_file))
            return

        with open(self.stocks_info_file, 'r') as top_stocks:
            for line in top_stocks:
                if not line:
                    continue

                stock_symbol = line.split()[0]
                eps_list = StocksRater.get_data_list(line, StocksRater.eps, 1, StocksRater.sales, 0)
                income_list = StocksRater.get_data_list(line, StocksRater.income, 1, StocksRater.eps, 0)
                sales_list = StocksRater.get_data_list(line, StocksRater.eps, 1, StocksRater.sales, 1)

                accelerated_stock = StocksRater.get_accelerated_stock(stock_symbol, eps_list, income_list, sales_list)
                if accelerated_stock:
                    heappush(self.acceleration_stocks_heap, accelerated_stock)

                growth_stock = StocksRater.get_growth_stock(stock_symbol, eps_list)
                if growth_stock:
                    heappush(self.growth_stocks_heap, growth_stock)

    @staticmethod
    def get_data_list(line, first_delimiter, after_first_delimiter, second_delimiter, after_second_delimiter):
        if not line:
            return None
        data_list = []
        data_as_string = line.split(first_delimiter)[after_first_delimiter].split(second_delimiter)[after_second_delimiter]
        start_index = data_as_string.find('[')
        end_index = data_as_string.find(']')
        if end_index > start_index + 1:
            data_as_string_list = data_as_string[start_index:(end_index + 1)].strip('][').split(', ')
            data_list = StocksRater.get_data_list_as_numbers(data_as_string_list)
        return data_list

    @staticmethod
    def get_data_list_as_numbers(data_as_string_list):
        data_list = []
        for data_as_string in data_as_string_list:
            data_as_number = StocksRater.get_data_as_number(data_as_string)
            if data_as_number is None:
                return None
            else:
                data_list.append(data_as_number)
        return data_list

    @staticmethod
    def get_data_as_number(data_as_string):
        try:
            for delimiter in StocksRater.delimiters:
                data_as_string = data_as_string.replace(delimiter, '')
            return float(data_as_string)
        except ValueError:
            return None

    @staticmethod
    def get_accelerated_stock(stock_symbol, eps_list, income_list, sales_list):
        if not eps_list or not income_list or not sales_list:
            return None

        eps_acceleration = StocksRater.calc_acceleration(eps_list)
        income_acceleration = StocksRater.calc_acceleration(income_list)
        sales_acceleration = StocksRater.calc_acceleration(sales_list)
        if not eps_acceleration or not income_acceleration or not sales_acceleration:
            return None

        return AcceleratedStock(stock_symbol, eps_list, eps_acceleration, income_list, income_acceleration, sales_list,
                                sales_acceleration)

    @staticmethod
    def calc_acceleration(data_list):
        if not data_list:
            return None

        acceleration = []
        for quarter in range(StocksRater.quarters_to_follow_acceleration * (-1), 0):
            q_acceleration = data_list[quarter]
            if q_acceleration <= 0 or (acceleration and q_acceleration <= acceleration[-1]):
                return None
            else:
                acceleration.append(q_acceleration)

        return acceleration

    @staticmethod
    def get_growth_stock(stock_symbol, eps_list):
        if not eps_list:
            return None

        eps_growth = StocksRater.calc_growth(eps_list)
        if not eps_growth:
            return None

        return GrowthStock(stock_symbol, eps_list, eps_growth)

    @staticmethod
    def calc_growth(data_list):
        if not data_list:
            return None

        growth = []
        for quarter in range(StocksRater.quarters_to_follow_growth * (-1), 0):
            q_growth = data_list[quarter]
            if q_growth < StocksRater.growth_threshold:
                return None
            else:
                growth.append(q_growth)

        return growth

    def write_accelerated_stocks_to_file(self):
        StocksRater.write_stocks_to_file(self.acceleration_stocks_file, self.acceleration_stocks_heap)

    def write_growth_stocks_to_file(self):
        StocksRater.write_stocks_to_file(self.growth_stocks_file, self.growth_stocks_heap)

    @staticmethod
    def write_stocks_to_file(stocks_file, heap):
        if os.path.exists(stocks_file):
            with open(stocks_file, 'r+') as f:
                f.truncate(0)  # need '0' when using r+

        with open(stocks_file, 'a') as top_stocks:
            while heap:
                top_stocks.write(str(heappop(heap)) + '\n')


def rate_stocks(stocks_info_file, acceleration_stocks_file, growth_stocks_file):
    rater = StocksRater(stocks_info_file, acceleration_stocks_file, growth_stocks_file)
    rater.calc_top_stocks()
    rater.write_accelerated_stocks_to_file()
    rater.write_growth_stocks_to_file()


def main():
    rate_stocks("stock_db.txt", "acceleration_stocks.txt", "growth_stocks.txt")


if __name__ == "__main__":
    main()
