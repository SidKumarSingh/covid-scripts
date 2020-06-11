# -*- coding: utf-8 -*-
#####################################
# Created on 02 May 2020            #
#                                   #
# @author: siddharth-kumar-singh    #
#####################################
# %%
import pandas as pd, numpy as np
from scipy.optimize import curve_fit
from datetime import date, timedelta
from calendar import monthrange
from scipy.stats import norm
from matplotlib import pyplot

def __logistic(X, c, k, q, v, b): #c = parameter, k = peak, q = parameter = 1, v = asymptote near max growth, b = growth rate 
    D = (c + q*np.exp(-b*X))**(1/v)
    y = k/D
    return y

def __forecast_l(ts, f, model):
    x_dt = np.min(ts)
    act_dt = np.max(ts)
    preds = list()
    a_p = list()
    preds.append([0])
    a_p.append(['A'])
    i = 0
    pred = 0
    while True:
        pred = f(i, model[0], model[1], model[2], model[3], model[4])
        preds.append([int(round(pred))])
        a_p.append(['A' if x_dt<=act_dt else 'P'])
        x_dt += timedelta(days=1)
        i += 1
        if x_dt > act_dt and np.sum(np.array(preds[-5:])) == 5*preds[-1][0]:
            break
    
    end_dt = date(x_dt.year,x_dt.month,monthrange(x_dt.year, x_dt.month)[1])

    while x_dt <= end_dt:
        preds.append([pred])
        a_p.append(['P'])
        x_dt += timedelta(days=1)
    
    index = pd.date_range(start=np.min(ts),end=end_dt)
    idx = np.arange(len(index))

    preds = np.concatenate((idx.reshape((idx.shape[0],1)),preds[1:],a_p[1:]),axis=1)

    dtf = pd.DataFrame(np.array(preds), index=index, columns=['idx','Confirmed_P','A_P']).astype({'Confirmed_P': 'float64', 'idx':'int32'})
    dtf['Confirmed_P'] = [int(round(x)) for x in dtf['Confirmed_P']]
    dtf['Change_C'] = dtf['Confirmed_P'] - dtf['Confirmed_P'].shift(1)
    dtf['Change_C'] = dtf['Change_C'].fillna(0)
    dtf.drop(columns=['Confirmed_P'])

    return dtf

def __band_calc(row,sdev):
    #print(row.Change_C)
    pred_h = int(round(row.Change_C + 1.96*sdev/np.sqrt(row.idx)))
    pred_l = int(round(row.Change_C - 1.96*sdev/np.sqrt(row.idx)))
    pred_l = pred_l if pred_l > 0 else 0
    pred_w = pred_h - pred_l
    print(pred_h, row.Change_C, pred_l, pred_w)

def get_predictions():
    conf_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

    # Confirmed cases
    conf = pd.read_csv(conf_url, encoding='utf-8', index_col=1).loc['India'].iloc[3:].rename('Confirmed')
    conf.index = pd.to_datetime(conf.index,format='%m/%d/%y')

    data_df = pd.DataFrame(conf)

    data_df['Change'] = data_df['Confirmed'] - data_df['Confirmed'].shift(1)
    data_df['Change'] = data_df['Change'].fillna(method='bfill')
    data_df = data_df.astype('int64')

    maxfev = 10000
    logistic_c,_ = curve_fit(__logistic, 
        xdata = np.arange(len(data_df['Confirmed'])), 
        ydata = data_df['Confirmed'].to_numpy(),
        maxfev=maxfev, 
        p0=[1,np.max(data_df['Confirmed']),1,0.1,1])

    pred = __forecast_l(data_df['Confirmed'].index, __logistic, logistic_c)

    pred['Change_L'] = pred['Change_W'] = 0

    pred_P = pred[pred['A_P']=='P'].apply(__band_calc,axis=1, args=[pred['Change_C'].std(axis=0)])

    """pyplot.plot(np.array(pred.index),np.array(pred['Change_C']))
    pyplot.show()
    
    data_final = pd.concat([data_df,pred],axis=1)
    data_final.to_csv('C:\\NRI\\COVID-19\\pred.csv')"""

    """data_final = pd.concat(
        [data_final,
        pred_x.rename(columns={'forecast':'Change_A','forecast_lower':'Change_L','forecast_band':'Change_W'})],
        axis=1)
    
    data_final['Change'] = data_final['Change'].fillna(0)
    data_final = data_final.astype({'Change': 'int64', 'Change_A':'int64','Change_L':'int64','Change_W':'int64'})
    
    return data_final"""

get_predictions()

# %%
