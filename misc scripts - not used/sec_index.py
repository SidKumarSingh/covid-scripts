# %%

# Sensex,Auto,Realty,Finance,Healthcare,FMCG
import pandas as pd
from datetime import date

sym_list = pd.read_excel('C:\\NRI\\COVID-19\\sym_list.xlsx', 'sym_list', index_col=0, usecols=[0,1,2,9], dtype='str')
i2_list = sym_list[sym_list['Type']=='I2'].iloc[:,0:1]

to_date = date.today().strftime('%d/%m/%Y')
data = pd.DataFrame()

for idx in i2_list.index:
    url = f'http://api.bseindia.com/BseIndiaAPI/api/ProduceCSVForDate/w?strIndex={idx}&dtFromDate=03/02/2020&dtToDate={to_date}'
    df = pd.read_csv(url, index_col=0, infer_datetime_format=True, usecols=[0,4], squeeze=True, dtype='float', parse_dates=[0],encoding='utf-8')
    df.dropna(axis=1,inplace=True)
    df.insert(loc=0,column='Index',value=i2_list.at[idx,'Name'])
    data = data.append(df)
data = data.reset_index().rename(columns={'index':'Date','Date':'Close'})
print(data)

# %%