import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file'] # Nebo jiný scope podle potřeby
TARGET_FOLDER_ID = '1mo6Qbdp6EU6O4TuuZfdaceuPQiEWbFQm'

def upload_file():
    creds_json = os.environ.get('GDRIVE_SERVICE_ACCOUNT_CREDENTIALS')
    if not creds_json:
        raise ValueError("Environment variable GDRIVE_SERVICE_ACCOUNT_CREDENTIALS is not set.")

    creds_info = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)

    service = build('drive', 'v3', credentials=creds)

    local_file_name = 'Python_nabidky.txt'
    drive_file_name = 'Python_nabidky.txt'

    if not os.path.exists(local_file_name):
        print(f"Chyba: Lokální soubor '{local_file_name}' nebyl nalezen. Ujistěte se, že scraping skript jej vytvořil.")
        return

    # Vyhledání existujícího souboru v konkrétní složce pro aktualizaci
    results = service.files().list(
        q=f"name='{drive_file_name}' and trashed=false and '{TARGET_FOLDER_ID}' in parents",
        spaces='drive',
        fields='files(id, name, parents)').execute() # Přidal jsem 'parents' pro kontrolu
    items = results.get('files', [])

    file_id = None
    if items:
        # Je možné, že najde soubor jinde, pokud je stejné jméno.
        # Zde zajistíme, že najdeme soubor přímo v naší cílové složce.
        for item in items:
            if 'parents' in item and TARGET_FOLDER_ID in item['parents']:
                file_id = item['id']
                print(f"Nalezen existující soubor na Google Drive (složka '{TARGET_FOLDER_ID}') s ID: {file_id}. Bude aktualizován.")
                break
        if not file_id:
             print(f"Soubor '{drive_file_name}' v cílové složce nebyl nalezen. Bude vytvořen nový.")
    else:
        print(f"Soubor '{drive_file_name}' v cílové složce nebyl nalezen. Bude vytvořen nový.")


    file_metadata = {
        'name': drive_file_name,
        'mimeType': 'text/plain',
        'parents': [TARGET_FOLDER_ID] # Klíčové: Řekne GDrive API, kam soubor nahrát
    }
    media = MediaFileUpload(local_file_name, mimetype='text/plain', resumable=True)

    if file_id:
        # Aktualizace existujícího souboru
        file = service.files().update(fileId=file_id,
                                      media_body=media,
                                      fields='id').execute()
        print(f"Soubor '{local_file_name}' byl úspěšně aktualizován na Google Drive (složka '{TARGET_FOLDER_ID}') s ID: {file.get('id')}")
    else:
        # Vytvoření nového souboru
        file = service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute()
        print(f"Soubor '{local_file_name}' byl úspěšně nahrán na Google Drive (složka '{TARGET_FOLDER_ID}') s ID: {file.get('id')}")

if __name__ == '__main__':
    upload_file()
