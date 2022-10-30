from flask import Flask
import json

serverConfig = open('config.json')
config = json.load(serverConfig)

PORT = config['port']

app = Flask(__name__)




@app.route('/')
def hello():
    return "hello world"

if __name__ == "__main__":
    app.run(host = "localhost",port = PORT,debug=True)