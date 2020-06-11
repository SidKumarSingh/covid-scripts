# %%

import pandas as pd

def find_dt(df, arglist):
    df_app = {'Metric':[], 'Date':[]}
    for arg in arglist:
        df_app['Metric'].append(arg['res_col'])
        dt = 0
        for idx in df.index:
            if df[arg['cnt_col']][idx]>0:
                dt = df[arg['dt_col']][idx]
                break
        df_app['Date'].append(dt)
    df_new = pd.DataFrame.from_dict(df_app)
    df_new['Date'] = pd.to_datetime(df_new['Date'],errors='coerce',format=arg['dt_format'])
    return(df_new)

url = 'https://oxcgrtportal.azurewebsites.net/api/CSVDownload'

data = pd.read_csv('C:\\NRI\\COVID-19\\OxCGRT.csv', index_col=1)

print('\tGovernment Response data complete')
print('Processing data...')

cd_lookup = pd.read_excel('C:\\NRI\\COVID-19\\Data_summary.xlsx',sheet_name='Coords',index_col=0)

data_ts = pd.read_excel('C:\\NRI\\COVID-19\\Data_summary.xlsx','Time Series', index=False)

ts = data_ts.sort_values(['Country_Region','Date'])

dz = ts.groupby('Country_Region').apply(find_dt, arglist = [{'cnt_col':'Confirmed', 'dt_col':'Date', 'res_col':'First_Case', 'dt_format':'%Y-%m-%d'}])

dz = dz.join(cd_lookup['CountryCode']).set_index('CountryCode')

dz = dz[dz.index.notnull()].reindex(data.index.unique().tolist()).dropna(axis=0,how='all')

cols = [c for c in data.columns if c[-5:]!='Notes']

data = data[cols].drop(columns=['CountryName'])

cn_grp = data.loc[dz.index.unique().tolist()].reset_index().groupby('CountryCode').apply(find_dt, arglist = [
    {'cnt_col':'C1_School closing', 'dt_col':'Date', 'res_col':'School Closure', 'dt_format':'%Y%m%d'},
    {'cnt_col':'C2_Workplace closing', 'dt_col':'Date', 'res_col':'Workplace Closure', 'dt_format':'%Y%m%d'},
    {'cnt_col':'C3_Cancel public events', 'dt_col':'Date', 'res_col':'Cancel Public Events', 'dt_format':'%Y%m%d'},
    {'cnt_col':'C4_Restrictions on gatherings', 'dt_col':'Date', 'res_col':'Restrictions on Gatherings', 'dt_format':'%Y%m%d'},
    {'cnt_col':'C5_Close public transport', 'dt_col':'Date', 'res_col':'Close Public Transport', 'dt_format':'%Y%m%d'},
    {'cnt_col':'C6_Stay at home requirements', 'dt_col':'Date', 'res_col':'Stay at Home Requirements', 'dt_format':'%Y%m%d'},
    {'cnt_col':'C7_Restrictions on internal movement', 'dt_col':'Date', 'res_col':'Restrictions on Internal Movement', 'dt_format':'%Y%m%d'},
    {'cnt_col':'C8_International travel controls', 'dt_col':'Date', 'res_col':'International Travel Controls', 'dt_format':'%Y%m%d'},
    {'cnt_col':'E1_Income support', 'dt_col':'Date', 'res_col':'Income Support', 'dt_format':'%Y%m%d'},
    {'cnt_col':'E2_Debt/contract relief', 'dt_col':'Date', 'res_col':'Debt/Contract Relief', 'dt_format':'%Y%m%d'},
    {'cnt_col':'E3_Fiscal measures', 'dt_col':'Date', 'res_col':'Fiscal Measures', 'dt_format':'%Y%m%d'},
    {'cnt_col':'E4_International support', 'dt_col':'Date', 'res_col':'International Support', 'dt_format':'%Y%m%d'},
    {'cnt_col':'H1_Public information campaigns', 'dt_col':'Date', 'res_col':'Public Information Campaigns', 'dt_format':'%Y%m%d'},
    {'cnt_col':'H2_Testing policy', 'dt_col':'Date', 'res_col':'Testing Policy', 'dt_format':'%Y%m%d'},
    {'cnt_col':'H3_Contact tracing', 'dt_col':'Date', 'res_col':'Contact Tracing', 'dt_format':'%Y%m%d'},
    {'cnt_col':'H4_Emergency investment in healthcare', 'dt_col':'Date', 'res_col':'Emergency investment in Healthcare', 'dt_format':'%Y%m%d'},
    {'cnt_col':'H5_Investment in vaccines', 'dt_col':'Date', 'res_col':'Investment in Vaccines', 'dt_format':'%Y%m%d'}    
]).reset_index(level=1,drop=True)

act_data = pd.concat([dz,cn_grp])

def get_age(df):
    df_app = {'Metric':[], 'Age':[]}
    for row in df.itertuples():
        if row.Metric == 'First_Case':
            continue
        else:
            df_app['Metric'].append(row.Metric)
            df_app['Age'].append(1000 if row.Date is pd.NaT else (row.Date - df[df.Metric == 'First_Case'].iloc[0,1]).days)
    df_new = pd.DataFrame.from_dict(df_app)
    return(df_new)

age_data = act_data.groupby('CountryCode').apply(get_age).reset_index(level=1,drop=True).set_index('Metric', append=True)
act_data.set_index('Metric', append='True', inplace=True)

def age_bin(df):
    s_min = df.Age.agg('min')
    s_max = pd.Series(df.Age.unique()).nlargest(2).iloc[1]
    boundary = [0, 1, 3, 7, 10, 15, 20, 45]
    bins = []
    labels = []
    if s_min < 0:
        bins.append(s_min)
        labels.append(f'{s_min}' + ' - 0')
    i = 0
    while i < len(boundary) and boundary[i] < s_max:
        bins.append(boundary[i])
        if boundary[i] == 45:
            labels.append('45 - ' + f'{s_max}')
        else:
            labels.append(f'{boundary[i]}' + ' - ' + f'{boundary[i+1]}')
        i += 1
    bins.append(s_max)
    bins.append(1000)
    labels.append('No data')
    print(labels)
    df['Age_Bin'] = pd.cut(df.Age, bins=bins, labels=labels)
    return(df)

age_data = age_data.reset_index()
age_data = age_data[age_data['Metric']!='First_Case']
age_data = age_data.groupby('Metric').apply(age_bin).set_index(['CountryCode','Metric'])

data_ox = act_data.join(age_data, how='left').reset_index(drop=False)

#print(data_ox)

print('\tGovernment Response binning complete')

# %%
