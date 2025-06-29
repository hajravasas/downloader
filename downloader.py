#!/usr/bin/env python3
"""
Google Drive Folder Downloader

This script downloads all files from a specified Google Drive folder
to a local directory on your computer.

Prerequisites:
1. Install required packages: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
2. Set up Google Drive API credentials (see setup instructions below)
"""

import os
import io
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.http import MediaIoBaseDownload

# Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveDownloader:
    def __init__(self, credentials_file='credentials.json', token_file='token.json', use_service_account=False):
        """
        Initialize the Google Drive downloader.
        
        Args:
            credentials_file: Path to the OAuth2 credentials JSON file or service account key
            token_file: Path to store/load the access token (not used with service account)
            use_service_account: If True, use service account authentication instead of OAuth
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.use_service_account = use_service_account
        self.service = None
        
    def authenticate(self):
        """Authenticate with Google Drive API."""
        if self.use_service_account:
            # Service Account Authentication
            if not os.path.exists(self.credentials_file):
                raise FileNotFoundError(
                    f"Service account key file '{self.credentials_file}' not found."
                )
            
            creds = ServiceAccountCredentials.from_service_account_file(
                self.credentials_file, scopes=SCOPES)
            self.service = build('drive', 'v3', credentials=creds)
            print("✓ Successfully authenticated with Google Drive using service account")
            
        else:
            # OAuth Authentication
            creds = None
            
            # Load existing token if available
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            
            # If there are no valid credentials, request authorization
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(
                            f"Credentials file '{self.credentials_file}' not found. "
                            "Please follow the setup instructions to create it."
                        )
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # Build the service
            self.service = build('drive', 'v3', credentials=creds)
            print("✓ Successfully authenticated with Google Drive")
    
    def get_folder_id(self, folder_name):
        """
        Get the folder ID by folder name.
        
        Args:
            folder_name: Name of the folder to find
            
        Returns:
            Folder ID if found, None otherwise
        """
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get('files', [])
        
        if not folders:
            return None
        elif len(folders) == 1:
            return folders[0]['id']
        else:
            print(f"Multiple folders found with name '{folder_name}':")
            for i, folder in enumerate(folders):
                print(f"  {i+1}. {folder['name']} (ID: {folder['id']})")
            
            while True:
                try:
                    choice = int(input("Enter the number of the folder you want: ")) - 1
                    if 0 <= choice < len(folders):
                        return folders[choice]['id']
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
    
    def list_files_in_folder(self, folder_id):
        """
        List all files in a Google Drive folder.
        
        Args:
            folder_id: The ID of the folder
            
        Returns:
            List of file objects
        """
        query = f"'{folder_id}' in parents and trashed=false"
        results = self.service.files().list(
            q=query,
            fields="files(id, name, mimeType, size)",
            pageSize=1000
        ).execute()
        
        return results.get('files', [])
    
    def download_file(self, file_id, file_name, download_path):
        """
        Download a file from Google Drive.
        
        Args:
            file_id: Google Drive file ID
            file_name: Name of the file
            download_path: Local path where file should be saved
        """
        try:
            # Get file metadata
            file_metadata = self.service.files().get(fileId=file_id).execute()
            mime_type = file_metadata.get('mimeType', '')
            
            # Handle Google Workspace files (Docs, Sheets, Slides, etc.)
            if mime_type.startswith('application/vnd.google-apps.'):
                export_formats = {
                    'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'application/vnd.google-apps.drawing': 'image/png'
                }
                
                export_mime_type = export_formats.get(mime_type)
                if export_mime_type:
                    request = self.service.files().export_media(fileId=file_id, mimeType=export_mime_type)
                    # Update file extension for exported files
                    extensions = {
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
                        'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
                        'image/png': '.png'
                    }
                    ext = extensions.get(export_mime_type, '')
                    if not file_name.endswith(ext):
                        file_name += ext
                        download_path = os.path.join(os.path.dirname(download_path), file_name)
                else:
                    print(f"⚠ Skipping unsupported Google Apps file: {file_name}")
                    return False
            else:
                # Regular file download
                request = self.service.files().get_media(fileId=file_id)
            
            # Download the file
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            
            while done is False:
                status, done = downloader.next_chunk()
            
            # Write to file
            with open(download_path, 'wb') as f:
                f.write(fh.getvalue())
            
            # Verify file was written to correct location
            if os.path.exists(download_path):
                print(f"  ✓ Saved to: {download_path}")
            else:
                print(f"  ✗ File not found at expected location: {download_path}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error downloading {file_name}: {str(e)}")
            return False
    
    def download_folder(self, folder_identifier, local_path):
        """
        Download all files from a Google Drive folder.
        
        Args:
            folder_identifier: Either folder name or folder ID
            local_path: Local directory path to save files
        """
        if not self.service:
            raise Exception("Not authenticated. Please run authenticate() first.")
        
        # Debug: Show the path being used
        print(f"📍 Attempting to save files to: {local_path}")
        print(f"📍 Full absolute path: {os.path.abspath(local_path)}")
        
        # Check if path exists and is accessible
        parent_dir = os.path.dirname(local_path)
        if parent_dir and not os.path.exists(parent_dir):
            print(f"⚠ Parent directory doesn't exist: {parent_dir}")
            try:
                os.makedirs(parent_dir, exist_ok=True)
                print(f"✓ Created parent directories")
            except Exception as e:
                print(f"✗ Failed to create parent directories: {e}")
                return
        
        # Create local directory if it doesn't exist
        try:
            os.makedirs(local_path, exist_ok=True)
            print(f"✓ Target directory ready: {local_path}")
        except Exception as e:
            print(f"✗ Failed to create target directory: {e}")
            return
        
        # Get folder ID
        if len(folder_identifier) == 33 and folder_identifier.isalnum():
            # Looks like a folder ID
            folder_id = folder_identifier
        else:
            # Treat as folder name
            folder_id = self.get_folder_id(folder_identifier)
            if not folder_id:
                print(f"✗ Folder '{folder_identifier}' not found.")
                return
        
        print(f"📁 Downloading files from folder ID: {folder_id}")
        
        # Get list of files
        files = self.list_files_in_folder(folder_id)
        
        if not files:
            print("No files found in the folder.")
            return
        
        print(f"Found {len(files)} files to download")
        
        # Download each file
        success_count = 0
        for i, file in enumerate(files, 1):
            file_name = file['name']
            file_id = file['id']
            file_path = os.path.join(local_path, file_name)
            
            print(f"[{i}/{len(files)}] Downloading: {file_name}")
            
            if self.download_file(file_id, file_name, file_path):
                print(f"✓ Downloaded: {file_name}")
                success_count += 1
            
        print(f"\n🎉 Download complete! {success_count}/{len(files)} files downloaded successfully.")


def main():
    """Main function to run the script."""
    print("Google Drive Folder Downloader")
    print("=" * 40)
    
    # Ask user for authentication method
    print("\nChoose authentication method:")
    print("1. OAuth (browser-based)")
    print("2. Service Account (recommended)")
    
    auth_choice = input("Enter choice (1 or 2): ").strip()
    
    if auth_choice == "2":
        # Service Account
        service_key_file = input("Enter path to service account JSON key file: ").strip()
        if not service_key_file:
            service_key_file = "service-account-key.json"
            print(f"Using default: {service_key_file}")
        
        downloader = GoogleDriveDownloader(
            credentials_file=service_key_file,
            use_service_account=True
        )
    else:
        # OAuth
        downloader = GoogleDriveDownloader()
    
    try:
        # Authenticate
        downloader.authenticate()
        
        # Get folder to download
        folder_name = input("\nEnter folder name or folder ID: ").strip()
        if not folder_name:
            print("No folder specified. Exiting.")
            return
        
        # Get local download path
        local_path = input("Enter local download path: ").strip()
        if not local_path:
            local_path = "./downloads"
            print(f"Using default path: {local_path}")
        
        # Download the folder
        downloader.download_folder(folder_name, local_path)
        
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


if __name__ == "__main__":
    main()


"""
SETUP INSTRUCTIONS:

1. Install required packages:
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

2. Set up Google Drive API:
   a. Go to https://console.developers.google.com/
   b. Create a new project or select existing one
   c. Enable the Google Drive API
   d. Go to "Credentials" and click "Create Credentials" → "OAuth 2.0 Client ID"
   e. Configure OAuth consent screen if prompted
   f. Choose "Desktop application" as application type
   g. Download the credentials JSON file
   h. Rename it to 'credentials.json' and place it in the same directory as this script

3. Run the script:
   python gdrive_downloader.py

4. On first run, it will open a browser for authentication
   Grant the necessary permissions

The script will:
- Authenticate with your Google Drive
- Ask for the folder name or ID you want to download
- Ask for the local path where files should be saved
- Download all files from the specified folder
- Handle Google Workspace files by converting them to standard formats
- Show progress and success/failure status for each file
"""