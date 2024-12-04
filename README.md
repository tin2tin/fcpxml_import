# FCPXML Importer for Blender
This Blender addon allows you to import FCPXML files (Final Cut Pro XML) into Blender's Video Sequence Editor (VSE). It extracts video, audio, transitions, and nested sequences from the FCPXML file and places them into Blender's timeline.

# Features:
- Import FCPXML files: Import all types of media including video, audio, and nested sequences.
- Search for missing files: Automatically search for missing media files by specifying a folder where Blender will look for them.
- Scene Configuration: Automatically sets the scene resolution, FPS, and duration based on the FCPXML file.
- Video and Audio Strips: Adds video or audio strips to Blender’s Video Sequence Editor.

![image](https://github.com/user-attachments/assets/55f9d7fe-1d63-4185-9f7d-09c79cf646ff)


# Requirements:
- Blender 3.0 or later (the addon is compatible with Blender 3.0+).
- Final Cut Pro XML (FCPXML) file to import the media and sequences.

# Installation
- Download the Script: https://github.com/tin2tin/fcpxml_import/archive/refs/heads/main.zip

### Install the Addon:
- Open Blender.
- Go to Edit → Preferences → Add-ons → Install...
- Browse for the downloaded zip file and click Install Add-on.

### Enable the Addon:
- Once installed, search for "FCPXML Importer" in the Add-ons tab.
- Enable the addon by checking the box next to it.

## Usage Instructions
- Open the Video Sequence Editor (VSE) in Blender:
- Go to Video Editing workspace.

### Import the FCPXML file:
- This script will add an option to the File menu for importing FCPXML files.
- Click on File → Import → FCPXML (.xml).
- Select the FCPXML file you wish to import.

### Specify a Search Folder (Optional):
- If there are missing media files (e.g., video/audio files that can't be found by their paths in the FCPXML), a search dialog will appear.
- You will be prompted to provide a folder that Blender can use to search for the missing files. Blender will look through all the files in that folder to resolve missing media.

### Check the Console:
- The script will output messages in Blender’s system console. You can see details about which files were indexed, searched, and any missing files.

#### Important Notes:
- Search Folder: If you provide a search folder, the addon will use it to attempt to resolve missing files. If no folder is specified, missing files will not be resolved.
- Scene Configuration: The script automatically sets the resolution and FPS based on the FCPXML, so no need to adjust these manually.
