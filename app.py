from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/test")
def index():
    return {"messages": ["Hi", "Hello", "There"]}

if __name__ == "__main__":
    app.run()