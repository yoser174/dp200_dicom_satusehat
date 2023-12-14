import hashlib
import os

import requests
from requests.auth import HTTPBasicAuth

# auth = HTTPBasicAuth(username="username", password="password")

file = "/home/yoserizy/Documents/GitHub/dp200_dicom_satusehat/DICOM_IMAGES/162CB78A"

size = os.path.getsize(file)

hash_md5 = hashlib.md5()

CHUNK_SIZE = 100

with open(file, "rb") as f:
    url = "https://api-satusehat-dev.dto.kemkes.go.id/dicom/telepathology/v1/dicomWeb/studies"
    offset = 0
    for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
        hash_md5.update(chunk)
        res = requests.put(
            url,
            data={"filename": "my_new_file"},
            files={"file": chunk},
            headers={
                "Authorization": "Bearer " + "MQfOwBFG2lBOtUSQ3i87QtqhX7mh",
                "Content-Range": f"bytes {offset}-{offset + len(chunk) -1}/{size}",
            },
        )
        print(res.text)
        offset = int(res.json().get("offset"))
        url = res.json().get("url")
    finalize = requests.post(
        url,
        data={"md5": hash_md5.hexdigest()},
        headers={"Authorization": "Bearer " + "MQfOwBFG2lBOtUSQ3i87QtqhX7mh"},
    )
    print(finalize.status_code)
    print(finalize.text)
