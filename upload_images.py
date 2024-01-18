import os
import sys
import json
import configparser
import shutil
import requests
import yaml
import logging.config
import time

VERSION = "0.1"
DICOM_FOLDER = ""
client_id = ""
client_secret = ""

# read ini file
config = configparser.ConfigParser()
config.read("upload_images.ini")
DICOM_FOLDER = config["General"]["DICOM_FOLDER"]
OUT_FAILED = config["General"]["OUT_FAILED"]
OUT_SUCCESS = config["General"]["OUT_SUCCESS"]
OUT_TEMP = config["General"]["OUT_TEMP"]
client_id = config["General"]["client_id"]
client_secret = config["General"]["client_secret"]
API_BASEURL = config["General"]["API_BASEURL"]
TOKEN_PATH = config["General"]["TOKEN_PATH"]
SEND_PATH = config["General"]["SEND_PATH"]

# Define a function to recursively delete empty folders
def delete_empty_folders(folder):
    # Get the list of files and subfolders in the folder
    files = os.listdir(folder)
    # Loop through each item
    for f in files:
        # Get the full path of the item
        fullpath = os.path.join(folder, f)
        # If the item is a subfolder, call the function recursively
        if os.path.isdir(fullpath):
            delete_empty_folders(fullpath)
    # After deleting the subfolders, check if the folder is empty
    files = os.listdir(folder)
    # If the folder is empty, delete it
    if len(files) == 0:
        logging.info(f"Deleting empty folder: {folder}")
        os.rmdir(folder)
        
def send_dicom(token, fname):
    """Send a DICOM file to the telepathology service using an API.

    Args:
        token (str): The access token for the API.
        fname (str): The path of the DICOM file.

    Returns:
        bool: True if the file was uploaded successfully, False otherwise.
    """
    logging.info(f"posting dicom file...[{token}]")
    try:
        path = SEND_PATH
        url = f"https://{API_BASEURL}{path}"
        with open(fname, "rb") as f:
            payload = f.read()
            headers = {
                "Content-type": "application/dicom",
                "Authorization": f"Bearer {token}",
                "Accept": "application/dicom+xml",
            }
            response = requests.post(url, data=payload, headers=headers)
            logging.info(response.status_code)
            logging.info(response.text)
            if response.status_code == 200:
                return True
            if response.status_code == 401:
                # un authorized, token expired
                logging.exception("401 (token expired?), exiting...")
                #sys.exit(0)

        return False
    except Exception as e:
        logging.exception(e)
        return False


def get_token(client_id, client_secret):
    """Get an access token from the API using client credentials.

    Args:
        client_id (str): The client ID for the API.
        client_secret (str): The client secret for the API.

    Returns:
        bool, str: True and the token if successful, False and an empty string otherwise.
    """
    logging.info("getting token...")
    path = TOKEN_PATH

    try:
        url = f"https://{API_BASEURL}{path}"
        payload = f"client_id={client_id}&client_secret={client_secret}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(url, data=payload, headers=headers)
        logging.info(response.text)
        response = response.json()
        token = response["access_token"]
        logging.info(token)
        return True, token
    except Exception as e:
        logging.exception(e)
        return False, ""


def main():
    """The main function of the script."""
    logging.info(f"start [{VERSION}]")
    logging.info(f"DICOM_FOLDER [{DICOM_FOLDER}]")
    logging.info(f"OUT_FAILED [{OUT_FAILED}]")
    logging.info(f"OUT_SUCCESS [{OUT_SUCCESS}]")
    logging.debug(f"client_id [{client_id}]")
    logging.debug(f"client_secret [{client_secret}]")
    logging.info(f"API_BASEURL [{API_BASEURL}]")
    logging.info(f"TOKEN_PATH [{TOKEN_PATH}]")
    logging.info(f"SEND_PATH [{SEND_PATH}]")
    num_file = 0
    for root, dirs, files in os.walk(DICOM_FOLDER):
        for file in files:
            num_file = num_file + 1
    logging.info(f"Total number of files to send: {num_file}")
    if num_file > 0:
        success, token = get_token(client_id, client_secret)
        if success:
            start_time = time.time()
            # create an empty list to store the file names or paths
            file_list = []
            for root, dirs, files in os.walk(DICOM_FOLDER):
                for file in files:
                    # get the full path of the file
                    full_fname = os.path.join(root, file)
                    # get the relative path of the file to the source folder
                    rel_path = os.path.relpath(full_fname, DICOM_FOLDER)
                    # append the relative path to the output folder
                    new_dest = os.path.join(OUT_TEMP, rel_path)
                    # create any intermediate directories if needed
                    os.makedirs(os.path.dirname(new_dest), exist_ok=True)
                    # move the file to the new destination
                    shutil.move(full_fname, new_dest) 
                    # append the file name or path to the list
                    file_list.append(new_dest)
            logging.info(f"List of files: {file_list}")
            # Get the list of files and subfolders in the folder
            files = os.listdir(DICOM_FOLDER)
            # Loop through each item
            for f in files:
                # Get the full path of the item
                fullpath = os.path.join(DICOM_FOLDER, f)
                # If the item is a subfolder, call the function recursively
                if os.path.isdir(fullpath):
                    delete_empty_folders(fullpath)
            if len(file_list) > 0:
                # iterate over the files from the list
                for file in file_list:
                    full_fname = file
                    logging.info(full_fname)
                    # get the relative path of the file to the source folder
                    rel_path = os.path.relpath(full_fname, OUT_TEMP)
                    # get the current time in seconds
                    current_time = time.time()
                    # subtract the current time from the start time to get the elapsed time
                    elapsed_time = current_time - start_time
                    # if the elapsed time is greater than 50 minutes, request a new token and update the start time
                    if elapsed_time > 50 * 60:
                        success, token = get_token(client_id, client_secret)
                        if success:
                            start_time = time.time()
                    if send_dicom(token=token, fname=full_fname):
                        # append the relative path to the output folder
                        new_dest = os.path.join(OUT_SUCCESS, rel_path)
                        # create any intermediate directories if needed
                        os.makedirs(os.path.dirname(new_dest), exist_ok=True)
                        # move the file to the new destination
                        shutil.move(full_fname, new_dest)
                    else:
                        # append the relative path to the output folder
                        new_dest = os.path.join(OUT_FAILED, rel_path)
                        # create any intermediate directories if needed
                        os.makedirs(os.path.dirname(new_dest), exist_ok=True)
                        # move the file to the new destination
                        shutil.move(full_fname, new_dest)
                delete_empty_folders(OUT_TEMP)
                os.makedirs(os.path.dirname(OUT_TEMP), exist_ok=True)
                delete_empty_folders(OUT_FAILED)
                os.makedirs(os.path.dirname(OUT_FAILED), exist_ok=True)

if __name__ == "__main__":
    # read the logging configuration from the yaml file
    with open("upload_images.yaml", "rt") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    # call the main function
    main()
