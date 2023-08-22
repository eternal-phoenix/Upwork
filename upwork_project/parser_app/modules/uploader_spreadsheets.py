# pip3 install google-auth google-auth-httplib2 google-auth-oauthlib google-api-python-client
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_credentials() -> Credentials:
    """file token.json stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first time"""  
        
    credentials = None
    token_path = os.path.abspath('upwork_project/parser_app/files/token.json')
    credentials_path = os.path.abspath('upwork_project/parser_app/files/credentials.json')
        
    if os.path.exists(token_path):
        credentials = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # if there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            credentials = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(credentials.to_json())
            
    return credentials
     

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', ]
SPREADSHEET_ID = '1rpO1tkrsoBM0kTE81vU-UcvVAEZ8TPw97rRLMvw4rW4'
CREDENTIALS = get_credentials()
     
     
def spreadsheets_api_write_row(values: list) -> None:

    credentials = CREDENTIALS

    # call the Google SpreadSheets API
    service = build('sheets', 'v4', credentials=credentials)

    try:
        # Append the row
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f'Sheet1!A:K',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': values}
        ).execute()
        
    except HttpError as error:
        print(f'[INFO] An error occurred: {error}')


if __name__ == '__main__':
    # testing uploader
    spreadsheets_api_write_row([['1','1','1','1','1','1','1','1','1','1','1']])

