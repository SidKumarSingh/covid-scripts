# -*- coding: utf-8 -*-
#####################################
# Created on 13 May 2020            #
# Modified on 18 August 2020        #
#                                   #
# @author: siddharth-kumar-singh    #
#####################################
# Changelog:                        
# 18-Aug-2020: Modified code for BSE sectoral indices
#####################################
# %%
import pandas as pd, numpy as np, math, time, requests as req, io
from datetime import datetime, timedelta

def get_capm_data():
    period2 = math.floor((datetime.now() - timedelta(days=1) - datetime(1970,1,1)).total_seconds())
    sym_list = pd.read_excel('C:\\NRI\\COVID-19\\sym_list.xlsx', 'sym_list', index_col=0, usecols=[0,1,2,14], dtype='str')
    idx_list = sym_list[sym_list['Type']=='I'].iloc[:,0:1]
    i2_list = sym_list[sym_list['Type']=='I2'].iloc[:,0:1]
    scrip_list = sym_list[sym_list['Type']=='S']

    ###### Index data
    idx_data = pd.DataFrame()

    for idx in idx_list.index:
        time.sleep(1)
        period2 += 86400 if idx_list['Name'].loc[idx] == 'NASDAQ' else 0
        url = f'https://query1.finance.yahoo.com/v7/finance/download/{idx}?period1=1580515200&period2={period2}&interval=1d&events=history'
        s = pd.read_csv(url,index_col=0, infer_datetime_format=True, usecols=[0,4], squeeze=True, dtype=np.float64, parse_dates=[0],encoding='utf-8')
        df = pd.DataFrame(s, columns=['Close'])
        df.insert(0, column='Name',value=idx_list['Name'].loc[idx])
        idx_data = idx_data.append(df)
        period2 -= 86400 if idx_list['Name'].loc[idx] == 'NASDAQ' else 0
    idx_data = idx_data.dropna().reset_index().rename(columns={'index':'Date'})
    print('\tIndex data complete')

    ###### BSE indices data
    from_date = datetime(year=2020,month=2,day=3).strftime('%d/%m/%Y')
    to_date = datetime.today().strftime('%d/%m/%Y')
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}
    for idx in i2_list.index:
        time.sleep(1)
        url = f'http://api.bseindia.com/BseIndiaAPI/api/ProduceCSVForDate/w?strIndex={idx}&dtFromDate={from_date}&dtToDate={to_date}'
        r = req.get(url=url,headers=headers).content
        df = pd.read_csv(io.StringIO(r.decode('utf-8')), infer_datetime_format=True, index_col=0, usecols=[0,4], dtype=np.float64, parse_dates=True)
        df.dropna(axis=1,inplace=True)
        df.insert(loc=0,column='Name',value=i2_list.at[idx,'Name'])
        df = df.reset_index().rename(columns={'index':'Date','Date':'Close'})
        df = df.astype({'Close':np.float64})
        idx_data = idx_data.append(df,ignore_index=True)
    print('\tBSE Sectoral Indices data complete')

    to_date = datetime.today() - timedelta(days=1)
    from_date = datetime.today() - timedelta(weeks=5)
    mask = (idx_data['Date']>=from_date) & (idx_data['Date']<=to_date)
    i2_data = idx_data.loc[mask].rename(columns={'Name':'Index'}).reset_index(drop=True)
    
    ###### Scrips data
    period1 = math.floor((datetime.now() - timedelta(days=7) - datetime(1970,1,1)).total_seconds())
    period2 = math.floor((datetime.now() - datetime(1970,1,1)).total_seconds())
    data = {'Name':[],'Change':[],'Mapping':[]}
    for idx in scrip_list.index:
        time.sleep(1)
        url = f'https://query1.finance.yahoo.com/v7/finance/download/{idx}?period1={period1}&period2={period2}&interval=1d&events=history'
        try:
            s = pd.read_csv(url,index_col=0, infer_datetime_format=True, usecols=[0,4], squeeze=True, dtype=np.float64, parse_dates=[0],encoding='utf-8')
        except:
            print(idx)
            continue
        delta = (s.iloc[-1]/s.iloc[0]) - 1
        data['Name'].append(scrip_list.at[idx,'Name'])
        data['Change'].append(delta)
        data['Mapping'].append(scrip_list.at[idx,'Mapping'])
    scrip_data_t = pd.DataFrame(data)
    scrip_data = pd.DataFrame()
    idx_map = ['Auto','Realty','Finance','Healthcare','FMCG','BSE','KOSPI','NASDAQ','Nikkei 225','Shanghai','FTSE 100']
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
#get_capm_data()
# %%
