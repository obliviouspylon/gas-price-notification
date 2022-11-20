from flask import Flask, Response, request
from flask_cors import CORS
from flask_apscheduler import APScheduler # https://viniciuschiele.github.io/flask-apscheduler/rst/usage.html https://www.techcoil.com/blog/how-to-use-flask-apscheduler-in-your-python-3-flask-application-to-run-multiple-tasks-in-parallel-from-a-single-http-request/
from waitress import serve
import datetime
from pytz import timezone
import gasWizard
import Enpro680
import jsonController
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', default=9000, dest='port',
                    help = 'Change Flask Port. Default 9000',)

app = Flask(__name__)
CORS(app)
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)

# config
listenOn = "0.0.0.0"

# @scheduler.task('interval', id='do_test', seconds=5, misfire_grace_time=900)
# def test():
#     print(datetime.datetime.now(timezone("EST")))

def hourisbetween(start, end):
    now = datetime.datetime.now(timezone("EST")).hour
    if (now >= start) and (now <= end):
        return True
    else:
        return False

@scheduler.task('interval', id='do_test', minutes=60, misfire_grace_time=900)
# @scheduler.task('interval', id='do_test', seconds=5, misfire_grace_time=900)
@app.route('/update')
def getGasPrediction():
    # print(datetime.datetime.now(timezone("EST")))
    force = request.args.get('force')
    if hourisbetween(9, 21) or force == "True":
        print("Updating Prediction")
        result = gasWizard.getPrediction()
        if result[0]:
            jsonController.saveJson("GasWizard",result[1][0],result[1][1],result[1][2])
        result = Enpro680.getPrediction()
        if result[0]:
            jsonController.saveJson("EnPro",result[1][0],result[1][1],result[1][2])
        return("Prediction Updated")
    return("Prediction Not Updated")

@app.route('/')
def sendPrediction():
    print("Sending Prediction")
    # message = gasWizard.getPrediction()
    data, tomorrow = jsonController.checkJson(readData=True)
    tomorrowDate = datetime.datetime.strptime(tomorrow, "%Y%m%d")
    message = ""

    for site in data[tomorrow]:
        direction = data[tomorrow][site]["direction"]
        amount = str(data[tomorrow][site]["amount"])
        price = str(data[tomorrow][site]["price"])
        if direction == "STAYS":
            message = message + site + ": " + direction + " at " + price + "\n"
        else:
            message = message + site + ": " + direction + " by " + amount + " to " + price + "\n"

    if message == "":
        return Response("No prediction found for " + tomorrowDate.strftime("%b %d"), status=201)
    else:
        message = "Gas Prediction - " + tomorrowDate.strftime("%b %d") + "\n" + message
        return(message[:-1])

scheduler.start()
if __name__ == '__main__':
    args = parser.parse_args()

    # print(sendPrediction())
    print("Starting Flask Server...")
    print("Listening on " + listenOn + ":" + str(args.port))
    serve(app,host = listenOn, port = int(args.port))
#    app.run(host=listenOn, port=port)
