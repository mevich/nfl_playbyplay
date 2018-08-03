import boto3, botocore
from config import *
from io import BytesIO
from PIL import Image
from werkzeug.utils import secure_filename
import requests
import hashlib


s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET
)


def upload_file_to_s3(file, key, acl="public-read"):
    file.seek(0)
    return s3.upload_fileobj(
        file,
        S3_BUCKET,
        key,
        ExtraArgs={
            "ACL": acl
        }
    )



def download_file_from_s3(bucket_name, filename):
    img_obj = BytesIO()
    s3.download_fileobj(bucket_name, filename, img_obj)
    return img_obj


def resize_image_longest_edge(image_name, long_pixel):
    image_url = '{}originals/{}'.format(S3_LOCATION,image_name)
    data = requests.get(image_url)

    img = Image.open(BytesIO(data.content))
    size = img.size

    ratio = float(long_pixel)/max(size)
    new_size = tuple([int(x*ratio) for x in size])
    img_resize = img.resize(new_size,Image.ANTIALIAS)

    new_img_file = BytesIO()
    img_resize.save(new_img_file, "JPEG")
    key = '{0}px/{1}'.format(long_pixel, image_name)

    return upload_file_to_s3(new_img_file, key)


def resize_image_square(image_name, square_side):
    image_url = '{}originals/{}'.format(S3_LOCATION, image_name)
    data = requests.get(image_url)
    img = Image.open(BytesIO(data.content))
    # img_resize = img.thumbnail(square_side)
    size = img.size
    width,height = size
    offset = (max(size) - min(size))/2
    if width>height:
        box = (offset, 0, min(size)+offset, min(size))
    else:
        box = (0, offset, min(size), min(size)+offset)

    img_crop = img.crop(box)
    new_size = (square_side, square_side)
    img_resize = img_crop.resize(new_size, Image.ANTIALIAS)

    new_img_file = BytesIO()
    img_resize.save(new_img_file, "JPEG")
    key = '{0}*{0}px/{1}'.format(square_side, image_name)

    return upload_file_to_s3(new_img_file, key)



