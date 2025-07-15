import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

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

    # Vyhledání existujícího souboru v konkrétní složce
    found_file_id = None
    try:
        results = service.files().list(
            q=f"name='{drive_file_name}' and trashed=false and '{TARGET_FOLDER_ID}' in parents",
            spaces='drive',
            fields='files(id, name, parents)').execute()
        items = results.get('files', [])

        if items:
            for item in items:
                if 'parents' in item and TARGET_FOLDER_ID in item['parents']:
                    found_file_id = item['id']
                    break

    except Exception as e:
        print(f"Chyba při vyhledávání souboru na Google Drive: {e}")
        found_file_id = None


    file_metadata = {
        'name': drive_file_name,
        'mimeType': 'text/plain',
        'parents': [TARGET_FOLDER_ID]
    }
    media = MediaFileUpload(local_file_name, mimetype='text/plain', resumable=True)

    if found_file_id:
        # Aktualizace existujícího souboru
        print(f"Nalezen existující soubor na Google Drive (složka '{TARGET_FOLDER_ID}') s ID: {found_file_id}. Bude aktualizován.")
        file = service.files().update(fileId=found_file_id,
                                      media_body=media,
                                      supportsAllDrives=True, # TOTO JE KLÍČOVÝ PŘÍDAVEK!
                                      fields='id').execute()
        print(f"Soubor '{local_file_name}' byl úspěšně aktualizován na Google Drive (složka '{TARGET_FOLDER_ID}') s ID: {file.get('id')}")
    else:
        # Vytvoření nového souboru
        print(f"Soubor '{drive_file_name}' v cílové složce nebyl nalezen. Bude vytvořen nový.")
        file = service.files().create(body=file_metadata,
                                      media_body=media,
                                      supportsAllDrives=True, # TOTO JE KLÍČOVÝ PŘÍDAVEK!
                                      fields='id').execute()
        print(f"Soubor '{local_file_name}' byl úspěšně nahrán na Google Drive (složka '{TARGET_FOLDER_ID}') s ID: {file.get('id')}")

if __name__ == '__main__':
    upload_file()
