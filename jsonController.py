import json
import datetime
from pytz import timezone
import os

def checkPrediction(readData = False):
    # Determine dates
    tomrorow = (datetime.datetime.now(timezone("EST")) + datetime.timedelta(days=1)).strftime("%Y%m%d")
    today = datetime.datetime.now(timezone("EST")).strftime("%Y%m%d")

    write = False
    data = {}
    
    try:
        # Safer file reading
        with open("predictionData.json", "r") as f:
            data = json.load(f)
        
        # Safely remove today's data if it exists
        if today in data:
            data.pop(today)
            write = True
            
    except FileNotFoundError:
        print("predictionData.json not found. Starting fresh structure.")
        write = True # We need to write the structure back later
    except json.JSONDecodeError:
        print("Error decoding predictionData.json. File may be corrupted. Starting fresh structure.")
        write = True # Treat as needing a rewrite to empty structure
    except Exception as e:
        # Catching other unexpected IO errors
        print(f"Unexpected error reading prediction data: {e}")
        write = True

    # Ensure tomorrow's key exists
    if not tomrorow in data:
        data[tomrorow] = {}
        write = True # Structure changed, so rewrite

    if write:
        try:
            with open("predictionData.json", "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"CRITICAL: Could not write to predictionData.json: {e}")
    
    if readData:
        return (data, tomrorow)
        
def savePrediction(website, direction, amount, price):
    # Use the improved checkPrediction which handles file I/O errors gracefully
    data, tomorrow = checkPrediction(readData = True)

    if website not in data.get(tomorrow, {}):
        data[tomorrow][website] = {
            "direction" : direction,
            "amount" : amount,
            "price" : price
        }
    
    # Rewrite after modification
    try:
        with open("predictionData.json", "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving prediction data: {e}")


def readPrediction():
    try:
        with open("predictionData.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return "Can't read json: File not found"
    except json.JSONDecodeError:
        return "Can't read json: Corrupted file"
    except Exception as e:
        return f"Can't read json: {e}"


def badNumber(number):
    if not isinstance(number, str):
        return True
        
    if number.startswith("+1"):
        # +1XXXXXXXXXX (12 chars total)
        if len(number) != 12 or not number[1:].isdigit():
            return True
    elif len(number) != 10 or not number.isdigit():
        return True
    return False

def addUser(number):
    if badNumber(number):
        return False
        
    data = {}
    try:
        with open("gasUsers.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("gasUsers.json not found. Creating new file.")
        # If file doesn't exist, data remains {}
    except json.JSONDecodeError:
        print("Error decoding gasUsers.json. Starting fresh.")
        pass # Data remains {}
    except Exception as e:
        print(f"Unexpected error reading gasUsers.json: {e}")
        return False

    if number in data:
        print(f"User {number} already exists.")
        return False

    data[number] = True

    try:
        with open("gasUsers.json", "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error writing gasUsers.json: {e}")
        return False

def readUsers(jsonForm = False):
    data = {}
    try:
        with open("gasUsers.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("gasUsers.json not found. Returning empty list.")
        return [] if not jsonForm else {}
    except json.JSONDecodeError:
        print("Error decoding gasUsers.json. Returning empty list.")
        return [] if not jsonForm else {}
    except Exception as e:
        print(f"Error reading gasUsers.json: {e}. Returning empty list.")
        return [] if not jsonForm else {}

    if jsonForm:
        return data
    else:
        # Return list of numbers (keys)
        return list(data.keys())

def deleteUser(number):
    if badNumber(number):
        return False

    data = {}
    try:
        with open("gasUsers.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        # If file is missing or corrupt, we can't delete, so we fail gracefully
        return False

    if number not in data:
        print(f"User {number} not found for deletion.")
        return False
        
    data.pop(number)

    try:
        with open("gasUsers.json", "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error writing gasUsers.json after deletion: {e}")
        return False