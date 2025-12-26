# Read the README.md file for instructions on how to use this script.
# This script sets the creation date of files in a folder based on their metadata from Google Photos.
# Uses the Photos Picker API for selecting media items.

import os
import webbrowser
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
import requests

# Ask the user to input the folder path
folder_path = ""
while not folder_path:
	folder_path = input("Enter the path to the folder containing the files you want to update: ")
	if not folder_path:
		print("Error: Folder path cannot be empty.")
	elif not os.path.exists(folder_path) or not os.path.isdir(folder_path):
		print("Error: Folder path does not exist or is not a directory.")
		folder_path = ""

print(f"\nFolder path: {folder_path}\n")

print("Authenticating with Google Photos...")
SCOPES = ['https://www.googleapis.com/auth/photospicker.mediaitems.readonly']
flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
creds = flow.run_local_server(port=8080)
access_token = creds.token
print(f"Authenticated! Access token: {access_token}")

# Create a Picker session
print("Creating Picker session...")
resp = requests.post(
	f'https://photospicker.googleapis.com/v1/sessions',
	headers={
		'Authorization': f'Bearer {access_token}',
		'Content-Type': 'application/json'
	}
)

# Open the Picker URL in the default web browser
session_id = resp.json()['id']
picker_url = resp.json()['pickerUri']
if picker_url:
	print(f"Opening Picker URL: {picker_url}")
	webbrowser.open(picker_url)
else:
	print("Error: No pickerUri returned from session creation.")
	exit(1)

print("Press ENTER after you have completed your selection in the Picker...")
input()

# Fetch media metadata for selected items
print("Fetching media items...")
nextpage_token = ''
timestamps = {}
while True:
	print("Fetching a page of media items...")
	mediaitems_response = requests.get(
		f'https://photospicker.googleapis.com/v1/mediaItems?sessionId={session_id}&pageSize=100&pageToken={nextpage_token}',
		headers={
			'Authorization': f'Bearer {access_token}',
			'Content-Type': 'application/json'
		}
	)

	if mediaitems_response.status_code == 200:
		media_items = mediaitems_response.json()['mediaItems']
		for picked_media_item in media_items:
			item_id = picked_media_item['id']
			creation_time = picked_media_item['createTime']
			filename = picked_media_item['mediaFile']['filename']
			timestamps[filename] = creation_time

		nextpage_token = mediaitems_response.json().get('nextPageToken')

		if not nextpage_token:
			break
	else:
		print(f"Error fetching media items: {mediaitems_response.status_code} - {mediaitems_response.text}")
		exit(1)

print(timestamps)

# Delete the session
print("Deleting the Picker session...")
delete_resp = requests.delete(
	f'https://photospicker.googleapis.com/v1/sessions/{session_id}',
	headers={
		'Authorization': f'Bearer {access_token}',
		'Content-Type': 'application/json'
	}
)

# Helper function to update file timestamps
def set_file_date(file_name, iso_time):
	file_path = os.path.join(folder_path, file_name)
	
	if not os.path.exists(file_path):
		print(f"Warning: File {file_name} not found on disk. Skipping...")
		return
	
	# Parse ISO 8601 timestamp (with or without milliseconds)
	try:
		# Attempt to parse with milliseconds
		creation_time = datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
	except ValueError:
		# Fallback to parsing without milliseconds
		creation_time = datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%SZ").timestamp()
	
	# Update file times
	try:
		from win32_setctime import setctime
		setctime(file_path, creation_time)  # Set creation time (Windows)
		os.utime(file_path, (creation_time, creation_time))  # Set access/modification times
		print(f"✓ {file_name}: {datetime.fromtimestamp(creation_time)}")
	except Exception as e:
		print(f"✗ {file_name}: Failed to set time - {e}")

# Process selected media items
print(f"\nUpdating file timestamps...\n")

files_updated = 0
files_skipped = []

for filename in os.listdir(folder_path):
	if filename in timestamps:
		set_file_date(filename, timestamps[filename])
		files_updated += 1
	else:
		files_skipped.append(filename)

# Report results
print(f"\n{'='*50}")
print(f"Summary: {files_updated} file(s) updated")

if files_skipped:
	print(f"Skipped {len(files_skipped)} file(s) which didn't have a corresponding timestamp in Google (or you didn't choose them in the Picker):")
	for f in files_skipped:
		print(f"  - {f}")

print(f"{'='*50}")
print("Done!")
