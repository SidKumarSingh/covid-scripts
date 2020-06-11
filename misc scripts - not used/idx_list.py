from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.firefox.options import Options
from pandas import DataFrame

def createHeadlessFirefox():
    options = Options()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    return browser

browser = createHeadlessFirefox()

url = 'https://www.bseindia.com/indices/IndexArchiveData.html'
browser.get(url)

Select(browser.find_element_by_id('ddlIndex')).select_by_value('SENSEX')
#sel.click()
opts = DataFrame([{'code':x.get_attribute('value'), 'name':x.text} for x in Select(browser.find_element_by_id('ddlIndex')).options[1:]])
browser.quit()

opts.to_excel('C:\\NRI\\COVID-19\\BSE_IDX.xlsx',sheet_name='IDX_List',index=False)