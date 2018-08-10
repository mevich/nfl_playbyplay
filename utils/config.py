import os

S3_KEY = os.environ.get('S3_KEY_VALUE')
S3_SECRET = os.environ.get('S3_SECRET_KEY_VALUE')
S3_BUCKET = 'mevich-nflpbp-registration-userimages'
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

GMAPS_API = os.environ.get('GMAPS_API_VALUE')


try:
	from config_local import *
except ImportError:
	pass