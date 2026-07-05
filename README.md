# Google Photos Video Downloader
For downloading videos from Google Photos and fixing their datetime metadata.

## Summary
Made for my compilation video workflows.

When downloading videos from Google Photos, they might be missing a proper datetime
stamp from the file and EXIF metadata, stripped by Google Photos. This can happen for
some Android device.

This script lets you pick up to 2k photos via the Google Photos Picker API,
downloads only the videos, and also corrects the file's datetime to match the original's.

## Setup
### Python
This script was made with Python 3.13.3. If you have the `.venv` folder already, you can run
`.venv\Scripts\activate.bat` to use the right Python environment.

### win32-setctime
Requires the [win32-setctime](https://pypi.org/project/win32-setctime/) python library, I couldn't
find another way to set file creation time:

`pip install win32-setctime`

### Google API
Set up a project in the Google API Console: https://console.developers.google.com/apis/library.

[Enable Google Photos Picker API](https://developers.google.com/photos/overview/configure-your-app).

Create a Desktop oauth client. Save the secret as `client_secret.json` in the same folder as this script.

In Data Access, give it the `.../auth/photospicker.mediaitems.readonly` scope.

## Usage
Start a cmd window in the script's folder. Run the script without any parameters. Input the
folder for where to download the video files when it asks for it.

A browser window will open for you to log into your Google account. Then the Photo Picker
browser window will open, select all photos/vidoes you want. The script will download
only videos, and also correct the datetime stamp on them.

You can choose a maximum of 2000 items. This is a Google Photos Picker API limitation.
If you need to update more than that, simply re-run the script and select the next batch
of items. The script will not download videos if there is already a same-named one in the
folder.

## Version
**3.0** - The script now also downloads videos from Google Photos, simplifying the workflow.

**2.0** - Picker API Migration. Moved from Google Photos Library API to Google Photos Picker API due to
[Google Photos Library API access rights deprecation](https://developers.googleblog.com/en/google-photos-picker-api-launch-and-library-api-updates/).

**1.0** - Initial version. Haven't bothered cleaning it up, it will create a temp "all_data.json" file 
to cache the album data, so it doesn't have to be downloaded every time for debugging purposes.
