import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file'] # Nebo jiný scope podle potřeby

def upload_file():
    # Načti credentials z proměnné prostředí
    creds_json = os.environ.get('GDRIVE_SERVICE_ACCOUNT_CREDENTIALS')
    if not creds_json:
        raise ValueError("Environment variable GDRIVE_SERVICE_ACCOUNT_CREDENTIALS is not set.")

    creds_info = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)

    # Zbytek tvého kódu pro nahrání souboru
    service = build('drive', 'v3', credentials=creds)

    # Specifikace názvu lokálního souboru a názvu souboru na Google Drive
    local_file_name = 'Python_nabidky.txt'
    drive_file_name = 'Python_nabidky.txt' # Stejný název na Drive

    # Kontrola, zda lokální soubor existuje
    if not os.path.exists(local_file_name):
        print(f"Chyba: Lokální soubor '{local_file_name}' nebyl nalezen. Ujistěte se, že scraping skript jej vytvořil.")
        return

    # Vyhledání existujícího souboru na Google Drive pro aktualizaci
    # Místo vytváření nového souboru pokaždé, budeme aktualizovat existující
    results = service.files().list(
        q=f"name='{drive_file_name}' and trashed=false",
        spaces='drive',
        fields='files(id, name)').execute()
    items = results.get('files', [])

    file_id = None
    if items:
        file_id = items[0]['id']
        print(f"Nalezen existující soubor na Google Drive s ID: {file_id}. Bude aktualizován.")
    else:
        print(f"Soubor '{drive_file_name}' na Google Drive nebyl nalezen. Bude vytvořen nový.")

    file_metadata = {'name': drive_file_name, 'mimeType': 'text/plain'}
    media = MediaFileUpload(local_file_name, mimetype='text/plain', resumable=True)

    if file_id:
        # Aktualizace existujícího souboru
        file = service.files().update(fileId=file_id,
                                      media_body=media,
                                      fields='id').execute()
        print(f"Soubor '{local_file_name}' byl úspěšně aktualizován na Google Drive s ID: {file.get('id')}")
    else:
        # Vytvoření nového souboru
        file = service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute()
        print(f"Soubor '{local_file_name}' byl úspěšně nahrán na Google Drive s ID: {file.get('id')}")

if __name__ == '__main__':
    upload_file()