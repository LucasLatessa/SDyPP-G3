from flask import Flask

app = Flask(__name__)

@app.route("/process")
def hello_world():
    data = {
        "data": "hola"
    }
    return data



if __name__ == '__main__':
   app.run() 