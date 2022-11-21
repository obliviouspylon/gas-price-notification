
# Part of code from
# https://www.geeksforgeeks.org/python-web-scraping-tutorial/

import datetime
from pytz import timezone
import sys
import re
from sys import platform
sys.path.append('./driver')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

URL = "https://toronto.citynews.ca/toronto-gta-gas-prices/"

def getContent():
    if platform == "linux" or platform == "linux2":
        # linux
        # https://askubuntu.com/questions/1399383/how-to-install-firefox-as-a-traditional-deb-package-without-snap-in-ubuntu-22
        options = Options()
        options.add_argument('--headless')
        # browser = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options=options)
        browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(),options=options)
    elif platform == "win32":
        # Windows...
        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.headless = True
        browser = webdriver.Firefox(options=fireFoxOptions)
    else:
        return ("")
    
    browser.implicitly_wait(5)
    browser.get(URL)
    try:
        prediction = browser.find_element(By.CLASS_NAME,"float-box").text
    except:
        prediction = ""
    browser.quit()

    return (prediction)

def tomrorowDate():
    today = datetime.datetime.now(timezone("EST"))
    tomrorow = today + datetime.timedelta(days=1)
    return (tomrorow.strftime("%B %d, %Y"))

def parseContent(prediction):

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
    return(direction, amount, price)

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
    prediction = getContent()
    
    if len(prediction) == 0:
        return(False,[])

    tomorrow = tomrorowDate()
    if tomorrow in prediction:
        direction, amount, price = parseContent(prediction)
        return (True, [direction, amount, price])
    else:
        return(False,[])

if __name__ == "__main__":
    print(getPrediction())
    print()
    # status, content = getWebsite()

    # if status == 200:
    #     city = "Toronto"
    #     date_string, direction, amount, price = parseContent(content)

    #     same = lastCheck(date_string)


    #     if same:
    #         print(city + " - " +date_string)
    #         if direction == "NOT CHANGE":
    #             print("Gas will NOT CHANGE and stay at " + price + "¢/L")
    #         else:
    #             print("Gas will " + direction + " by " + amount + "¢ to " + price + "¢/L")