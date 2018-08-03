import os

S3_KEY = os.environ.get('S3_KEY_VALUE')
S3_SECRET = os.environ.get('S3_SECRET_KEY_VALUE')
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)


try:
	from config_local import *
except ImportError:
	pass