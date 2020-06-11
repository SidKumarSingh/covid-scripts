# %%
import requests, pandas as pd
from bs4 import BeautifulSoup as bs

url = 'https://indexes.nikkei.co.jp/en/nkave/index/component?idx=nk225'

r = requests.get(url)
content = bs(r.text,'html5lib')
items = content.find_all('div',class_='component-list')
data = {'Symbol':[], 'Name':[]}
for item in items:
    data['Symbol'].append(item.div.text+'.T')
    data['Name'].append(item.a.text)

df = pd.DataFrame(data)
df.to_csv('C:\\NRI\\COVID-19\\Nikkei.csv',index=False)
print('Done')

# %%
