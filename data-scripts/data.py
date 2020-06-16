# -*- coding: utf-8 -*-
#####################################
# Created on 02 May 2020            #
# Last modified on 16 June 2020     #
#                                   #
# @author: siddharth-kumar-singh    #
#####################################
# Changelog:                        
# 28-May-2020: Changed prediction o/p to Excel based on module changes
# 04-Jun-2020: cd_lookup called before modules to remove redundancy
# 15-Jun-2020: Added temporary code to adjust India data in global TS
# 15-Jun-2020: Passing TS to prediction module to reduce additional data fetch
# 16-Jun-2020: Passing summary data to two modules
#####################################
# %%
import pandas as pd, requests
from datetime import datetime, timedelta
from get_global_ts import get_global_ts
from get_ox_data import get_ox_data
from doubling import doubling
from sigmoid import get_predictions
from capm import get_capm_data

print('Fetching data...')

#### Load original coords table
cd_lookup = pd.read_excel('C:\\NRI\\COVID-19\\Data_summary.xlsx',sheet_name='Coords',index_col=0)

#### Load global summary file
base_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'
day_diff = 1
dt_str = datetime.strftime(datetime.today()-timedelta(days=day_diff),'%m-%d-%Y') + '.csv'

r = requests.get(base_url + dt_str)

while r.ok == False:
    day_diff+=1
    dt_str = datetime.strftime(datetime.today()-timedelta(days=day_diff),'%m-%d-%Y') + '.csv'
    r = requests.get(base_url + dt_str)

data = pd.read_csv(base_url + dt_str, index_col=False,usecols=[2,3,4,7,8,9],parse_dates=['Last_Update'],infer_datetime_format=True,dtype={'Confirmed':'Int64','Deaths':'Int64','Recovered':'Int64'})

#### India data
data_ind = data[data['Country_Region']=='India'].set_index('Province_State')
data_ind.drop(columns=['Country_Region'],inplace=True)
ind_st = pd.read_excel('C:\\NRI\\COVID-19\\Data_summary.xlsx',sheet_name='India',index_col=0, usecols=[0,5])
data_ind = data_ind.join(ind_st)
print('\tIndia Daily summary complete')

#### Global Daily summary
data_f = data.iloc[:,1:].groupby('Country_Region').agg(
        Last_Update = ('Last_Update','max'),
        Confirmed = ('Confirmed','sum'),
        Deaths = ('Deaths','sum'),
        Recovered = ('Recovered','sum'))

data_f.sort_index(inplace=True)
print('\tGlobal Daily summary complete')

#### Time Summary data
ind_tot = data_ind.Confirmed.sum()
data_ts = get_global_ts(ind_tot)
print('\tGlobal Time summary complete')

#### Oxford Data
data_ox = get_ox_data(data_ts, cd_lookup)
print('\tGovernment Response binning complete')

#### Doubling rate calculation
data_dr = doubling(data_ts, cd_lookup)
print('\tDoubling rate computation complete')

#### Predictions data
data_pred = get_predictions(data_ts[data_ts['Country_Region']=='India'].iloc[:,1:])
print('\tPrediction computation complete')

#### Capital markets data
print('Getting capital markets data...')
data_capm_idx, data_capm_idx2, data_capm_scrips = get_capm_data()

#### Write to excel
print('Loading data...')
with pd.ExcelWriter('C:\\NRI\\COVID-19\\Data_Summary.xlsx') as xl:
    data_f.reset_index().to_excel(xl,'Summary', index=False)
    cd_lookup.reset_index().to_excel(xl, 'Coords', index=False)
    data_ts.to_excel(xl, 'Time Series',index=False)
    data_ind.reset_index().to_excel(xl, 'India', index=False)
    data_ox.to_excel(xl, 'Gov_Action', index=False)
    data_dr.reset_index().to_excel(xl, 'Doubling', index=False)
    data_capm_idx.to_excel(xl,'Indices',index=False)
    data_capm_idx2.to_excel(xl,'Sectoral',index=False)
    data_capm_scrips.to_excel(xl,'Scrips',index=False)
    
with pd.ExcelWriter('C:\\NRI\\COVID-19\\Predictions.xlsx') as xl:
    data_pred.to_excel(xl,'Predictions', index=False)

print('Data fetch complete')