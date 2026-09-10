# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 10:22:58 2025

@author: annej
"""
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import time
#install chrome driver manager

driver = webdriver.Chrome() #(service = service, options=options)

if not os.path.exists('Detailedpages'):
    os.mkdir('Detailedpages')
#if not til at gemme de individuelle links??




def GetDetailedPageLinks(page_source):
    result = []
    #soup = BeautifulSoup(page_source, features="lxml")
    soup = BeautifulSoup(page_source, features="html.parser")
    items = soup.find_all("app-housing-list-item")
    
    #service = Service(ChromeDriverManager().install()) instalerer chromebrowser som selenium bruger til koden
   
    for i, item in enumerate(items):
        try:
            link_element = item.find('a', href=True)
            if link_element:
                result.append(item.find('a')['href'])
            # Skuffesager (og evt. andet) har ikke samme struktur med link
            # Vi springer dem over hvis ikke de har et element <a href="...">
        except:
            print("Item number", i, "failed")

    return result


#funktion til at gemme??


link= 'https://www.boliga.dk/resultat?area=7&searchTab=0&propertyType=1,2,3,4,5,6,9&sort=street-a&pageSize=50&page='
driver.get(link)
time.sleep(3)


cookie_handler = driver.find_element('xpath','//*[@id="CybotCookiebotDialogBodyButtonDecline"]')
cookie_handler.click()


user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
headers = {'User-Agent': user_agent}

detailed_page_links = []
house = 1
more_pages = True
max_pages = 20     # delete this later...

while more_pages:
    try:
        detailed_page = link + str(house)
        driver.get(detailed_page)

        time.sleep(1)

        page_source = driver.page_source
        detailed_links_on_page = GetDetailedPageLinks(page_source)

        if not detailed_links_on_page:
            print("No more pages, starting to save houses as HTMLs")
            more_pages = False
        else:
            detailed_page_links += detailed_links_on_page
            print(house, "scraped")
            house += 1

        time.sleep(0.1)
    except Exception as e:
        print(f"Error at {house}: {e}, {type(e)}")
        more_pages = False
        
current_link = 0
for link in (detailed_page_links):
    current_link += 1
    print(f"processing page {current_link} out of {len(detailed_page_links)} with link {link}")
    try:
        full_link = "https://www.boliga.dk" + link
        driver.get(full_link)
    
    
        page_html = driver.page_source
        
        link_name = link.replace("/","_").replace("?", "_")
        path_to_get_files = os.path.join('Detailedpages', link_name + ".html")
        
        with open(path_to_get_files, "w", encoding='utf-8') as f:
            f.write(page_html)
            
    except Exception as e:
         print(f"Error at {link}: {e}")
        
driver.quit()
        
print("Done scraping and saving")


