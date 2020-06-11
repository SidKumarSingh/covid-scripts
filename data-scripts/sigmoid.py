# -*- coding: utf-8 -*-
#####################################
# Created on 02 May 2020            #
# Last modified on 01 June 2020     #
#                                   #
# @author: siddharth-kumar-singh    #
#####################################
# Changelog:                        
# 28-May-2020: Fixed SettingWithCopyWarning on data_final FOR loop at end
# 01-Jun-2020: Changed logic for c_max calculation
#####################################
# %%
import pandas as pd, numpy as np
from scipy.optimize import curve_fit
from datetime import date, timedelta
from calendar import monthrange
#from matplotlib import pyplot

def __lognorm(X, k1, k2, mu, sdev):
    X = X*k1
    A = np.exp(-0.5*((np.log(X)-mu)/sdev)**2)
    B = (X*sdev*np.sqrt(2*np.pi))
    y = k2*A/B
    return y

def __forecast_g(ts, f, model):
    x_dt = np.min(ts)
    act_dt = np.max(ts)

    preds = list()
    preds.append(['A', 0, 0, 0])
    i=1
    while preds[-1][1]>0 or x_dt<=act_dt:
        pred = f(i, model[0], model[1], model[2], model[3])
        if x_dt>=act_dt:
            pred_h = pred + 1.96*np.exp(model[3])*model[1]/np.sqrt(i)
            pred_l = pred - 1.96*np.exp(model[3])*model[1]/np.sqrt(i)
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
        pred_w = 1.96*np.exp(model[3])*model[1]/np.sqrt(i)
        A_P = 'P'
        preds.append([A_P, int(round(pred)), int(round(pred_l)), int(round(pred_w))])
        i+=1
        x_dt = x_dt + timedelta(days=1)

    index = pd.date_range(start=np.min(ts), end=end_dt, freq='D')
    dtf = pd.DataFrame(np.array(preds),index=index, columns=['A_P','Change_A', 'Change_L', 'Change_W'])
    return dtf

def get_predictions():
    conf_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

    # Confirmed cases
    conf = pd.read_csv(conf_url, encoding='utf-8', index_col=1).loc['India'].rename('Confirmed').iloc[3:]
    conf.index = pd.to_datetime(conf.index,format='%m/%d/%y')

    data_df = pd.DataFrame(conf)
    data_df['Change'] = data_df['Confirmed'] - data_df['Confirmed'].shift(1)
    data_df['Change'] = data_df['Change'].fillna(method='bfill')
    data_df = data_df.astype('int64')

    #maxfev = int(1e3)
    lognorm_model,_ = curve_fit(__lognorm,
        xdata=np.arange(len(data_df['Change']))[-25:],
        ydata=data_df['Change'].to_numpy()[-25:],
        #maxfev = maxfev,
        p0=[0.2,4000,3.5,0.3],
        bounds=(0, np.array([1,10000,10,1])))
    
    pred_x = __forecast_g(data_df['Change'].index, __lognorm, lognorm_model)
    c_max = (pred_x['Change_L'].astype('int32') + pred_x['Change_W'].astype('int32')).max()
    pred_xp = pred_x[pred_x['A_P']=='P']
    for i in range(len(pred_xp)):
        if int(pred_xp['Change_A'].iloc[i])/c_max<=0.03:
            l97_dt = pred_xp.index[i]
            r = i+1
            break
    for i in range(r,len(pred_xp)):
        if int(pred_xp['Change_A'].iloc[i])/c_max<=0.01:
            l99_dt = pred_xp.index[i]
            r = i+1
            break
    for i in range(r,len(pred_xp)):
        if int(pred_xp['Change_A'].iloc[i])==0:
            l_dt = pred_xp.index[i]
            r = i+1
            break
    
    d = {'Ref':[int(round(c_max*0.5)),int(round(c_max*0.3)),int(round(c_max*0.5))],'Mark':[f'End 97% on\n{l97_dt.strftime("%d %B %Y")}',f'End 99% on\n{l99_dt.strftime("%d %B %Y")}',f'No new cases on\n{l_dt.strftime("%d %B %Y")}']}
    pred_final = pd.DataFrame(data=d, index=[l97_dt, l99_dt, l_dt])

    data_final = pd.concat([data_df,pred_x,pred_final],axis=1)
    data_final['Change'] = data_final['Change'].fillna(0)
    data_final['Ref'] = data_final['Ref'].fillna(0)
    data_final['Confirmed'] = data_final['Confirmed'].fillna(0)    
    data_final = data_final.astype({'Confirmed':'int64','Change': 'int64', 'Change_A':'int64','Change_L':'int64','Change_W':'int64','Ref':'int64'})
    data_final = data_final.reset_index().rename(columns={'index':'Date'})
    for i in range(len(data_final)):
        if data_final['A_P'].iloc[i] == 'P':
            data_final.at[i,'Confirmed'] = data_final['Confirmed'].iloc[i-1] + data_final['Change_A'].iloc[i]
    return data_final

get_predictions().to_excel('C:\\NRI\\COVID-19\\Predictions.xlsx',sheet_name='Predictions',index=False)
# %%
