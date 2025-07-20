import os

# Tester script to make sure the script works as expected.
# It will list all files in a specified folder and compare them with the files from the Google Photos album.

def get_all_file_names(folder_path):
	try:
		file_names = os.listdir(folder_path)
		return file_names
	except FileNotFoundError:
		print(f"The folder '{folder_path}' does not exist.")
		return []
	except Exception as e:
		print(f"An error occurred: {e}")
		return []

# Example usage
folder_path = "E:/1 Video Projects/Snowkiting test"
actual_files = get_all_file_names(folder_path)

# Read file_names_test.txt into an array called files2
try:
	with open("file_names_test.txt", "r") as file:
		gphotos_files = [line.strip() for line in file.readlines()]
except FileNotFoundError:
	print("The file 'file_names_test.txt' does not exist.")
	gphotos_files = []
except Exception as e:
	print(f"An error occurred while reading the file: {e}")
	gphotos_files = []

# Find items that are in one array but not the other
unique_to_actual_files = set(actual_files) - set(gphotos_files)
unique_to_gphotos = set(gphotos_files) - set(actual_files)

# Print count of items in each array
print(f"Number of items in 'actual_files': {len(actual_files)}")
print(f"Number of items in 'gphotos_files': {len(gphotos_files)}")

# Print the differences
if unique_to_actual_files:
	print("Items in 'actual_files' but not in 'gphotos':", unique_to_actual_files)
if unique_to_gphotos:
	print("Items in 'gphotos' but not in 'actual_files':", unique_to_gphotos)
if not unique_to_actual_files and not unique_to_gphotos:
	print("Both arrays contain the same items.")