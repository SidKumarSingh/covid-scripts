# -*- coding: utf-8 -*-
#####################################
# Created on 13 May 2020            #
#                                   #
# @author: siddharth-kumar-singh    #
#####################################
# %%
# Sensex,Auto,Realty,Finance,Healthcare,FMCG
import pandas as pd, numpy as np, math
from datetime import datetime, timedelta

def get_capm_data():
    period2 = math.floor((datetime.now() - datetime(1970,1,1)).total_seconds())

    sym_list = pd.read_excel('C:\\NRI\\COVID-19\\sym_list.xlsx', 'sym_list', index_col=0, usecols=[0,1,2,9], dtype='str')
    idx_list = sym_list[sym_list['Type']=='I'].iloc[:,0:1]
    i2_list = sym_list[sym_list['Type']=='I2'].iloc[:,0:1]
    scrip_list = sym_list[sym_list['Type']=='S']

    ###### Index data
    idx_data = pd.DataFrame()

    for idx in idx_list.index:
        url = f'https://query1.finance.yahoo.com/v7/finance/download/{idx}?period1=1580515200&period2={period2}&interval=1d&events=history'
        s = pd.read_csv(url,index_col=0, infer_datetime_format=True, usecols=[0,4], squeeze=True, dtype=np.float64, parse_dates=[0],encoding='utf-8')
        df = pd.DataFrame(s, columns=['Close'])
        df.insert(0, column='Name',value=sym_list['Name'].loc[idx])
        idx_data = idx_data.append(df)
    idx_data = idx_data.dropna().reset_index().rename(columns={'index':'Date'})
    print('\tIndex data complete')

    ###### BSE indices data
    to_date = datetime.today().strftime('%d/%m/%Y')
    from_date = (datetime.today() - timedelta(weeks=5)).strftime('%d/%m/%Y')
    i2_data = pd.DataFrame()

    for idx in i2_list.index:
        url = f'http://api.bseindia.com/BseIndiaAPI/api/ProduceCSVForDate/w?strIndex={idx}&dtFromDate={from_date}&dtToDate={to_date}'
        df = pd.read_csv(url, index_col=0, infer_datetime_format=True, usecols=[0,4], squeeze=True, dtype=np.float64, parse_dates=[0],encoding='utf-8')
        df.dropna(axis=1,inplace=True)
        df.insert(loc=0,column='Index',value=i2_list.at[idx,'Name'])
        i2_data = i2_data.append(df)
    i2_data = i2_data.reset_index().rename(columns={'index':'Date','Date':'Close'})
    print('\tBSE Sectoral Indices data complete')
    
    ###### Scrips data
    period1 = math.floor((datetime.now() - timedelta(days=7) - datetime(1970,1,1)).total_seconds())
    data = {'Name':[],'Change':[],'Mapping':[]}
    for idx in scrip_list.index:
        url = f'https://query1.finance.yahoo.com/v7/finance/download/{idx}?period1={period1}&period2={period2}&interval=1d&events=history'
        try:
            s = pd.read_csv(url,index_col=0, infer_datetime_format=True, usecols=[0,4], squeeze=True, dtype=np.float64, parse_dates=[0],encoding='utf-8')
        except:
            print(idx)
            break
        delta = (s.iloc[-1]/s.iloc[0]) - 1
        data['Name'].append(scrip_list.at[idx,'Name'])
        data['Change'].append(delta)
        data['Mapping'].append(scrip_list.at[idx,'Mapping'])
    scrip_data_t = pd.DataFrame(data)
    scrip_data = pd.DataFrame()
    idx_map = ['Auto','Realty','Finance','Healthcare','FMCG','Sensex','Kospi','Nasdaq','Nikkei','Shanghai','FTSE']
    for i in range(len(idx_map)):
        df = scrip_data_t[scrip_data_t['Mapping'].str.get(i)=='1'].sort_values(by=['Change'],ascending=False)
        if df.iat[0,1]<0:
            list = [-3,-2,-1,0]
        elif df.iat[1,1]<0:
            list = [0,-2,-1,0]
        elif df.iat[-1,1]>0:
            list = [0,1,2,3]
        elif df.iat[-2,1]>0:
            list = [0,1,2,-1]
        else:
            list = [0,1,-2,-1]
        df = df.iloc[list][['Name','Change']]
        df.insert(loc=0,column='Index',value=idx_map[i])
        df.reset_index(drop=True,inplace=True)
        scrip_data = scrip_data.append(df,ignore_index=True)
        print('\tScrips data complete')
    return idx_data, i2_data, scrip_data
print(get_capm_data())
# %%
