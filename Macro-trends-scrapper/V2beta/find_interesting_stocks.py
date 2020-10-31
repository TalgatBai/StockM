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
#data_open = pd.read_pickle(r"C:\Work\Elior_personal\Projj\Temp_WIP\open_history.pkl")
#data_high = pd.read_pickle(r"C:\Work\Elior_personal\Projj\Temp_WIP\high_history.pkl")
#data_low = pd.read_pickle(r"C:\Work\Elior_personal\Projj\Temp_WIP\low_history.pkl")

important_stocks = ['bill','wtrh','lazy','meli','cvet','clw','wms','RGEN','amrk','futu','cwh','unfi','hov','sam','snps','bmch','shw','clgx','ssd','dhi','wst']
important_stocks = [x.upper() for x in important_stocks]
#data_high_imp = data_high.loc[:,important_stocks]
#data_low_imp = data_low.loc[:,important_stocks]
data_close_imp = data_close.loc[:,important_stocks]
#data_open_imp = data_open.loc[:,important_stocks]

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

def canidate_stocks(data,relative_change = 0.2,relative_drop = -0.06):
    #temp = {}
    change = {}
    symbol = []
    dates = []
    counter = []
    for i in range(40):
        change[f'{i}'] = data.pct_change(periods=(i+1))
        for indx in change[f'{i}'].columns:
            mask = change[f'{i}'].loc[:,indx] >= relative_change
            # find start date from which the growth started 
            start = (mask[mask].index - BDay(i+1)).values
            # adjust the True/False searies to be at the start date => True in index==start_date
            mask = mask.reset_index()
            mask.loc[:,indx] =  mask.Date.isin(start)
            mask = mask.set_index('Date',drop=True)[indx]
            # create an indicator whether there was a drop of 8% during the i days untill the growth 
            # initialize all to false 
            mask_remove = pd.Series(False).repeat(len(mask)).reset_index(drop=True)
            # check if there is any drop of 8% in stock price along the way 
            for j in range(i+1):
                mask_remove = np.logical_or( (change[f'{j}'][indx].shift(periods=-(j+1)) <= relative_drop).reset_index(drop=True) ,mask_remove)
            mask = np.logical_and(mask.reset_index(drop=True),np.logical_not(mask_remove))
            dates.extend((change[f'{i}'].loc[mask.values,indx].index).values)
            symbol.extend(pd.Series(indx).repeat(sum(mask)).values)
            counter.extend(pd.Series(i+1).repeat(sum(mask)).values)

    return(list(set(zip(symbol,dates,counter))))

    
#%% main 

#temp_high = date_filter(data_high_imp,start_date,end_date)
#temp_low = date_filter(data_low_imp,start_date,end_date)

temp = date_filter(data_close_imp,start_date,end_date)

#temp = date_filter(data_close_imp,'2020-7-15','2020-10-15').iloc[:,0:3]

interesting = canidate_stocks(data=temp)
interesting = pd.DataFrame(interesting)
interesting.columns = ['symbol','date','num_days_to_cash']
interesting.to_csv(r"C:\Work\Elior_personal\Projj\Temp_WIP\interesting_important_lastyear_s.csv",index=False)

