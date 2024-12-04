# FCPXML Importer for Blender (Enhanced Version)

This Blender addon allows you to import FCPXML files (Final Cut Pro XML) into Blender's Video Sequence Editor (VSE). It extracts video, audio, transitions, and nested sequences from the FCPXML file and places them into Blender's timeline.

---

## Key Features:
- **Enhanced FCPXML Import:** Import all types of media, including video, audio, and nested sequences, with advanced parsing.
- **Advanced Media Resolution:** Search and resolve missing media files from multiple search paths with partial filename matching.
- **Scene Configuration:** Automatically sets the scene resolution, FPS, and duration based on the FCPXML file.
- **Video and Audio Strips:** Seamlessly adds video or audio strips to Blender’s Video Sequence Editor.
- **Error Handling and Logging:** Detailed console messages for media resolution, missing files, and sequence imports.

---

## Requirements:
- Blender 3.0 or later (the addon is compatible with Blender 3.0+).
- A Final Cut Pro XML (FCPXML) file to import media and sequences.

---

## Installation:
- Download from my Fork

### Install the Addon:
1. Open Blender.
2. Navigate to **Edit → Preferences → Add-ons → Install...**
3. Browse to the downloaded zip file and click **Install Add-on**.

### Enable the Addon:
1. Search for "FCPXML Importer" in the Add-ons tab.
2. Enable the addon by checking the box next to it.

---

## Usage Instructions:
### Import the FCPXML file:
1. Open the **Video Sequence Editor (VSE)** in Blender.
2. Navigate to the **Video Editing** workspace.
3. Click **File → Import → Enhanced FCPXML (.xml)**.
4. Select the FCPXML file you wish to import.

### Specify a Search Folder (Optional):
- If there are missing media files (e.g., video/audio files that can't be found by their paths in the FCPXML), a search dialog will appear.
- Provide a folder where Blender will search for the missing files. Blender will resolve partial matches for file paths when possible.

### Check the Console:
- Details about imported files, indexed paths, and missing media will appear in Blender’s system console.

---

## Key Improvements (Enhanced Version):
- **Improved Media Resolution:** Supports multiple search paths and partial filename matching.
- **Enhanced XML Parsing:** Modular parsing for sequences, tracks, and clips.
- **Better Error Handling:** Informative logging and feedback for missing or unresolved media.
- **Improved Scene Configuration:** Automatically adjusts resolution, FPS, and sequence duration.
- **Modular Design:** Clear separation of concerns for parsing, resolving, and importing media.

---

This enhanced version offers greater reliability and flexibility for FCPXML imports into Blender. Enjoy an improved and streamlined experience for integrating Final Cut Pro projects into Blender!
"""

# Write the updated content back to the README file
with open(readme_path, "w") as file:
    file.write(updated_readme_content)

"README.md successfully updated."
