from flask import Flask
import json
import os

configFile = open(__file__.split('/')[-2]+'/serverConfig.json')
config = json.load(configFile)

PORT = config['port']
app = Flask(__name__)




@app.route('/')
def hello():
    return "server running on port "+str(PORT)

if __name__ == "__main__":
    print("server started on",PORT)
   
    app.run(host = "localhost",port = PORT,debug=True)
   