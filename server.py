from flask import Flask, Response, request, redirect, jsonify
from flask_cors import CORS
from flask_apscheduler import APScheduler
from waitress import serve
import datetime
from pytz import timezone
import gasWizard
import Enpro680
import jsonController
import argparse
import taskerJoinSMS
import time
import logging
import os
import hmac
from dotenv import load_dotenv
from functools import wraps

# --- Setup ---
parser = argparse.ArgumentParser()
parser.add_argument('-p', default=5000, dest='port',
                    help='Change Flask Port. Default 5000',)

app = Flask(__name__)
CORS(app)
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)

# config
listenOn = "0.0.0.0"

load_dotenv()
userKey = os.getenv('USER_KEY')
tasker_join_api = os.getenv('TASKER_JOIN_API')
tasker_join_device = os.getenv('TASKER_JOIN_DEVICE')

# Configure logging
logging.basicConfig(level=logging.DEBUG,  # Set logging level
                    format='%(asctime)s - %(levelname)s - %(message)s')


# --- Authorization Decorator & Helper ---

def valid_key_from_request():
    """
    Validate requests to protected endpoints using constant-time comparison.
    Returns the provided key string if valid, otherwise None.
    """
    if not userKey:
        logging.error("USER_KEY environment variable not set. Authorization disabled.")
        return None
        
    provided_key = request.args.get("Key")

    if provided_key is None:
        provided_key = request.headers.get("X-Api-Key")

    if provided_key is None and request.is_json:
        req_json = request.get_json(silent=True) or {}
        provided_key = req_json.get("Key")

    if not provided_key:
        return None
        
    # SECURITY: Use constant-time comparison
    return hmac.compare_digest(str(provided_key), str(userKey))

