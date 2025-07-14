from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import os

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def upload_file():
    creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': 'Python_nabidky.txt', 'parents': ['1mo6Qbdp6EU6O4TuuZfdaceuPQiEWbFQm']}
    media = MediaFileUpload('Python_nabidky.txt', mimetype='text/plain', resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print('File ID:', file.get('id'))

if __name__ == '__main__':
    upload_file()
