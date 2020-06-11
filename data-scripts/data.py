# -*- coding: utf-8 -*-
#####################################
# Created on 02 May 2020            #
# Last modified on 04 June 2020     #
#                                   #
# @author: siddharth-kumar-singh    #
#####################################
# Changelog:                        
# 28-May-2020: Changed prediction o/p to Excel based on module changes
# 04-Jun-2020: cd_lookup called before modules to remove redundancy
#####################################
import pandas as pd
from get_India import get_India_data
from get_global_summ import get_global_summary
from get_global_ts import get_global_ts
from get_ox_data import get_ox_data
from doubling import doubling
from sigmoid import get_predictions
from capm import get_capm_data

print('Fetching data...')

#### Load original coords table
cd_lookup = pd.read_excel('C:\\NRI\\COVID-19\\Data_summary.xlsx',sheet_name='Coords',index_col=0)

#### India data
data_ind = get_India_data()
print('\tIndia Daily summary complete')

#### Global Daily summary
data_f = get_global_summary(data_ind)
print('\tGlobal Daily summary complete')

#### Time Summary data
data_ts = get_global_ts()
print('\tGlobal Time summary complete')

#### Oxford Data
data_ox = get_ox_data(data_ts, cd_lookup)
print('\tGovernment Response binning complete')

#### Doubling rate calculation
data_dr = doubling(data_ts, cd_lookup)
print('\tDoubling rate computation complete')

#### Predictions data
data_pred = get_predictions()
print('\tPrediction computation complete')

#### Capital markets data
print('Getting capital markets data...')
data_capm_idx, data_capm_idx2, data_capm_scrips = get_capm_data()

#### Write to excel
print('Loading data...')
with pd.ExcelWriter('C:\\NRI\\COVID-19\\Data_Summary.xlsx') as xl:
    data_f.reset_index().to_excel(xl,'Summary', index=False)
    cd_lookup.reset_index().to_excel(xl, 'Coords', index=False)
    data_ts.to_excel(xl, 'Time Series',index=False)
    data_ind.reset_index().to_excel(xl, 'India', index=False)
    data_ox.to_excel(xl, 'Gov_Action', index=False)
    data_dr.reset_index().to_excel(xl, 'Doubling', index=False)
    data_capm_idx.to_excel(xl,'Indices',index=False)
    data_capm_idx2.to_excel(xl,'Sectoral',index=False)
    data_capm_scrips.to_excel(xl,'Scrips',index=False)
    
with pd.ExcelWriter('C:\\NRI\\COVID-19\\Predictions.xlsx') as xl:
    data_pred.to_excel(xl,'Predictions', index=False)

print('Data fetch complete')