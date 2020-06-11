# -*- coding: utf-8 -*-
#####################################
# Created on 02 May 2020            #
# Last modified on 04 June 2020     #
#                                   #
# @author: siddharth-kumar-singh    #
#####################################
# Changelog:                        
# 04-Jun-2020: Added doubling buckets for 1mn+
#####################################
# %%
import pandas as pd

def __cnt_bins(df, case_cnt):
    cnt = {'nbin':[], 'age':[]}
    i = 0
    dt = 0
    for row in df.itertuples():
        r = 1
        while i < len(case_cnt) and r == 1:
            if row.Confirmed >= case_cnt[i]:
                cnt['nbin'].append(case_cnt[i])
                cnt['age'].append(0 if i == 0 else (row.Date - dt).days)
                dt = row.Date
                i += 1
                r = 0
            else:
                break
    df_new = pd.DataFrame.from_dict(cnt)
    return df_new

def doubling(data_ts, cd_lookup):
    data_r = data_ts.reset_index().set_index('Country_Region').join(cd_lookup.reset_index().set_index('Country_Region')).reset_index(drop=True).set_index('CountryCode')
    cnt_list=['IND','JPN','CHN','USA','GBR','ITA']
    data_r = data_r.loc[cnt_list]

    case_cnt = [1, 100, 1000, 2000, 4000, 6000, 10000, 20000, 40000, 80000, 150000, 300000, 600000, 1000000, 2000000]

    data_dr = data_r.groupby('CountryCode').apply(__cnt_bins,case_cnt).reset_index(level=1,drop=True)
    return data_dr

cd_lookup = pd.read_excel('C:\\NRI\\COVID-19\\Data_summary.xlsx',sheet_name='Coords',index_col=0)
data_ts = pd.read_excel('C:\\NRI\\COVID-19\\Data_summary.xlsx',sheet_name='Time Series', index_col=False)
doubling(data_ts,cd_lookup)

# %%
