
# Part of code from
# https://www.geeksforgeeks.org/python-web-scraping-tutorial/

import requests
from bs4 import BeautifulSoup
import re

URL = "https://gaswizard.ca/gas-price-predictions/"

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
        direction = 'go UP'
    elif 'pd-nc' in change.attrs['class']:
        direction = "NOT CHANGE"
    elif 'pd-down' in change.attrs['class']:
        direction = "go DOWN"
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

if __name__ == "__main__":
    status, content = getWebsite()

    if status == 200:
        city = "Toronto"
        date_string, direction, amount, price = parseContent(content, city)

        same = lastCheck(date_string)

        if same:
            print(city + " - " +date_string)
            if direction == "NOT CHANGE":
                print("Gas will NOT CHANGE and stay at " + price + "¢/L")
            else:
                print("Gas will " + direction + " by " + amount + "¢ to " + price + "¢/L")