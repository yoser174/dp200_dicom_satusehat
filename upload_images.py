import logging.config
import yaml
import configparser
import requests
import os, sys
import shutil
import json


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
    try:
        logging.info("posting dicom file...[%s]" % token)
        path = "dicomWeb/studies"
        head = {
            "Content-Type": "application/octet-stream",
            "Content-type": "application/dicom",
            "Accept": "application/dicom+xml",
            "Accept-Encoding": "gzip, deflate, br",
            "Authorization": "Bearer " + token,
        }
        files = {"upload_file": open(fname, "rb")}
        purl = API_BASEURL + path
        r = requests.post(purl, files=files, headers=head)
        logging.info(r.status_code)
        logging.info(r.text)
        sys.exit(0)
        if r.status_code == 200:
            return True
        return False
    except Exception as e:
        logging.error(str(e))
        return True


def get_token():
    logging.info("geting token...")
    path = "accesstoken?grant_type=client_credentials"
    token = ""

    # purl = "https://api-satusehat-dev.dto.kemkes.go.id/oauth2/v1/accesstoken?grant_type=client_credentials"
    try:
        purl = API_BASEURL + path
        logging.debug(purl)
        head = {"Content-Type": "application/x-www-form-urlencoded"}
        auth_info = {
            "client_id": client_id,
            "grant_type": "client_credentials",
            "client_secret": client_secret,
            "scope": "unit",
        }
        r = requests.post(purl, auth_info, head)

        response = json.loads(r.text)
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
