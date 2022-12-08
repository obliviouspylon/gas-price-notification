
# Part of code from
# https://www.geeksforgeeks.org/python-web-scraping-tutorial/

import datetime
from pytz import timezone
import requests
from bs4 import BeautifulSoup
import re

URL = "https://gaswizard.ca/gas-price-predictions/"
# Price Prediction for Saturday 19th of November 2022

def getWebsite():
    # Making a GET request
    r = requests.get(URL)
    
    # print content of request
    if ((r.status_code == 200) and (False)):
        with open("GasWizard.html","w") as f:
            f.write(r.content.decode('utf-8'))

    return (r.status_code,r.content)

def parseContent(content, city):
    soup = BeautifulSoup(content, 'html.parser')

    # Get Date
    date_string = soup.find('div', class_='price-date').contents

    # Get Toronto Gas Prices
    cityGasInfo = list(soup.find('td', class_='gwgp-cityname', string= re.compile(city)).parent.children)

    # Remove line
    for value in cityGasInfo:
        if len(value) == 1:
            cityGasInfo.remove(value)

    price, change = list(cityGasInfo[1].children)
    if 'pd-up' in change.attrs['class']:
        direction = 'UP'
    elif 'pd-nc' in change.attrs['class']:
        direction = "STAYS"
    elif 'pd-down' in change.attrs['class']:
        direction = "DOWN"
    amount = change.text

    return(date_string[0], direction, amount, price.replace(" ",""))

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

def ord(n):
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))

def tomrorowDate():
    today = datetime.datetime.now(timezone("EST"))
    tomrorow = today + datetime.timedelta(days=1)
    return (ord(tomrorow.day) + tomrorow.strftime(" of %B %Y"))
# 19th of November 2022

def getPrediction():
    status, content = getWebsite()

    if status == 200:
        city = "Toronto"
        date_string, direction, amount, price = parseContent(content, city)

        tomorrow = tomrorowDate()

        if tomorrow in date_string:
            if direction == "STAYS":
                amount = 0
            else:
                amount = re.findall("\d+",amount)[0]
            return (True,[direction, amount, price])
        else:
            return(False,[])

        # same = True
        # if same:
        #     message = city + " - " +date_string
        #     if direction == "NOT CHANGE":
        #         message = message + "\nGas will NOT CHANGE and stay at " + price + "¢/L"
        #     else:
        #         message = message + "\nGas will " + direction + " by " + amount + "¢ to " + price + "¢/L"
        #     return message
    else:
        return((False,[]))


def sendNotification(message, tn_username, tn_sid, tn_csrf):
    import jsonController
    import random
    import time
    import TextNow
    numbers = jsonController.readUsers()

    #Get message
    data, tomorrow = jsonController.checkPrediction(readData=True)
    tomorrowDate = datetime.datetime.strptime(tomorrow, "%Y%m%d")
    message = ""

    for site in data[tomorrow]:
        direction = data[tomorrow][site]["direction"]
        amount = str(data[tomorrow][site]["amount"])
        price = str(data[tomorrow][site]["price"])
        if direction == "STAYS":
            message = message + site + ": " + direction + " at " + price + "¢/L. "
        else:
            message = message + site + ": " + direction + " by " + amount + " to " + price + "¢/L. "

    if message == "":
        message = "No prediction found for " + tomorrowDate.strftime("%b %d")
    else:
        message = "Gas Prediction - " + tomorrowDate.strftime("%b %d") + ". " + message
    
    for number in numbers:
        time.sleep(random.randint(5,15))
        TextNow.send_sms(number, message, tn_username, tn_sid, tn_csrf)

if __name__ == "__main__":
    status, content = getWebsite()

    if status == 200:
        city = "Toronto"
        date_string, direction, amount, price = parseContent(content, city)

        same = lastCheck(date_string)

        if same:
            print(city + " - " +date_string)
            if direction == "STAYS":
                print("Gas will STAY at " + price + "¢/L")
            else:
                print("Gas will " + direction + " by " + amount + "¢ to " + price + "¢/L")