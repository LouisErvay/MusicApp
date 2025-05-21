from dearpygui import dearpygui as dpg

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

# ID du dossier que vous souhaitez examiner
FOLDER_ID = '19HL_7V41eajoSX--TsCz8ocIhVyf8BEE'

global gdrive_handler
gdrive_handler = None

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.

class GDrive_handler:

    def __init__(self):

        self.creds = None
        self.flow = None
        self.drive_service = None

        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
        else:
            self.flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            self.creds = self.flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

        try:
            self.drive_service = build("drive", "v3", credentials=self.creds)

        except HttpError as err:
            print(err)

    def get_folder(self, folder_id):
        # Récupérer la liste des fichiers dans le dossier
        return self.drive_service.files().list(q=f"'{folder_id}' in parents",
                                               fields='files(name, mimeType, id)').execute()

    def get_full_folder(self, folder_id=None):
        try:
            data = self.get_folder(FOLDER_ID if folder_id is None else folder_id).get("files", [])
            for file in data:
                print(file)
                if file['mimeType'] == 'application/vnd.google-apps.folder':
                    self.get_full_folder(folder_id=file['id'])

        except HttpError as err:
            print(err)



def create_handler(s=None, a=None, u=None):
    global gdrive_handler
    gdrive_handler = GDrive_handler()

def load_full_folder(s=None, a=None, u=None):
    global gdrive_handler

    if gdrive_handler is None:
        print("No gdrive handler")
        return

    gdrive_handler.get_full_folder()


def create_tab():
    with dpg.tab(label="Google Drive", tag="gdrive_tab"):
        with dpg.group(horizontal=False):
            dpg.add_button(label="Create handler", callback=create_handler)
            dpg.add_button(label="Gdrive", callback=load_full_folder)
