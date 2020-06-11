# -*- coding: utf-8 -*-
#####################################
# Created on 02 May 2020            #
# Last modified on 01 June 2020     #
#                                   #
# @author: siddharth-kumar-singh    #
#####################################
# Changelog:                        
# 27-May-2020: Added tzinfo parsing for dateutil
# 30-May-2020: Modified due to change in source MoHFW website
# 01-Jun-2020: Modified code to accept unassigned cases
#####################################
# %%
import requests, pandas as pd 
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
from dateutil.tz import gettz
from bs4 import BeautifulSoup as bs

def get_India_data():
    url = "https://www.mohfw.gov.in/"

    r = requests.get(url)

    soup = bs(r.content, 'html5lib')

    upd_time_str = soup.find('div',attrs={'class':'status-update'}).span.text
    ist_tzone = gettz('Asia/Kolkata')
    tzinfo = {'IST':ist_tzone}
    upd_time_str = upd_time_str[upd_time_str.find(':')+2:upd_time_str.find('(') - 1]
    upd_time = parse(upd_time_str,tzinfos=tzinfo)
    upd_time = upd_time.astimezone(tz=timezone.utc).replace(tzinfo=None)

    table = soup.find('div',attrs={'class':'data-table'}).find('tbody')
    data = list()


    for table_row in table.findAll('tr'):
        columns = table_row.findAll('td')
        if len(columns)==6 and columns[1].text.find('Total')==-1:
            try:
                data.append([columns[1].text, int(columns[5].text.replace('#','') or 0), int(columns[3].text.replace('#','') or 0),int(columns[4].text.replace('#','') or 0), upd_time])
            except:
                continue
        else:
            continue

    data_ind = pd.DataFrame(data, columns=['Province_State','Confirmed','Recovered','Deaths', 'Last_Update']).set_index('Province_State')
    ind_st = pd.read_excel('C:\\NRI\\COVID-19\\Data_summary.xlsx',sheet_name='India',index_col=0, usecols=[0,5])
    data_ind = data_ind.join(ind_st)
    return data_ind
#get_India_data()#.to_csv('C:\\NRI\\COVID-19\\India.csv')
# %%
