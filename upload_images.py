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
import http.client as httplib
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


def read_in_chunks(file_object, chunk_size=1024):
    """Generator to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def send_dicom(token, fname):
    logging.info("posting dicom file...[%s]" % token)
    # try:
    path = "dicomWeb/studies"
    purl = API_BASEURL + path
    # https://api-satusehat-dev.dto.kemkes.go.id/dicom/telepathology/v1/dicomWeb/studies
    # headers = {
    #     "Content-Type": "application/octet-stream",
    #     "Content-type": "application/dicom",
    #     "Accept": "application/xml",
    #     "Authorization": "Bearer " + token,
    # }

    with open(fname, "rb") as f:
        data = f.read()
        res = requests.post(
            url=purl,
            data=data,
            headers={
                "Content-Type": "application/octet-stream",
                "Authorization": "Bearer " + token,
            },
        )
        print(res.status_code)
        # print(res.text)

        # let's check if what we sent is what we intended to send...
        # assert (
        #     base64.b64decode(
        #         res.json()["data"][len("data:application/octet-stream;base64,") :]
        #     )
        #     == data
        # )
    # session = requests.Session()
    # with open(fname, "rb") as f:
    #     form = encoder.MultipartEncoder(
    #         {
    #             "documents": ("tes.", f, "application/octet-stream"),
    #             "composite": "NONE",
    #         }
    #     )
    #     headers = {
    #         "Prefer": "respond-async",
    #         "Content-Type": "application/dicom",
    #         "Authorization": "Bearer " + token,
    #     }
    #     resp = session.post(purl, headers=headers, data=form)
    #     logging.info(resp.status_code)
    #     # logging.info(resp.text)
    # session.close()
    # chunk_size = 1024 * 1024
    # with open(fname, "rb") as f:
    #     while True:
    #         chunk = f.read(chunk_size)
    #         if not chunk:
    #             break
    #         response = requests.post(
    #             "https://api-satusehat-dev.dto.kemkes.go.id/dicom/telepathology/v1/dicomWeb/studies",
    #             data=chunk,
    #             headers=headers,
    #         )

    # if response.status_code == 200:
    #     print("Success")
    # else:
    #     print("Error")

    # file_size = os.path.getsize(fname)
    # with open(fname, "rb") as fd:
    #     with tqdm(
    #         desc=f"Uploading",
    #         total=file_size,
    #         unit="B",
    #         unit_scale=True,
    #         unit_divisor=1024,
    #     ) as t:
    #         reader_wrapper = CallbackIOWrapper(t.update, fd, "read")
    #         response = requests.post(
    #             purl, data=reader_wrapper, headers=headers, stream=True, timeout=60
    #         )
    #         response.raise_for_status()
    #         logging.info(response.status_code)
    #         if response.status_code == 200:
    #             return True
    # return False
    # logging.info(response.text)

    # SRC = '/path/to/file'
    # DST = '/url/to/upload'

    # session = requests.Session()
    # with open(fname, "rb") as f:
    #     form = encoder.MultipartEncoder(
    #         {
    #             "documents": ("my_file.csv", f, "application/octet-stream"),
    #             "composite": "NONE",
    #         }
    #     )
    #     headers = {"Prefer": "respond-async", "Content-Type": form.content_type}
    #     resp = session.post(purl, headers=headers, data=form)
    #     logging.info(resp.status_code)
    #     logging.info(resp.text)
    # session.close()

    # encoder = MultipartEncoder(
    #     fields={
    #         "file": (
    #             os.path.basename(fname),
    #             open(fname, "rb"),
    #             "text/plain",
    #         )
    #     }
    # )
    # response = requests.post(
    #     purl, data=encoder, headers={"Content-Type": encoder.content_type}
    # )
    # logging.info(response.status_code)
    # logging.info(response.text)

    # with open(fname, "rb") as f:
    #     # payload = f.read()
    #     # payload = "<file contents here>"

    #     headers = {
    #         "Content-Type": "application/octet-stream",
    #         "Content-type": "application/dicom",
    #         "Authorization": "Bearer " + token,
    #     }
    #     with open(fname, "rb") as file:
    #         r = requests.post(
    #             purl,
    #             data=file,
    #             # auth=zfsauth,
    #             verify=False,
    #             headers=headers,
    #             timeout=None,
    #         )

    # r = requests.request("POST", purl, headers=headers, data={"file": f})

    # logging.info(r.status_code)
    # logging.info(r.text)
    # sys.exit(0)

    # logging.info("posting dicom file...[%s]" % token)
    # path = "dicomWeb/studies"
    # head = {
    #     "Content-Type": "application/octet-stream",
    #     "Content-type": "application/dicom",
    #     "Accept": "application/dicom+xml",
    #     "Accept-Encoding": "gzip, deflate, br",
    #     "Authorization": "Bearer " + token,
    # }
    # files = {"upload_file": open(fname, "rb")}
    # purl = API_BASEURL + path
    # r = requests.post(purl, files=files, headers=head)
    # logging.info(r.status_code)
    # logging.info(r.text)
    # sys.exit(0)
    # if r.status_code == 200:
    #     return True
    #     return False
    # except Exception as e:
    #     logging.error(str(e))
    #     return True


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
                        logging.info("")
                    #     shutil.move(full_fname, OUT_SUCCESS + file)
                    # else:
                    #     shutil.move(full_fname, OUT_FAILED + file)
