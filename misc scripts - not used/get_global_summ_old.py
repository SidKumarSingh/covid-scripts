# -*- coding: utf-8 -*-
#####################################
# Created on 02 May 2020            #
#                                   #
# @author: siddharth-kumar-singh    #
#####################################
import requests, pandas as pd
from datetime import datetime, timedelta

def get_global_summary(data):
    data_f = data.groupby('Country_Region').agg(
        Last_Update = ('Last_Update','max'),
        Confirmed = ('Confirmed','sum'),
        Deaths = ('Deaths','sum'),
        Recovered = ('Recovered','sum'))

    data_f.sort_index(inplace=True)
    return data_f