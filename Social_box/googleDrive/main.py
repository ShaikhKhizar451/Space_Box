from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]
file_path = os.path.realpath(os.curdir)
file_bool = os.path.exists(file_path + "/Social_box/googleDrive/token.json")

# This Function will create drive service, creates token if exists or else use token to access cloud data
def create_service():
    creds = None
    if os.path.exists(file_path + "/Social_box/googleDrive/token.json"):
        creds = Credentials.from_authorized_user_file(
            file_path + "/Social_box/googleDrive/token.json", SCOPES
        )
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                file_path + "/Social_box/googleDrive/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(file_path + "/Social_box/googleDrive/token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("drive", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
