# COVID-19 Dashboard
Repository for COVID-19 Dashboards made in Tableau and associated data scripts

## List of files
### Tableau workbooks
* *NRI India COVID-19 Dashboard_STG.twbx* - Production dashboard with analytics (no prediction)
* *NRI India COVID-19 Dashboard_Pred.twbx* - Dashboard for India prediction

### Data files
* *Data_summary.xlsx* - Excel data source for *Dashboard_STG*
* *Predictions.xlsx* - Excel data source for *Dashboard_Pred*

### Data scripts
Data scripts are contained in the *./data-scripts* folder
* *data.py* - Master script to run all subscripts and push data into data files
* *capm.py* - Script to pull Capital Markets data
* *doubling.py* - Script to calculate doubling rate for countries
* *get_global_summ.py* - Script to pull Global Daily Summary from JHU CSSE
* *get_global_ts.py* - Script to pull Time Series from JHU CSSE
* *get_India.py* - Script to pull India data from MoHFW website
* *get_ox_data.py* - Script to pull Government Response data from Blavatnik School of Governance, University of Oxford
* *sigmoid.py* - Script to predict data for India
* *requirements.in* - Python requirements template for pip-tools

### Miscellaneous files
* *maps-master/States* - Map shapefiles for Indian states
* *misc scripts - not used* - Scripts used to test prediction model and miscellaneous data pulls

## Author
* Siddharth Kumar Singh
