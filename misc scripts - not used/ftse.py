# %%
import requests, pandas as pd
from bs4 import BeautifulSoup as bs

url = 'https://en.wikipedia.org/wiki/FTSE_100_Index'

r = requests.get(url)
content = bs(r.text,'html5lib')
items = content.find('table',id='constituents').tbody.find_all('tr')
data = {'Symbol':[], 'Name':[]}
#print(content.find('table',id='constituents').tbody)
for item in items:
    d = item.find_all('td')
    try:
        data['Symbol'].append(d[1].text+'.L')
        data['Name'].append(d[0].text)
    except:
        pass

df = pd.DataFrame(data)
df.to_csv('C:\\NRI\\COVID-19\\FTSE.csv',index=False)
print('Done')

# %%
