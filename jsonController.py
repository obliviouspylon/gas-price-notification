
import json
import datetime
from pytz import timezone

def checkPrediction(readData = False):
    # today = datetime.datetime.now(timezone("EST")).strftime("%Y%m%d")
    tomrorow = (datetime.datetime.now(timezone("EST")) + datetime.timedelta(days=1)).strftime("%Y%m%d")
    today = datetime.datetime.now(timezone("EST")).strftime("%Y%m%d")

    write = False
    try:
        with open("predictionData.json","r") as f:
            data = json.load(f)
        if today in data:
            data.pop(today)
            write = True
    except:
        print("Unable to open Data File")
        data = {}
        write = True

    if not tomrorow in data:
        data[tomrorow] = {}

    if write:
        with open("predictionData.json","w") as f:
            json.dump(data, f, indent=4)
    
    if readData:
        return (data, tomrorow)
        
def savePrediction(website, direction, amount, price):
    data, tomorrow = checkPrediction(readData = True)

    if not website in data[tomorrow]:
        data[tomorrow][website] = {
            "direction" : direction,
            "amount" : amount,
            "price" : price
        }
    try:
        with open("predictionData.json","w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

def readPrediction():
    try:
        with open("predictionData.json","r") as f:
            data = json.load(f)
        return(data)
    except:
        return("Can't read json")