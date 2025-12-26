# Google Photos Datetime Metadata Updater
For fixing datetime metadata for photos and videos downloaded from Google Photos albums.

## Summary
When downloading from Google Photos, the photos/videos might be missing a proper datetime
stamp from the file and EXIF metadata, stripped by Google Photos. This can happen for
some Android device.
This script queries Google Photos for their original datetime and updates the files accordingly.

## Setup
### Python
This script was made with Python 3.13.3. If you have the `.venv` folder already, you can run
`.venv\Scripts\activate.bat` to use the right Python environment.

### win32-setctime
Requires the [win32-setctime](https://pypi.org/project/win32-setctime/) python library, I couldn't
find another way to set file creation time: `pip install win32-setctime`

### Google API
Set up a project in the Google API Console: https://console.developers.google.com/apis/library.

[Enable Google Photos Picker API](https://developers.google.com/photos/overview/configure-your-app).

Create a Desktop oauth client. Save the secret as `client_secret.json` in the same folder as this script.

In Data Access, give it the `.../auth/photospicker.mediaitems.readonly` scope.

## Usage
Start a cmd window in the script's folder. Run the script without any parameters. Input the folder containing
the media files when it asks for it.
A browser window will open for you to log into your Google account. Then the Photo Picker browser window
will open, select all photos you want to update the timestamp for.

You can choose a maximum of 2000 items. If you need to update more than that, simply re-run the script
and select the next batch of photos. The script will only update the media items for the photos you choose.

The script will then update the timestamps on all the media files you chose according to what is recorded
in Google Photos.

## Version
**2.0** - Picker API Migration. Moved from Google Photos Library API to Google Photos Picker API due to
[Google Photos Library API access rights deprecation](https://developers.googleblog.com/en/google-photos-picker-api-launch-and-library-api-updates/).

**1.0** - Initial version. Haven't bothered cleaning it up, it will create a temp "all_data.json" file 
to cache the album data, so it doesn't have to be downloaded every time for debugging purposes.
