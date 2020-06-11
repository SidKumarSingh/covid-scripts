# -*- coding: utf-8 -*-
#####################################
# Created on 02 May 2020            #
#                                   #
# @author: siddharth-kumar-singh    #
#####################################
import requests, pandas as pd
from datetime import datetime, timedelta

def get_global_summary(data_ind):
    base_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'
    day_diff = 1
    dt_str = datetime.strftime(datetime.today()-timedelta(days=day_diff),'%m-%d-%Y') + '.csv'

    r = requests.get(base_url + dt_str)

    while r.ok == False:
        day_diff+=1
        dt_str = datetime.strftime(datetime.today()-timedelta(days=day_diff),'%m-%d-%Y') + '.csv'
        r = requests.get(base_url + dt_str)

    data = pd.read_csv(base_url + dt_str)

    data['Last_Update'] = pd.to_datetime(data['Last_Update'],infer_datetime_format=True)

    data_f = data.groupby('Country_Region').agg(
        Last_Update = ('Last_Update','max'),
        Confirmed = ('Confirmed','sum'),
        Deaths = ('Deaths','sum'),
        Recovered = ('Recovered','sum'))

    data_f.drop('India',inplace=True)

    ind_data = data_ind.copy()
    ind_data.insert(0, 'Country_Region', 'India')

    ind_row = ind_data.groupby('Country_Region').agg(
        Last_Update = ('Last_Update','max'),
        Confirmed = ('Confirmed','sum'),
        Deaths = ('Deaths','sum'),
        Recovered = ('Recovered','sum'))

    data_f = data_f.append(ind_row)
    data_f.sort_index(inplace=True)
    return data_f