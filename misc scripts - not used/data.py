import requests, csv, pandas as pd
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup as bs

print('Fetching data...')

###############################    INDIA DATA     ################################################################
url = "https://www.mohfw.gov.in/"

r = requests.get(url)

soup = bs(r.content, 'html5lib')

upd_time_str = soup.find('div',attrs={'class':'status-update'}).span.text
upd_time_str = upd_time_str[upd_time_str.find(':')+2:].replace('+','+0')
upd_time = datetime.strptime(upd_time_str,'%d %B %Y, %H:%M GMT%z')
upd_time = upd_time.astimezone(tz=timezone.utc)
upd_time_str = datetime.strftime(upd_time,'%d-%m-%Y %H:%M')

table = soup.find('div',attrs={'class':'data-table'}).find('tbody')
data = []

data_h = ['Province_State','Confirmed','Recovered','Deaths', 'Last_Update']
#data.append(data_h)

for table_row in table.findAll('tr'):
    if table_row.td.text.find("Total")!=-1:
        break
    columns = table_row.findAll('td')
    output_row = []
    output_row.append(columns[1].text)
    output_row.append(int(columns[2].text))
    output_row.append(int(columns[3].text))
    output_row.append(int(columns[4].text))
    output_row.append(upd_time_str)
    data.append(output_row)

""" with open('C:\\NRI\\COVID-19\\ind_data.csv','w',newline='') as op:
    writer = csv.writer(op)
    writer.writerows(data)
 """
data_ind = pd.DataFrame(data, columns=data_h).set_index('Province_State')
data_ind['Last_Update'] = pd.to_datetime(data_ind['Last_Update'],infer_datetime_format=True)

ind_st = pd.read_excel('C:\\NRI\\COVID-19\\Data_summary.xlsx',sheet_name='India',index_col=0, usecols=[0,5])
data_ind = data_ind.join(ind_st)
print('\tIndia Daily summary complete')

###############################    GLOBAL DATA     ################################################################
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

#data_f.to_csv('C:\\NRI\\COVID-19\\daily.csv')
print('\tGlobal Daily summary complete')

##############################    TIME SUMMARY DATA    ############################################################
url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

df = pd.read_csv(url, encoding='utf-8', index_col=False)

data = df.iloc[:, [1] + list(range(4,len(df.columns)))]

data_ts = data.melt(id_vars=['Country/Region'], var_name = 'Date', value_name='Confirmed').rename(columns={'Country/Region': 'Country_Region'})

data_ts['Date'] = pd.to_datetime(data_ts['Date'],infer_datetime_format=True)

#data_ts.to_csv('C:\\NRI\\COVID-19\\TimeSeries.csv',index=False)
print('\tGlobal Time summary complete')

##############################     OXFORD DATA      ###############################################################

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

data = pd.read_csv(url, index_col=1)

print('\tGovernment Response data complete')
print('Processing data...')

cd_lookup = pd.read_excel('C:\\NRI\\COVID-19\\Data_summary.xlsx',sheet_name='Coords',index_col=0)

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
    
    df['Age_Bin'] = pd.cut(df.Age, bins=bins, labels=labels)
    return(df)

age_data = age_data.reset_index()
age_data = age_data[age_data['Metric']!='First_Case']
age_data = age_data.groupby('Metric').apply(age_bin).set_index(['CountryCode','Metric'])
data_ox = act_data.join(age_data, how='left').reset_index(drop=False)

print('\tGovernment Response binning complete')

####################################     DOUBLING        ####################################################################

data_r = data_ts.reset_index().set_index('Country_Region').join(cd_lookup.reset_index().set_index('Country_Region')).reset_index(drop=True).set_index('CountryCode')
cnt_list=['IND','JPN','CHN','USA','GBR','ITA']
data_r = data_r.loc[cnt_list]

case_cnt = [1, 100, 1000, 2000, 4000, 6000, 10000, 20000, 40000, 80000, 150000, 300000, 600000]

def cnt_bins(df):
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
    return(df_new)

data_dr = data_r.groupby('CountryCode').apply(cnt_bins).reset_index(level=1,drop=True)
print('\tDoubling rate computation complete')

####################################     OUTPUT EXCEL    ####################################################################
print('Loading data...')
with pd.ExcelWriter('C:\\NRI\\COVID-19\\Data_Summary.xlsx') as xl:
    data_f.reset_index().to_excel(xl,'Summary', index=False, engine='xlsxwriter')
    cd_lookup.reset_index().to_excel(xl, 'Coords', index=False, engine='xlsxwriter')
    data_ts.to_excel(xl, 'Time Series',index=False, engine='xlsxwriter')
    data_ind.reset_index().to_excel(xl, 'India', index=False, engine='xlsxwriter')
    data_ox.to_excel(xl, 'Gov_Action', index=False, engine='xlsxwriter')
    data_dr.reset_index().to_excel(xl, 'Doubling', index=False, engine='xlswriter')

print('Data fetch complete')