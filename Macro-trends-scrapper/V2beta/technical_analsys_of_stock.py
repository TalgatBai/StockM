from yahoofinancials import YahooFinancials

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

    print(validate_stock_technically(stock))

    
if __name__== "__main__":
    main()