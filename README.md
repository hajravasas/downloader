# Google Drive Folder Downloader

A Python script that downloads all files from a specified Google Drive folder to your local computer. Supports both OAuth authentication and Service Account authentication, with automatic handling of Google Workspace files (Docs, Sheets, Slides).

## Features

- 📁 Download entire Google Drive folders with one command
- 🔄 Converts Google Workspace files to standard formats (DOCX, XLSX, PPTX)
- 📊 Real-time progress tracking and status updates
- 🔐 Two authentication methods: OAuth and Service Account
- 🛡️ Robust error handling and retry logic
- 📂 Automatic directory creation
- 🎯 Support for both folder names and folder IDs

## Prerequisites

- Python 3.7 or higher
- Google account with access to Google Drive
- Google Cloud Console project (free)

## Installation

### 1. Install Python Dependencies

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. Download the Script

Save the `downloader.py` script to your desired directory.

## Google Cloud Console Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "Drive Downloader")
5. Click "Create"
6. Wait for the project to be created and select it

### Step 2: Enable Google Drive API

1. In your project, go to **APIs & Services** → **Library**
2. Search for "Google Drive API"
3. Click on "Google Drive API"
4. Click **"Enable"**

### Step 3: Choose Authentication Method

You have two options. **Service Account is recommended** for automated scripts.

## Option A: Service Account Authentication (Recommended)

Service accounts are perfect for automated scripts and don't require browser authentication.

### Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"Service Account"**
3. Fill in the details:
   - **Service account name**: `drive-downloader`
   - **Description**: `Service account for downloading Google Drive files`
4. Click **"Create and Continue"**
5. Skip the optional role assignment (click **"Continue"**)
6. Skip granting users access (click **"Done"**)

### Generate Service Account Key

1. In the **Credentials** page, find your service account
2. Click on the service account name (not the edit icon)
3. Go to the **"Keys"** tab
4. Click **"Add Key"** → **"Create new key"**
5. Select **"JSON"** format
6. Click **"Create"**
7. The key file will automatically download
8. Move the downloaded file to your script directory
9. Rename it to `service-account-key.json`

### Share Google Drive Folder

1. Open the downloaded JSON key file
2. Find the `"client_email"` field and copy the email address
   - It looks like: `drive-downloader@your-project.iam.gserviceaccount.com`