def require_auth(f):
    """
    Decorator to enforce API Key authentication on routes.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key_match = valid_key_from_request()
        
        if not provided_key_match:
            logging.warning("Unauthorized access attempt detected.")
            return jsonify({"error": "Unauthorized. Invalid or missing API Key."}), 401
        
        # Pass the validated key to the decorated function if necessary (optional)
        # For simplicity here, we just pass the request along if authorized.
        return f(*args, **kwargs)
    return decorated_function


# --- Utility Functions ---

def hourisbetween(start, end):
    now = datetime.datetime.now(timezone("EST")).hour
    if (now >= start) and (now <= end):
        return True
    else:
        return False

# --- Routes ---

@scheduler.task('interval', id='do_test', minutes=60, misfire_grace_time=900)
@app.route('/update')
def getGasPrediction():
    # print(datetime.datetime.now(timezone("EST")))
    try:
        force = request.args.get('force', 'False') # Use default value
    except Exception as e:
        logging.error(f"Error parsing 'force' parameter: {e}")
        force = "False"
        
    if hourisbetween(9, 21) or force == "True":
        print("Updating Prediction")
        try:
            result = gasWizard.getPrediction()
            if result and result[0]:
                jsonController.savePrediction("GasWizard", result[1][0], result[1][1], result[1][2])
        except Exception as e:
            logging.error(f"Error updating GasWizard prediction: {e}")
        try:
            result = Enpro680.getPrediction()
            if result and result[0]:
                jsonController.savePrediction("EnPro", result[1][0], result[1][1], result[1][2])
        except Exception as e:
            logging.error(f"Error updating EnPro680 prediction: {e}")
        return("Prediction Updated")
    return("Prediction Not Updated")


@app.route('/')
def sendPrediction():
    print("Sending Prediction")
    try:
        data, tomorrow = jsonController.checkPrediction(readData=True)
        tomorrowDate = datetime.datetime.strptime(tomorrow, "%Y%m%d")
        message = ""

        for site in data.get(tomorrow, {}):
            direction = data[tomorrow][site].get("direction", "UNKNOWN")
            amount = str(data[tomorrow][site].get("amount", "0"))
            price = str(data[tomorrow][site].get("price", "0"))
            
            if direction == "UNKNOWN":
                continue
            if direction == "STAYS":
                message = f"{message}{site}: {direction} at {price}¢/L\n"
            else:
                message = f"{message}{site}: {direction} by {amount} to {price}¢/L\n"
        
        if message == "":
            return Response("No prediction found for " + tomorrowDate.strftime("%b %d"), status=201)
        else:
            message = "Gas Prediction - " + tomorrowDate.strftime("%b %d") + "\n" + message
            return(message[:-1])
    except Exception as e:
        logging.error(f"Error generating prediction message: {e}")
        return jsonify({"error": "Could not generate prediction message."}), 500


@app.route('/user', methods=['POST', 'GET', "DELETE"])
@require_auth
def manageUsers():
    content_type = request.headers.get('Content-Type')
    
    if content_type != 'application/json':
        logging.warning("User route accessed without application/json content type.")
        return jsonify({"error": "Unsupported Media Type"}), 415

    try:
        reqJson = request.get_json()
    except Exception:
        return jsonify({"error": "Invalid JSON payload"}), 400


    if request.method == 'GET' or request.method == 'PUT':
        # print("Find Users")
        return(";".join(jsonController.readUsers()))

    elif request.method == 'POST':
        # print("Add User")
        try:
            number = reqJson["Number"]
        except KeyError:
            return jsonify({"error": "Missing 'Number' field in request body"}), 400
            
        if jsonController.addUser(number):
            try:
                sms_success = taskerJoinSMS.sendSMS(tasker_join_api, tasker_join_device, number,
                                  "Success!\n"
                                  "You will receive predictions daily.\n"
                                  "Text CHECK for current prediction.\n"
                                  "Text STOP to opt out.\n"
                                  "Contact James for any questions."
                                  )
                sms_prediction = sendPrediction() 
                taskerJoinSMS.sendSMS(tasker_join_api, tasker_join_device, number, sms_prediction)
                return jsonify({"status": "Successful", "message": "User added and SMS sent"})
            except Exception as e:
                logging.error(f"SMS sending failed for new user: {e}")
                return jsonify({"status": "Failed", "message": "User added, but SMS failed to send."}), 500
        else:
            taskerJoinSMS.sendSMS(tasker_join_api, tasker_join_device, number, "Something went wrong. Please contact James")
            return jsonify({"status": "Failed", "message": "User number invalid or storage failed."}), 400

    elif request.method == 'DELETE':
        # print("Remove User")
        try:
            number = reqJson["Number"]
        except KeyError:
            return jsonify({"error": "Missing 'Number' field in request body"}), 400
        
        if jsonController.deleteUser(number):
            taskerJoinSMS.sendSMS(tasker_join_api, tasker_join_device, number, "You have been removed. Bye!")
            return jsonify({"status": "Successful", "message": "User removed."})
        else:
            taskerJoinSMS.sendSMS(tasker_join_api, tasker_join_device, number, "Something went wrong. Please contact James")
            return jsonify({"status": "Failed", "message": "User not found or deletion failed."}), 404
    else:
        return jsonify({"error": "Method Not Allowed"}), 405


# --- SMS Jobs ---

def sendSMS_job(force=False, number=None, mark_sent=True):
    # Check if the time window allows sending (or if forced)
    if hourisbetween(13, 21) or force:
        try:
            # Call the route function to generate the message content
            message = sendPrediction()
            if isinstance(message, tuple): # Check if sendPrediction returned an error response
                logging.error("Could not retrieve prediction message for SMS.")
                return "Failed: Prediction unavailable"
            if isinstance(message, dict): # Check if sendPrediction returned an error response (JSON)
                logging.error(f"Error response from sendPrediction: {message.get('error')}")
                return "Failed: Prediction unavailable"
            
        except Exception as e:
            logging.error(f"Critical error during message generation in sendSMS_job: {e}")
            return "Failed: Internal message error"


        # Read existing contents safely
        try:
            with open("gasPredictionMessage.txt", "r") as f:
                contents = f.read().strip()
        except FileNotFoundError:
            contents = ""
        except Exception as e:
            logging.error(f"Error reading gasPredictionMessage.txt: {e}")
            contents = ""

        if message != contents:
            if number == "" or number is None:
                try:
                    numbers = jsonController.readUsers()
                except Exception as e:
                    logging.error(f"Failed to read users for broadcast: {e}")
                    return "Failed: User list unavailable"
            else:
                numbers = {number: True}

            for number_item in numbers:
                if isinstance(number_item, dict):
                     number = list(number_item.keys())[0] # Handle dictionary keys if structure changed
                else:
                     number = str(number_item)
                     
                try:
                    taskerJoinSMS.sendSMS(tasker_join_api, tasker_join_device, number, message)
                    time.sleep(5) # Delay between individual SMS sends
                except Exception as e:
                    logging.error(f"Failed to send SMS to {number}: {e}")
                    # Continue to next user even if one fails
                    continue

            if mark_sent:
                try:
                    with open("gasPredictionMessage.txt", "w") as f:
                        f.write(message)
                except Exception as e:
                    logging.error(f"Failed to write to gasPredictionMessage.txt: {e}")
                    
            return("Successful")
        else:
            return ""
    else:
        return ""


@scheduler.task('interval', id='send_gas_SMS', minutes=130, misfire_grace_time=900)
def scheduled_sendSMS():
    # Scheduler calls the internal job directly
    return sendSMS_job(force=False, number=None, mark_sent=True)


@app.route('/gas/sendSMS')
@require_auth
def sendSMS_route():
    # Manual sends do NOT update gasPredictionMessage.txt, so they will not
    # suppress the later scheduled SMS.
    force = request.args.get('force') == "True"
    number = request.args.get('number')

    try:
        return sendSMS_job(force=force, number=number, mark_sent=False)
    except Exception as e:
        logging.error(f"Error executing manual SMS route: {e}")
        return jsonify({"error": "Failed to execute manual SMS job."}), 500


# --- Global Error Handlers ---

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the exception
    logging.exception("An unhandled exception occurred:")  # Logs traceback
    # Return a JSON response with the error message
    response = {
        "error": str(e),
        "status_code": 500
    }
    return jsonify(response), 500


@app.errorhandler(404)
def path_not_found(e):
    print("Someone tried a weird route: " + str(request.path))
    return jsonify({"error": "Not Found"}), 404


# --- Startup ---

scheduler.start()
if __name__ == '__main__':
    args = parser.parse_args()

    print("Starting Flask Server...")
    print("Listening on " + listenOn + ":" + str(args.port))
    serve(app, host=listenOn, port=int(args.port))