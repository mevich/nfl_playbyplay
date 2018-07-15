from flask import Flask
from nflpbp_models import database

app = Flask(__name__)
app.secret_key = b'_5#y2L"U4Q8z\n\xec]/'


@app.before_request
def before_request():
    database.connect()


@app.after_request
def after_request(response):
    database.close()
    return response




import handlers




