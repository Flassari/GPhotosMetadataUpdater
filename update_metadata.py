# Read the README.md file for instructions on how to use this script.
# This script sets the creation date of files in a folder based on their metadata from a Google Photos album.

import os

DELETE_MISSING_FILES = False # Set to True to delete files that are not in the album

album_id='' # <- Fill this with the ID of the album you want to extract metadata from.
# You can find the album ID in the URL of the album in Google Photos, or by using the script to list all albums.
# If you leave it empty, the script will list all albums and ask you to pick one.

folder_path = "" # <- Fill this with the path to the folder containing the files you want to set the creation date for.

all_album_items = {}

def extract_album_info(album_id):
	from google_auth_oauthlib.flow import InstalledAppFlow
	from googleapiclient.discovery import build
	from google.oauth2.credentials import Credentials
	from google.auth.transport.requests import Request

	# Auth flow
	SCOPES = ['https://www.googleapis.com/auth/photoslibrary']
	creds = None
	if os.path.exists('authtoken.cached.json'):
		creds = Credentials.from_authorized_user_file('authtoken.cached.json', SCOPES)
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
			creds = flow.run_local_server(port=8080)
		# Save the credentials for the next run
		with open('authtoken.cached.json', 'w') as token:
			token.write(creds.to_json())

	# Build the API service
	service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)

	if album_id is None:
		# Get a list of all photo albums
		albums_results = service.albums().list(pageSize=100).execute()
		albums = albums_results.get('albums', [])

		# Print album details
		for album in albums:
			print(album['title'])
			print(f"\t ID: {album['id']}")
		
		print("Pick one of the albums and populate the album_id variable with it.")
		exit(1)

	# Get the album details
	album = service.albums().get(albumId=album_id).execute()

	# Print album details
	print(f"Album title: {album['title']}")
	print(f"Number of media items: {album['mediaItemsCount']}")

	nextPageToken = None
	current_page = 1

	while True:
		print(f"Page {current_page}")
		current_page += 1
		
		media_items = service.mediaItems().search(body={'albumId': album_id, 'pageSize': 100, 'pageToken': nextPageToken}).execute()
		for item in media_items.get('mediaItems', []):
			if (item['filename'] in all_album_items):
				print(f"!!!!!!!!!! File {item['filename']} ({item['mimeType']}) already exists in file_dates. Skipping...")
				continue

			all_album_items[item['filename']] = item

		if not "nextPageToken" in media_items:
			break
		nextPageToken = media_items["nextPageToken"]


	with open('all_data.json', 'w') as f:
		import json
		json.dump(all_album_items, f, indent=4)

def set_file_date(file_name):
	from datetime import datetime
	
	file_path = os.path.join(folder_path, file_name)
	item_info = all_album_items[file_name]

	iso_time = item_info['mediaMetadata']['creationTime']
	creation_time = 0

	if not item_info:
		print(f"File {file_name} not found in all_album_items. Skipping...")
		return
	
	# convert ISO 8601 format to timestamp
	try:
		# Attempt to parse with milliseconds
		creation_time = datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
	except ValueError:
		# Fallback to parsing without milliseconds
		creation_time = datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%SZ").timestamp()

	from win32_setctime import setctime
	setctime(file_path, creation_time) # Set creation time
	os.utime(file_path, (creation_time, creation_time)) # Set access and modification time
	print(f"Setting file {file_path} creation time to {creation_time}.")


# try to read and parse all_data.json
try:
	import json

	ITEM_CACHE_FILENAME = 'all_data.json'
	if os.path.exists(ITEM_CACHE_FILENAME):
		with open(ITEM_CACHE_FILENAME, 'r') as f:
			all_album_items = json.load(f)
except Exception as e:
	print(f"Couldn't read all_data.json. Error: {e}")


if not all_album_items:
	print("No data found in all_data.json. Downloading it from Google Photos API.")
	extract_album_info(album_id)
else:
	print("Using cached photo album data found in all_data.json. To refresh, delete all_data.json and run the script again.")

actual_files = os.listdir(folder_path)
no_metadata_files = []

for file in actual_files:
	if file in all_album_items:
		set_file_date(file)
	else:
		no_metadata_files.append(file)


for file in no_metadata_files:
	if DELETE_MISSING_FILES:
		print(f"File {file} does not exist in the album. Deleting it.")
		file_path = os.path.join(folder_path, file)
		os.remove(file_path)
	else:
		print(f"File {file} does not exist in the album. Re-run this script with DELETE_MISSING_FILES set to True to delete it.")

print(f"All done!")