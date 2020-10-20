# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 19:04:33 2020

@author: User
"""

#%% import
import pandas as pd
from pandas.tseries.offsets import BDay
import numpy as np 

#%% initialization 

data_close = pd.read_pickle(r"C:\Work\Elior_personal\Projj\Temp_WIP\close_history.pkl")
data_open = pd.read_pickle(r"C:\Work\Elior_personal\Projj\Temp_WIP\open_history.pkl")
data_high = pd.read_pickle(r"C:\Work\Elior_personal\Projj\Temp_WIP\high_history.pkl")
data_low = pd.read_pickle(r"C:\Work\Elior_personal\Projj\Temp_WIP\low_history.pkl")

important_stocks = ['bill','wtrh','lazy','meli','cvet','clw','wms','RGEN','amrk','futu','cwh','unfi','hov','sam','snps','bmch','shw','clgx','ssd','dhi','wst']
important_stocks = [x.upper() for x in important_stocks]
data_high_imp = data_high.loc[:,important_stocks]
data_low_imp = data_low.loc[:,important_stocks]

start_date = '2019-10-01'
end_date = '2020-10-15'

#%% date filter 
def date_filter(df, start_date,end_date,date_col = 'index'):
    if(type(date_col)==str):
        if(date_col == 'index'):
            df = df.reset_index(level=0)
            date_col = df.columns[0]
        
    mask = (df[date_col] >= start_date) & (df[date_col] <= end_date)
    return(df.loc[mask].set_index(date_col))

#%% canidate finder 

def canidate_stocks(data_low,data_high,relative_change = 0.2,relative_drop = -0.08):
    temp = {}
    change = {}
    for i in range(40):
        #temp[f'{i}'] = data_low.shift(periods=(i+1))
        temp = data_low.shift(periods=(i+1))
        change[f'{i}'] = (data_high/temp)-1
    
    #temp = data_low.shift(periods=40)
    #change = (data_high/temp )-1
    symbol = []
    dates = []
    counter = []
    
    for i in range(40):
        for indx in change[f'{i}'].columns:
            mask = change[f'{i}'].loc[:,indx] >= relative_change
            mask_remove = pd.Series(False).repeat(len(mask))
            # check if there is any drop of 8% in stock price along the way 
            for j in range(i+1):
                mask_remove = np.logical_or(change[f'{j}'].loc[:,indx].reset_index(drop=True) <= relative_drop ,mask_remove.reset_index(drop=True))
            mask = np.logical_and(mask.reset_index(drop=True),np.logical_not(mask_remove))
            dates.extend((change[f'{i}'].loc[mask.values,indx].index - BDay(i+1)).values)
            symbol.extend(pd.Series(indx).repeat(sum(mask)).values)
            counter.extend(pd.Series(i+1).repeat(sum(mask)).values)

    return(list(set(zip(symbol,dates))))

    
#%% main 

temp_high = date_filter(data_high_imp,start_date,end_date)
temp_low = date_filter(data_low_imp,start_date,end_date)

interesting = canidate_stocks(temp_low,temp_high)
interesting = pd.DataFrame(interesting)
interesting.columns = ['symbol','date']
interesting.to_csv(r"C:\Work\Elior_personal\Projj\Temp_WIP\interesting_important_lastyear.csv",index=False)
