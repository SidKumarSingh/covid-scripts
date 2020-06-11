# -*- coding: utf-8 -*-
#####################################
# Created on 02 May 2020            #
# Modified on 06 May 2020           #
#                                   #
# @author: siddharth-kumar-singh    #
#####################################
# %%
import pandas as pd, numpy as np
from scipy.optimize import curve_fit
from datetime import date, timedelta
from calendar import monthrange

def __gaussian(X, a, b, c): #a = max value, b = mean, c = variance
    y = a * np.exp(-0.5 * ((X-b)/np.sqrt(c))**2)
    return y

def __forecast_g(ts, f, model):
    x_dt = np.min(ts)
    act_dt = np.max(ts)
    
    preds = list()
    pred = f(0, model[0], model[1], model[2])
    preds.append(['A', int(round(pred)), 0, 0])
    i = 1
    while preds[-1][1]>0 or x_dt<=act_dt:
        pred = f(i, model[0], model[1], model[2])
        if x_dt>=act_dt:
            pred_h = pred + 1.96*np.sqrt((i+1)*model[2])
            pred_l = pred - 1.96*np.sqrt((i+1)*model[2])
            pred_l = pred_l if pred_l>0 else 0
            pred_w = pred_h - pred_l
            A_P = 'P'
        else:
            pred_l = 0
            pred_w = 0
            A_P = 'A'
        preds.append([A_P, int(round(pred)), int(round(pred_l)), int(round(pred_w))])
        i+=1
        x_dt = x_dt + timedelta(days=1)
    
    end_dt = date(year=x_dt.year,month=x_dt.month,day=monthrange(x_dt.year, x_dt.month)[1])

    while x_dt<end_dt:
        pred = pred_l = 0
        pred_w = 1.96*np.sqrt((i+1)*model[2])
        A_P = 'P'
        preds.append([A_P, int(round(pred)), int(round(pred_l)), int(round(pred_w))])
        i+=1
        x_dt = x_dt + timedelta(days=1)

    index = pd.date_range(start=np.min(ts), end=end_dt, freq='D')

    dtf = pd.DataFrame(np.array(preds), index=index, columns=['A_P','forecast', 'forecast_lower', 'forecast_band'])
    return dtf

def get_predictions():
    conf_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

    # Confirmed cases
    conf = pd.read_csv(conf_url, encoding='utf-8', index_col=1).loc['India'].iloc[3:-1].rename('Confirmed')
    #conf = conf.iloc[0:-1]
    conf.index = pd.to_datetime(conf.index,format='%m/%d/%y')

    data_df = pd.DataFrame(conf) #pd.concat([conf,death,rec], axis=1, sort=True)
    data_df['Change'] = data_df['Confirmed'] - data_df['Confirmed'].shift(1)
    data_df['Change'] = data_df['Change'].fillna(method='bfill')
    data_df = data_df.astype('int64')

    maxfev = 2400

    gaussian_model,_ = curve_fit(__gaussian,
        xdata=np.arange(len(data_df['Change'])),
        ydata=data_df['Change'].to_numpy(),
        maxfev=maxfev,
        p0=[np.max(data_df['Change']),np.mean(data_df['Change']),np.var(data_df['Change'])])

    #print(gaussian_model)

    pred_x = __forecast_g(data_df['Change'].index, __gaussian, gaussian_model)
    
    data_final = pd.concat([data_df,pred_x.rename(columns={'forecast':'Change_A','forecast_lower':'Change_L','forecast_band':'Change_W'})],axis=1)
    data_final['Change'] = data_final['Change'].fillna(0)
    data_final['Confirmed'] = data_final['Confirmed'].fillna(0)    
    data_final = data_final.astype({'Confirmed':'int64','Change': 'int64', 'Change_A':'int64','Change_L':'int64','Change_W':'int64'})
    for i in range(len(data_final)):
        if data_final['A_P'].iloc[i] == 'P':
            data_final['Confirmed'].iloc[i] = data_final['Confirmed'].iloc[i-1] + data_final['Change_A'].iloc[i]

    return data_final
get_predictions()#.to_csv('C:\\NRI\\COVID-19\\pred.csv')
# %%
