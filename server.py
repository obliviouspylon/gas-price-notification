from flask import Flask
from flask_cors import CORS
from waitress import serve
import gasPrice

app = Flask(__name__)
CORS(app)

port = 9000


@app.route('/')
def gasPrediction():
    message = gasPrice.getPrediction()
    return(message)

if __name__ == '__main__':
    print("Starting Flask Server...")
    print("Port: " + str(port))
    serve(app,host = "localhost", port = port)
    # app.run(host="localhost", port=port)