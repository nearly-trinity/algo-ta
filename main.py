import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import io


# Set your JSON configuration file path
client_secret_file = 'secret.json'
f23_folder_id = "1nEG932UPWHBElot52mJfScJwTPk-o2-U"
download_dir = "homeworks"


# Scopes define the access level you are requesting from the user
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_and_authorize():
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
    creds = flow.run_local_server(port=0)

    return creds


def get_files_in_dir(service, homework_folder_name):

    query = f"'{f23_folder_id}' in parents and name='MWF:11:30'"

    # Execute the query to find the student folder
    student_folder = service.files().list(
        q=query,
        pageSize=1,
        fields="files(id, name)"
    ).execute()

    print(student_folder)
    print()

    query = f"'{f23_folder_id}' in parents and name='HW' and mimeType='application/vnd.google-apps.folder'"

    homework_folder = service.files().list(
        q=query,
        pageSize=1,
        fields="files(id, name)"
    ).execute()

    print(homework_folder)

    # if homework_folder.get('files'):
    #     # Get the ID of the student folder
    #     homework_folder_id = homework_folder['files'][0]['id']

    #     # Build the query string to search for the specific homework folder inside the student folder
    #     query = f"'{student_folder_id}' in parents and name='{homework_folder_name}' and mimeType='application/vnd.google-apps.folder'"

    #     # Execute the query to find the homework folder
    #     homework_folder = service.files().list(
    #         q=query,
    #         pageSize=1,
    #         fields="files(id)"
    #     ).execute()

    #     # Check if the homework folder was found
    #     if homework_folder.get('files'):
    #         # Get the ID of the homework folder
    #         homework_folder_id = homework_folder['files'][0]['id']

    #         # Build the final query to retrieve files within the homework folder
    #         query = f"'{homework_folder_id}' in parents"
            
    #         # Execute the query to get files within the homework folder
    #         results = service.files().list(
    #             q=query,
    #             pageSize=1000,
    #             fields="files(id, name, mimeType)"
    #         ).execute()

    #         files = results.get('files', [])
    #         return files
    #     else:
    #         return []  # Homework folder not found
    # else:
    #     return []  # Student folder not found

    # # copied this from api docs
    # results = service.files().list(
    #     q=f"'{f23_folder_id}' in parents",
    #     pageSize=1000,
    #     fields="files(id, name, mimeType)"
    # ).execute()

    # files = results.get('files', [])

    # return files


def download_files(files, service, download_dir):
    if not files:
        print('No files found in the specified folder.')
    else:
        print(f'Downloading files from the specified folder to "{download_dir}"...')
        os.makedirs(download_dir, exist_ok=True)

        downloaded_files = []

        for file in files:
            file_name = file['name']
            file_id = file['id']
            mime_type = file['mimeType']

            if mime_type == 'application/vnd.google-apps.folder':
                continue

            if mime_type.startswith('application/vnd.google-apps'):
                # google docs, sheets, or slides file, export it as pdf
                export_mimeType = 'application/pdf'
                request = service.files().export(fileId=file_id, mimeType=export_mimeType)
            else:
                # regular binary file
                request = service.files().get_media(fileId=file_id)

            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            done = False

            while done is False:
                status, done = downloader.next_chunk()
                print(f'Download {int(status.progress() * 100)}% of {file_name}')

            downloaded_files.append((file_name, file_content.getvalue()))

        print('Download complete.')

        # Save downloaded PDFs to the download_dir
        for file_name, file_content in downloaded_files:
            pdf_path = os.path.join(download_dir, file_name + '.pdf')
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(file_content)



# Authenticate and authorize the application
credentials = authenticate_and_authorize()
service = build('drive', 'v3', credentials=credentials)


# List folders in Google Drive
files = get_files_in_dir(service, "HW1")
# download_files(files, service, download_dir)


