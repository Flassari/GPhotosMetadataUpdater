# Google Photos Datetime Metadata Updater
For fixing datetime metadata for photos and videos downloaded from Google Photos albums.

## Summary
When downloading from Google Photos, the photos/videos might be missing a proper datetime
stamp from the file and EXIF metadata, stripped by Google Photos. This can happen for
some Android device.
This script queries Google Photos for their original datetime and updates the files accordingly.

## Setup
### win32-setctime
Requires the "win32-setctime" python library, I couldn't find another way to set file
creation time: `pip install win32-setctime`

### Google API
Set up a project in the Google API Console: https://console.developers.google.com/apis/library.

Enable Google Photos Library API.

Create a Desktop oauth client. Save the secret as `client_secret.json` in the same folder as this script.

In Data Access, give it these scopes: `/auth/photoslibrary.readonly.originals`, `/auth/photoslibrary`,
and `./auth/photoslibrary.readonly`. There's probably more restrictive scopes that work, send a PR if you find them.

## Usage
This script only works with a single Album in your Google Photos, not your entire photos stream.

Fill in the `album_id` and `folder_path` variables in the script (couldn't be bothered to take them as
input, send a PR if you want.)

You can find the album ID in the URL of the album in Google Photos, or by running the script with the `album_id` variable empty to list all albums and their IDs.

Run the script to update the files' timestamp to the corresponding ones in the album.

You can optionally set DELETE_MISSING_FILES to True to delete files that were not found in the album.
This can happen with iOS Live Photos videos. I didn't need them when creating this script, you
could amend it to set the Live Photo videos to the same date as the photo. Send a PR if you want.

## Version
**1.0** - Initial version. Haven't bothered cleaning it up, it will create a temp "all_data.json" file 
to cache the album data, so it doesn't have to be downloaded every time for debugging purposes.
