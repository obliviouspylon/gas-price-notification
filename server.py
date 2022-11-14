from flask import Flask
from flask_cors import CORS
from waitress import serve
import gasPrice

app = Flask(__name__)
CORS(app)

# config
port = 9000
listenOn = "0.0.0.0"


@app.route('/')
def gasPrediction():
    message = gasPrice.getPrediction()
    return(message)

if __name__ == '__main__':
    print("Starting Flask Server...")
    print("Listening on " + listenOn + ":" + str(port))
    serve(app,host = listenOn, port = port)
#    app.run(host=listenOn, port=port)
