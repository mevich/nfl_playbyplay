from flask import Flask
from nflpbp_models import database

app = Flask(__name__)
app.secret_key = b'_5#y2L"U4Q8z\n\xec]/'


@app.before_request
def before_request():
    database.connect(reuse_if_open=True)


@app.errorhandler(500)
def internal_error(error):
	database.close()


@app.after_request
def after_request(response):
	if not database.is_closed():
		database.close()
	return response


import handlers




