import bpy
import xml.etree.ElementTree as ET
import os

bl_info = {
    "name": "FCPXML Importer",
    "blender": (3, 0, 0),
    "category": "Sequencer",
    "description": "Import FCPXML files including video, audio, transitions, and nested sequences into Blender's Video Sequence Editor.",
    "author": "tintwotin",
    "version": (1, 0, 0),
    "location": "File > Import > FCPXML (.xml)",
    "warning": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "wiki_url": "",
    "doc_url": "",
}

class FilePathIndex:
    def __init__(self, search_paths):
        self.search_paths = search_paths
        self.file_index = self.build_index(search_paths)
    
    def build_index(self, paths):
        """Build a cache index of all files in the search paths."""
        file_index = {}
        for path in paths:
            print(f"Indexing path: {path}")  # Debug print to show the paths being indexed
            for root, dirs, files in os.walk(path):
                for file in files:
                    lower_case_name = file.lower()
                    file_index[lower_case_name] = os.path.join(root, file)
        print(f"Index built with {len(file_index)} files.")  # Debug print to show number of files indexed
        return file_index
    
    def find_file(self, filename):
        """Find a file in the indexed directories, case insensitive."""
        lower_case_name = os.path.basename(filename.lower())
        print(f"Searching for file: {filename}")  # Debug print to show which file is being searched
        resolved_path = self.file_index.get(lower_case_name, None)
        #resolved_path = self.file_index.find_file(os.path.basename(file_path))
        if resolved_path:
            print(f"File found: {resolved_path}")  # Debug print to show if the file was found
        else:
            print(f"File not found: {filename}")  # Debug print to show if the file was not found
        return resolved_path

def parse_fcpxml(filepath):
    """Parse the FCPXML file and extract relevant data."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    sequences = []
    
    for sequence in root.findall(".//sequence"):
        seq_name = sequence.find("name").text
        duration = int(sequence.find("duration").text)
        rate = int(sequence.find("rate/timebase").text)
        width = int(sequence.find(".//samplecharacteristics/width").text)
        height = int(sequence.find(".//samplecharacteristics/height").text)
        
        tracks = []
        
        for track in sequence.findall(".//track"):
            clips = []
            
            for clip in track.findall("clipitem"):
                clip_type = "video" if clip.find(".//media/video") is not None else "audio"
                clip_name = clip.find("name").text
                start = int(clip.find("start").text)
                end = int(clip.find("end").text)
                file_path = clip.find(".//file/pathurl").text
                in_frame = int(clip.find("in").text) if clip.find("in") is not None else 0
                out_frame = int(clip.find("out").text) if clip.find("out") is not None else end
                
                clips.append({
                    "type": clip_type,
                    "name": clip_name,
                    "start": start,
                    "end": end,
                    "in": in_frame,
                    "out": out_frame,
                    "file_path": file_path
                })
            
            tracks.append({"clips": clips})
        
        sequences.append({
            "name": seq_name,
            "duration": duration,
            "rate": rate,
            "width": width,
            "height": height,
            "tracks": tracks
        })
    
    return sequences


def configure_scene(context, width, height, fps, duration):
    """Configure the scene settings such as resolution and FPS."""
    scene = context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = int(duration * fps)  # Set the frame_end based on sequence duration
    scene.sequence_editor_create()


def import_fcpxml(context, filepath, report_error, search_paths=None):
    """Main function to import the FCPXML into Blender."""
    base_dir = os.path.dirname(filepath)
    sequences = parse_fcpxml(filepath)
    
    missing_files = {}  # Store missing file information
    
    # If search_paths are provided, use them to find missing files
    file_index = FilePathIndex(search_paths or [])  # Initialize file index
    
    print(f"Initial search paths: {search_paths}")  # Debug print
    
    for seq in sequences:
        configure_scene(context, seq['width'], seq['height'], seq['rate'], seq['duration'])
        
        vse = bpy.context.scene.sequence_editor
        video_channel = 2
        audio_channel = 1
        
        for track in seq['tracks']:
            for clip in track['clips']:
                file_path = clip['file_path']
                
                # Check if the file path is missing or invalid
                print(f"Checking file: {file_path}")  # Debug print
                
                if not file_path or file_path == "None":
                    print(f"Missing file: {file_path}")  # Debug print
                    missing_files[clip['file_path']] = [base_dir]
                    continue
                
                # Normalize file path to absolute path
                file_path = bpy.path.abspath(file_path)
                
                if not os.path.isabs(file_path):
                    file_path = os.path.join(base_dir, file_path)
                
                # Check file existence in the index (optimized)
                resolved_path = file_index.find_file(file_path)
                
                if resolved_path and os.path.isfile(resolved_path):
                    print(f"Found file: {resolved_path}")  # Debug print
                    file_path = resolved_path
                else:
                    print(f"File missing: {file_path}")  # Debug print
                    missing_files[clip['file_path']] = [base_dir]
                    continue
                
                # Create video or sound strip
                if clip['type'] == 'video':
                    strip = vse.sequences.new_movie(
                        name=clip['name'],
                        filepath=file_path,
                        channel=video_channel,
                        frame_start=clip['start']
                    )
                    strip.frame_final_end = clip['start'] + (clip['out'] - clip['in'])
                    strip.frame_start = clip['start'] - clip['in']
                    strip.frame_offset_start = clip['start']
                    strip.frame_final_duration = clip['out'] - clip['in']
                    strip.channel = video_channel
                else:
                    strip = vse.sequences.new_sound(
                        name=clip['name'],
                        filepath=file_path,
                        channel=audio_channel,
                        frame_start=clip['start']
                    )
                    strip.frame_final_end = clip['start'] + (clip['out'] - clip['in'])
                    strip.frame_start = clip['start'] - clip['in']
                    strip.frame_offset_start = clip['start']
                    strip.frame_final_duration = clip['out'] - clip['in']
                    strip.channel = audio_channel
    
    return {'FINISHED'}, missing_files


class FCPXMLImportOperator(bpy.types.Operator):
    """Operator to import FCPXML"""
    bl_idname = "sequencer.import_fcpxml"
    bl_label = "Import FCPXML"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    search_path: bpy.props.StringProperty(
        name="Search Folder",
        description="Folder to search for missing files",
        subtype='DIR_PATH'
    )
    
    def execute(self, context):
        # Ensure the search path is passed correctly
        search_paths = [self.search_path] if self.search_path else []
        result, missing_files = import_fcpxml(context, self.filepath, self.report, search_paths)
        
        if missing_files:
            self.report({'WARNING'}, f"Missing files: {', '.join(set(missing_files.keys()))}")
            return self.invoke_search(context)
        
        return result
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def invoke_search(self, context):
        """If missing files were found, show browser folder"""
        print("Missing files found, invoking search dialog.")  # Debug print
        context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "search_path", text="Search Folder")
    
def menu_func_import(self, context):
    self.layout.operator(FCPXMLImportOperator.bl_idname, text="FCPXML (.xml)")

def register():
    bpy.utils.register_class(FCPXMLImportOperator)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(FCPXMLImportOperator)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()