
# Part of code from
# https://www.geeksforgeeks.org/python-web-scraping-tutorial/

import datetime
from pytz import timezone
import sys
import re
from sys import platform
import requests

def scrape_content():
    city_news_url = "https://toronto.citynews.ca/toronto-gta-gas-prices/"
    sys.path.append('./driver')

    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.firefox.options import Options
    from webdriver_manager.firefox import GeckoDriverManager
    if platform == "linux" or platform == "linux2":
        # linux
        # https://askubuntu.com/questions/1399383/how-to-install-firefox-as-a-traditional-deb-package-without-snap-in-ubuntu-22
        options = Options()
        options.add_argument('--headless')
        # browser = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options=options)
        # browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(),options=options)
        browser = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options=options)
    elif platform == "win32":
        # Windows...
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.headless = True
        browser = webdriver.Firefox(options=fireFoxOptions)
    else:
        return ("")
    
    browser.implicitly_wait(5)
    browser.get(city_news_url)
    try:
        prediction = browser.find_element(By.CLASS_NAME,"float-box").text
    except:
        prediction = ""
    browser.quit()

    # Check if prediction is valid
    if len(prediction) == 0:
        return(False,[])

    tomorrow = tomrorowDate("%B %d, %Y")
    if tomorrow in prediction:

        if 'no change' in prediction.lower(): # No Change
            direction = "STAYS"
            amount = 0
        else:
            # '1 cent(s)\nEn-Pro tells CityNews that prices are expected to fall 1 cent(s) at 12:01am on November 18, 2022 to an average of 157.9 cent(s)/litre at most GTA stations.'
            if 'rise' in prediction.lower():
                direction = 'UP'
            elif 'fall' in prediction.lower():
                direction = "DOWN"
            
            centSplit = prediction.split("cent(s)")
            amount = centSplit[0].strip()

        price = re.findall("(?<=average of).*(?=cent)",prediction)[0].replace(" ","")
        return (True, [direction, amount, price])
    else:
        return(False,[])

def get_enpro_api():
    # Check City
    # r = requests.get('http://cms.en-pro.com/api/enpro-cities-list')

    # Assume City 1 is Toronto
    try:
        r = requests.get('https://cms.en-pro.com/api/enpro-city-prices/1', verify=True)
    except:
        print("Unable to get trusted SSL Certificate for Enpro")
        r = requests.get('https://cms.en-pro.com/api/enpro-city-prices/1', verify=False)
    if r.status_code == 200:
        body_json = r.json()
        today_date = datetime.datetime.now(timezone("EST")).strftime("%d-%m-%Y")
        tomorrow_date = tomrorowDate("%d-%m-%Y")
        today_price, tomorrow_price = (None, None)
        for i in body_json["data"]:
            if i["date"] == today_date:
                today_price = float(i["price"]) * 100
            elif i["date"] == tomorrow_date:
                tomorrow_price = float(i["price"]) * 100
        
        if today_price is not None and tomorrow_price is not None:
            change_amount = tomorrow_price - today_price
            if change_amount == 0:
                direction = "STAYS"
            elif change_amount < 0:
                direction = "DOWN"
            elif change_amount > 0:
                direction = "UP"

            return (True, [direction, abs(change_amount), tomorrow_price])
        else:
            return(False,[])

def tomrorowDate(date_format):
    today = datetime.datetime.now(timezone("EST"))
    tomorrow = today + datetime.timedelta(days=1)
    return tomorrow.strftime(date_format)

def lastCheck(date_string):
    try:
        with open("lastCheck.txt","r") as f:
            content = f.read()
    except:
        return (True)
    
    if content != date_string:
        with open("lastCheck.txt","w") as f:
            f.write(date_string)
        return (True)
    else:
        return (False)

def getPrediction():
    # return(scrape_content())
    return(get_enpro_api())

if __name__ == "__main__":
    print(getPrediction())