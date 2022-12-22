# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 11:38:33 2020

"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from bs4 import BeautifulSoup
import os, sys
import time
from urllib.parse import urljoin
import pandas as pd
import re
import numpy as np
import datetime

# base set up
start_time = datetime.datetime.now()


options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
#os.chdir("C:/Users/user/desktop/scripts/python")
#cwd = os.getcwd()
#main_dir = os.path.abspath(os.path.join(cwd, os.pardir))
#print('Main Directory:', main_dir)

chromedriver = ("C:/chromedriver_win32/chromedriver.exe")
os.environ["webdriver.chrome.driver"] = chromedriver
# browser = webdriver.Chrome(options=options, executable_path=chromedriver)

mainurl = "https://www.bunnings.com.au/our-range"

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
page = requests.get(mainurl, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')

# script start

subcat = []
for item in soup.findAll('ul', attrs={'class': 'chalkboard-menu'}):
    links = item.find_all('a')
    for link in links:
        subcat.append(urljoin(mainurl, link.get("href")))
subcat

result = pd.DataFrame()
for adrs in subcat:
#    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
#    page = requests.get(adrs, headers=headers)
#    soup = BeautifulSoup(page.content, 'html.parser')
#    pagelink = adrs
#    adrs="https://www.bunnings.com.au/our-range/storage-cleaning/cleaning/brushware-mops/indoor-brooms"
    catProd = pd.DataFrame()
    url = adrs
    browser = webdriver.Chrome(options=options, executable_path=chromedriver)
    browser.get(url)

    lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while (match == False):
        lastCount = lenOfPage
        #time.sleep(3)
        lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount == lenOfPage:
            match = True
    reached= False
    while (reached==False):
        try:
            wait = WebDriverWait(browser, 10)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#MoreProductsButton")))

            browser.find_element_by_css_selector('#MoreProductsButton').click()
            lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            match = True
            while (match == True):
                lastCount = lenOfPage
                #time.sleep(3)
                lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount == lenOfPage:
                    match = True
                    #time.sleep(3)
                    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.view-more_btn_text")))
                    browser.find_element_by_css_selector('#content-layout_inside-anchor > div.search-result__content > div > div > section > div:nth-child(4) > div > div:nth-child(2) > div > button > div.view-more_btn_text').click()
        except:
            reached=True
# grab the items
            page = browser.page_source
            soup = BeautifulSoup(page, 'html.parser')
            browser.close()

        for article in soup.findAll('article', attrs={'class':'product-list__item hproduct special-order-product'}):
            for product in article.findAll('img', attrs={'class': 'photo'}):
                pName = product['alt']
                pCat = adrs
                pID = article['data-product-id']
                temp= pd.DataFrame({'proID':[pID],'Product':[pName],'Category':[pCat]})
                #catProd=catProd.append(temp)
                result = result.append(temp)
        #time.sleep(3)
        result.head()

result.reset_index(drop=True)

#writes to CSV
writer = pd.ExcelWriter('C:/test.xlsx')
result.to_excel(writer,'Sheet1', index=False)
writer.save()

finish_time = datetime.datetime.now()
duration = finish_time - start_time

dur_list = str(duration).split(':')
hour = dur_list[0]
minutes = dur_list[1]
seconds = dur_list[2].split('.')[0]

print ('Duration: %s Hours, %s Minutes, %s Seconds' %(hour, minutes, seconds))