3. Go to [Google Drive](https://drive.google.com)
4. Right-click on the folder you want to download
5. Click **"Share"**
6. Add the service account email address
7. Set permission to **"Viewer"**
8. Uncheck **"Notify people"** (it's a service account)
9. Click **"Send"**

## Option B: OAuth Authentication (Alternative)

OAuth requires browser authentication but works with your personal Google account.

### Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **"External"** user type (or **"Internal"** if using Google Workspace)
3. Fill in the required information:
   - **App name**: `Personal Drive Downloader`
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
4. Click **"Save and Continue"**
5. Skip adding scopes (click **"Save and Continue"**)
6. Add test users:
   - Click **"Add Users"**
   - Add your Gmail address
   - Click **"Save and Continue"**
7. Review and click **"Back to Dashboard"**

### Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"OAuth 2.0 Client ID"**
3. Choose **"Desktop application"**
4. Enter a name like `Drive Downloader Desktop`
5. Click **"Create"**
6. Download the credentials JSON file
7. Move it to your script directory
8. Rename it to `credentials.json`

## Usage

### Running the Script

```bash
python downloader.py
```

### Authentication Flow

The script will prompt you to choose an authentication method:

```
Choose authentication method:
1. OAuth (browser-based)
2. Service Account (recommended)
Enter choice (1 or 2): 2
```

**For Service Account:**

- Enter the path to your service account JSON key file
- Default: `service-account-key.json`

**For OAuth:**

- A browser window will open for authentication
- Sign in with your Google account
- Grant the necessary permissions

### Downloading Files

1. **Enter Google Drive folder:**

   - You can enter either the folder name: `My Photos`
   - Or the folder ID: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

2. **Enter local download path:**
   - Specify where you want files saved, no double quotes
   - Examples:
     - `./downloads` (relative path)
     - `/Users/username/Downloads/MyFiles` (absolute path)
     - `"/Volumes/External Drive/Backup"` (external drive with spaces)

### Finding Google Drive Folder ID

If you prefer using folder IDs instead of names:

1. Go to [Google Drive](https://drive.google.com)
2. Navigate to your folder
3. Look at the URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
4. Copy the ID portion

## Example Usage

```bash
$ python gdrive_downloader.py

Google Drive Folder Downloader
========================================

Choose authentication method:
1. OAuth (browser-based)
2. Service Account (recommended)
Enter choice (1 or 2): 2

Enter path to service account JSON key file: service-account-key.json
✓ Successfully authenticated with Google Drive using service account

Enter folder name or folder ID: Family Photos 2024
📁 Downloading files from folder ID: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms

Enter local download path: /Users/john/Downloads/FamilyPhotos
📍 Attempting to save files to: /Users/john/Downloads/FamilyPhotos
✓ Target directory ready: /Users/john/Downloads/FamilyPhotos

Found 25 files to download
[1/25] Downloading: vacation-photo1.jpg
✓ Downloaded: vacation-photo1.jpg
[2/25] Downloading: family-reunion.png
✓ Downloaded: family-reunion.png
...

🎉 Download complete! 25/25 files downloaded successfully.
```

## File Type Support

The script handles various file types:

| Google Drive File Type | Downloaded As        | Extension |
| ---------------------- | -------------------- | --------- |
| Google Docs            | Microsoft Word       | `.docx`   |
| Google Sheets          | Microsoft Excel      | `.xlsx`   |
| Google Slides          | Microsoft PowerPoint | `.pptx`   |
| Google Drawings        | PNG Image            | `.png`    |
| Regular files          | Original format      | Original  |

## Troubleshooting

### Common Issues

**"Folder not found"**

- Ensure the folder name is spelled correctly
- For service accounts: Make sure you shared the folder with the service account email
- Try using the folder ID instead of the name

**"Permission denied"**

- For service accounts: The service account needs at least "Viewer" access to the folder
- For OAuth: Make sure you granted the necessary permissions during authentication

**"Service account key file not found"**

- Check the file path you entered
- Ensure the JSON key file is in the correct location
- Verify the filename is correct

**"OAuth access denied / Error 403"**

- Add yourself as a test user in the OAuth consent screen
- Make sure you're using the correct Google account
- Try the "Go to [app name] (unsafe)" option in the browser warning

**Files downloading to wrong location**

- Check that the path exists and is writable
- Use quotes around paths with spaces: `"/path/with spaces/"`
- Try using absolute paths instead of relative paths

### Debug Mode

The script includes debug information to help troubleshoot path issues:

```
📍 Attempting to save files to: /your/specified/path
📍 Full absolute path: /full/resolved/path
✓ Target directory ready: /your/specified/path
```

## Security Notes

- **Service Account Keys**: Keep your JSON key files secure and never share them publicly
- **OAuth Tokens**: The script stores authentication tokens locally in `token.json`
- **Permissions**: The script only requests read-only access to your Google Drive

## File Structure

```
your-project/
├── gdrive_downloader.py          # Main script
├── service-account-key.json      # Service account key (if using)
├── credentials.json              # OAuth credentials (if using)
├── token.json                    # OAuth token (auto-generated)
└── downloads/                    # Default download directory
```

## Advanced Usage

### Batch Processing

You can modify the script to process multiple folders by editing the `main()` function to accept command-line arguments or read from a configuration file.

### Scheduling

For automated backups, you can schedule the script using:

**macOS/Linux (cron):**

```bash
# Add to crontab (crontab -e)
0 2 * * * /usr/bin/python3 /path/to/gdrive_downloader.py
```

**Windows (Task Scheduler):**
Create a scheduled task that runs the Python script.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

---

**Note**: This script is for personal use and educational purposes. Make sure you comply with Google's Terms of Service and your organization's policies when using this tool.
