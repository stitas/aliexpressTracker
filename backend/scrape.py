import re
import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--incognito')

def get_source(url):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    elem = driver.find_element(By.TAG_NAME, 'body')
    no_of_pagedowns = 20

    while no_of_pagedowns:
        elem.send_keys(Keys.PAGE_DOWN)
        no_of_pagedowns-=1
        time.sleep(0.1)

    return driver.page_source

def get_product_data(url):
    product_info = {}
    if url[0] != 'h':
        soup = BeautifulSoup(requests.get('http:'+url).content, 'html5lib')
    else:
        soup = BeautifulSoup(requests.get(url).content, 'html5lib')
    s = soup.find(lambda t: t.name == 'script' and 'window.runParams' in t.text)
    data = re.sub('^.*?{','',s.text.strip())
    data = re.sub('^.*?:','',data.strip())
    data = data.replace('\\"','')
    data = data[:-2]

    try:
        data = json.loads(data)
    except:
        return product_info
    
    product_info['title'] = data['metaDataComponent']['title']
    product_info['url'] = data['metaDataComponent']['ogurl']
        
    if 'minActMultiCurrencyPrice' in data['priceComponent']['discountPrice']:
        product_info['discountedPrice'] = float(data['priceComponent']['discountPrice']['minActMultiCurrencyPrice'])
            
    product_info['originalPrice'] = float(data['priceComponent']['origPrice']['minMultiCurrencyPrice'])
    product_info['rating'] = float(data['feedbackComponent']['evarageStar'])
    product_info['image'] = data['imageComponent']['imagePathList'][0]
    product_info['currency'] = data['priceComponent']['origPrice']['minAmount']['currency']
    
    return product_info

# Unused function meant to scrape data for a number of products of given category 

#def get_product_list(base_url,num_of_products):
#    
#    page_index = 1
#    product_list = []
#    products = []
#    products_data = []
#    run = True
#    
#    while run:
#        url = base_url+'&page='+str(page_index)
#        soup = BeautifulSoup(get_source(url),'html.parser')
#        
#        products = soup.find_all('data',{'class':'search-card-item'},href=True)
#       
#        for product in products:
#            product_list.append(product['href'])
#            
#            if len(product_list) >= num_of_products:
#                run = False
#                break
#            
#        page_index += 1
#        
#    for product in product_list:
#        product_info = get_product_data('http:'+product)
#        products_data.append(product_info)
#        
#    return products_data
