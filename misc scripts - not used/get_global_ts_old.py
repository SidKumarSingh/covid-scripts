# -*- coding: utf-8 -*-
#####################################
# Created on 02 May 2020            #
# Last modified on 10 June 2020     #
#                                   #
# @author: siddharth-kumar-singh    #
#####################################
# Changelog:                        
# 10-Jun-2020: Added logic to aggregate provinces of countries
#####################################
# %%
import pandas as pd 

def get_global_ts():
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

    df = pd.read_csv(url, encoding='utf-8', index_col=False)

    data = df.iloc[:, [1] + list(range(4,len(df.columns)))]

    data_ts = data.melt(id_vars=['Country/Region'], var_name = 'Date', value_name='Confirmed').rename(columns={'Country/Region': 'Country_Region'})

    data_ts['Date'] = pd.to_datetime(data_ts['Date'],infer_datetime_format=True)

    data_ts = data_ts.groupby(['Country_Region','Date'],as_index=False).sum()

    return data_ts

get_global_ts()

# %%
