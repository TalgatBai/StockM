from yahoofinancials import YahooFinancials
import datetime
import pytz

def is_market_open(nyc_datetime):
    
   if (nyc_datetime.hour < 8 ) or (nyc_datetime.hour > 16 ) :
        return False
   
   if (nyc_datetime.hour == 8 ) and (nyc_datetime.minute < 30 ) :
        return False
        
   if (nyc_datetime.hour == 16 ) and (nyc_datetime.minute > 0 ) :
        return False
   
   return True
   
def get_relative_time_precentage(nyc_datetime) :
    
    time_of_nasadaq_open_in_minutes = 390
    
    hour_differnce  = nyc_datetime.hour - 9 
    hour_differnce_in_minutes = hour_differnce * 60
    minutes_differnce = nyc_datetime.minute - 30
    sum_of_min_differnce = minutes_differnce + hour_differnce_in_minutes

    
    return sum_of_min_differnce / time_of_nasadaq_open_in_minutes 
    


def detect_breakout(stock, volume_threshold):
    
    is_breakout = False
    nyc_datetime = datetime.datetime.now(pytz.timezone('US/Eastern'))
    market_open_flag = is_market_open(nyc_datetime)
    
    if (market_open_flag == False ) :
        return False

    stock_current_volume = stock.get_current_volume()
    stock_3m_avg_volume = stock.get_three_month_avg_daily_volume()
    relative_time_precentage = get_relative_time_precentage(nyc_datetime)
    stock_3m_avg_relative_volume = relative_time_precentage * stock_3m_avg_volume

    if (stock_current_volume >= stock_3m_avg_relative_volume * volume_threshold):
        is_breakout =  True
    
    
    return is_breakout

def validate_stock_technically(stock):

    stock_50_ma = stock.get_50day_moving_avg()
    stock_200_ma = stock.get_200day_moving_avg()
    stock_current_price = stock.get_current_price()
    stock_yearly_low = stock.get_yearly_low()
    stock_yearly_high = stock.get_yearly_high()    


    if stock_50_ma <= stock_200_ma :
        return False
        
    if stock_current_price < stock_50_ma:
        return False
        
    if stock_yearly_low * 1.3 > stock_current_price :
        return False
                
    if stock_yearly_high * 0.75 > stock_current_price :
        return False    
    
    return True
            
def main():
    
    stock = YahooFinancials('WMS')
    print(detect_breakout(stock, 1.5))
    print(validate_stock_technically(stock))

    
if __name__== "__main__":
    main()