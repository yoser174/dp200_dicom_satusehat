import logging.config
import yaml
import configparser
import requests
import os, sys
import shutil
import json
from requests_toolbelt import MultipartEncoder
import urllib3
import mmap
from requests_toolbelt.multipart import encoder
import http.client
import os.path
import requests
import os
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper
import json
import base64


VERSION = "0.0.1"
DICOM_FOLDER = ""
client_id = ""
client_secret = ""

# read ini file
config = configparser.ConfigParser()
config.read("upload_images.ini")
DICOM_FOLDER = config["General"]["DICOM_FOLDER"]
OUT_FAILED = config["General"]["OUT_FAILED"]
OUT_SUCCESS = config["General"]["OUT_SUCCESS"]
client_id = config["General"]["client_id"]
client_secret = config["General"]["client_secret"]
API_BASEURL = config["General"]["API_BASEURL"]


with open("upload_images.yaml", "rt") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


def send_dicom(token, fname):
    logging.info("posting dicom file...[%s]" % token)
    try:
        path = "/dicom/telepathology/v1/dicomWeb/studies"
        conn = http.client.HTTPSConnection(API_BASEURL)
        with open(fname, "rb") as f:
            payload = f.read()
            headers = {
                "Content-type": "application/dicom",
                "Authorization": "Bearer " + token,
                "Accept": "application/dicom+xml",
            }
            conn.request("POST", path, payload, headers)
            res = conn.getresponse()
            data = res.read()
            logging.info(res.status)
            logging.info(data.decode("utf-8"))
            if res.status == 200:
                return True

        return False
    except Exception as e:
        logging.error(str(e))
        return True


def get_token():
    logging.info("geting token...")
    path = "/oauth2/v1/accesstoken?grant_type=client_credentials"

    try:
        conn = http.client.HTTPSConnection(API_BASEURL)
        payload = "client_id=YvIA6rsdXIMSH8b0Leqpg2ldWuzDudtluSvApRHbpN5U1rHb&client_secret=DFckVLAbOaKvsX73ddzvNztSn0ekwVXHeNEuDdaTWRrcRZNVjyI4Qz38vtyc3GQM"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        conn.request("POST", path, payload, headers)
        res = conn.getresponse()
        data = res.read()
        print(data.decode("utf-8"))
        response = json.loads(data.decode("utf-8"))
        logging.info(response)
        token = response["access_token"]
        logging.info(token)
        return True, token
    except Exception as e:
        logging.error(str(e))
        return False, token


if __name__ == "__main__":
    logging.info("start [%s]" % VERSION)
    logging.info("DICOM_FOLDER [%s]" % DICOM_FOLDER)
    logging.info("OUT_FAILED [%s]" % OUT_FAILED)
    logging.info("OUT_SUCCESS [%s]" % OUT_SUCCESS)
    logging.debug("client_id [%s]" % client_id)
    logging.debug("client_secret [%s]" % client_secret)
    logging.info("API_BASEURL [%s]" % API_BASEURL)
    num_file = 0
    for root, dirs, files in os.walk(DICOM_FOLDER):
        for file in files:
            num_file = num_file + 1
    logging.info(num_file)
    if num_file > 0:
        sukses, token = get_token()
        if sukses:
            for root, dirs, files in os.walk(DICOM_FOLDER):
                for file in files:
                    logging.info(os.path.join(root, file))
                    full_fname = os.path.join(root, file)
                    if send_dicom(token=token, fname=full_fname):
                        shutil.move(full_fname, OUT_SUCCESS + file)
                    else:
                        shutil.move(full_fname, OUT_FAILED + file)
