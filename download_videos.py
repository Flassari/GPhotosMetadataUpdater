# Read the README.md file for instructions on how to use this script.
# This script sets the creation date of files in a folder based on their metadata from Google Photos.
# Uses the Photos Picker API for selecting media items.

import os
import shutil
import urllib
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests
from google_auth_oauthlib.flow import InstalledAppFlow

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

def filename_exists(file_path):
	return os.path.exists(file_path)

def unique_filename(file_name):
	new_file_name = file_name
	if any(video['filename'] == new_file_name for video in video_items):
		base_name, ext = os.path.splitext(new_file_name)
		counter = 1
		while True:
			new_file_name = f"{base_name}_{counter}{ext}"
			if not any(video['filename'] == new_file_name for video in video_items):
				return new_file_name
			counter += 1
	
	return new_file_name

# Fetch media metadata for selected items
print("Fetching media items...")
nextpage_token = ''
video_items = []
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
			if picked_media_item['type'] == "VIDEO":
				item_status = picked_media_item['mediaFile']['mediaFileMetadata']['videoMetadata']['processingStatus']
				if item_status != "READY":
					print(f"Error: Video {picked_media_item['mediaFile']['filename']} is not ready for download (status: {item_status}).")
					exit(1)
				
				video_items.append({
					'itemId': picked_media_item['id'],
					'filename': unique_filename(picked_media_item['mediaFile']['filename']),
					'baseUrl': picked_media_item['mediaFile']['baseUrl'],
					'creationTime': picked_media_item['createTime']
				})

		nextpage_token = mediaitems_response.json().get('nextPageToken')

		if not nextpage_token:
			break
	else:
		print(f"Error fetching media items: {mediaitems_response.status_code} - {mediaitems_response.text}")
		exit(1)



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
	except Exception as e:
		print(f"{file_name}: Failed to set time - {e}")

# Function to download video files
def download_video(url, file_name, creation_time):
	full_file_path = os.path.join(folder_path, file_name)
	if filename_exists(full_file_path):
		print(f"{file_name}: File already exists. Skipping download.")
		return True

	download_url = f"{url}=dv" # =dv for download video
	request = urllib.request.Request(download_url, headers={
		'Authorization': f'Bearer {access_token}',
		'Content-Type': 'application/json'
	})
	
	ATTEMPTS_COUNT = 5
	for attempt in range(ATTEMPTS_COUNT):
		try:
			with urllib.request.urlopen(request) as response:
				with open(full_file_path, "wb") as out_file:
					shutil.copyfileobj(response, out_file)
					set_file_date(full_file_path, creation_time)
			return True

		except Exception as e:
			print(f"{file_name}: Error downloading on attempt {attempt+1}/{ATTEMPTS_COUNT} - {e}")

	return False


# Process selected media items
print(f"\nDownloading and updating metadata for {len(video_items)} video(s) in parallel...\n")

total_videos = len(video_items)
max_workers = max(1, min(32, total_videos))
failure_count = 0

with ThreadPoolExecutor(max_workers=max_workers) as executor:
	futures = {executor.submit(download_video, video['baseUrl'], video['filename'], video['creationTime']): video for video in video_items}
	for completed_count, future in enumerate(as_completed(futures), 1):
		video = futures[future]
		filename = video['filename']
		try:
			success = future.result()
			if success:
				print(f"Completed {completed_count}/{total_videos} - {filename}")
			else:
				print(f"Failed {completed_count}/{total_videos} - {filename}")
				failure_count += 1
		except Exception as e:
			print(f"{filename}: Processing failed - {e}")

# Report results
print(f"\n{'='*50}")
print(f"Summary: {len(video_items) - failure_count} video(s) downloaded.")
if failure_count > 0:
	print(f"{failure_count} video(s) failed to download.")
print(f"{'='*50}")
print("Done!")
