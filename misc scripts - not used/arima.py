# %%

import pandas as pd, numpy as np
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.stattools import acf, adfuller
from statsmodels.graphics.tsaplots import plot_acf,plot_pacf
from statsmodels.tsa.arima_model import ARIMA
from matplotlib import pyplot
from sklearn.metrics import mean_squared_error as mse

conf_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
death_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
rec_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

# Confirmed cases
conf = pd.read_csv(conf_url, encoding='utf-8', index_col=1).loc['India'].iloc[3:].rename('Confirmed')
conf.index = pd.to_datetime(conf.index,format='%m/%d/%y')

# Deaths
death = pd.read_csv(death_url, encoding='utf-8', index_col=1).loc['India'].iloc[3:].rename('Deaths')
death.index = pd.to_datetime(death.index,format='%m/%d/%y')

# Recovered cases
rec = pd.read_csv(rec_url, encoding='utf-8', index_col=1).loc['India'].iloc[3:].rename('Recovered')
rec.index = pd.to_datetime(rec.index,format='%m/%d/%y')

data_df = pd.concat([conf,death,rec], axis=1, sort=True)
data_df['Active'] = data_df['Confirmed'] - data_df['Deaths'] - data_df['Recovered']
#data_df.drop(columns=['Confirmed','Deaths','Recovered'],inplace=True)
data_df['Change_A'] = data_df['Active'] - data_df['Active'].shift(1)
#data_df['Change_C'] = data_df['Confirmed'] - data_df['Confirmed'].shift(1)
data_df['Change_A'] = data_df['Change_A'].fillna(method='bfill')
#data_df['Change_C'] = data_df['Change_C'].fillna(method='bfill')
data_df = data_df.astype('int64')
X = data_df.Active.to_numpy()
# p = 17 or 18 or 19
# q = 2
# d = 1 or 2 or 3
plot_acf(X)
pyplot.show()
#plot_pacf(X, lags=40)
#pyplot.show()

"""train, test = X[0:-15],X[-15:]
#model = pm.auto_arima(train, seasonal=False)
#print(model)
#forecasts = model.predict(test.shape[0])
#x = np.arange(X.shape[0])
#pyplot.plot(x[0:-15], train, color='blue')
#pyplot.plot(x[-15:], forecasts, color='orange')
#pyplot.show()
history = list(train)
predictions = list()
for t in range(len(test)):
    model = ARIMA(train,order=(4,1,2))
    model_fit = model.fit()
    predictions.append(model_fit.forecast()[0])
    history.append(test[t])
    print(f'{t+1:0>2d}. Predicted = {predictions[-1]:.4f} Expected = {history[-1]:4f}')

error = mse(test, predictions)
print(f'Test MSE: {error:.4f}')

pyplot.plot(test, color = 'blue')
pyplot.plot(predictions, color='orange')
pyplot.show()"""

"""model = ARIMA(data_df.Active,order=(10,1,0),freq='D')
model_fit = model.fit(disp=0)
print(model_fit.summary())
residuals = pd.DataFrame(model_fit.resid)
residuals.plot()
pyplot.show()
residuals.plot(kind='kde')
pyplot.show()
print(residuals.describe())"""

# %%
