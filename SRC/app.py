from flask import Flask
from database import Database

app = Flask(__name__)
service_port = 40001
db = Database()


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/sample-query')
def run_sample_query():
    res = db.sample_query(4, 5)
    return app.send_static_file('index.html')


if __name__ == "__main__":
    app.run(port=service_port)
