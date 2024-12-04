import bpy
import xml.etree.ElementTree as ET
import os
import logging
from typing import List, Dict, Any, Tuple

bl_info = {
    "name": "Enhanced FCPXML Importer",
    "author": "tintwotin",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "File > Import > FCPXML (.xml)",
    "description": "Import FCPXML files with advanced media resolution and sequence handling",
    "warning": "",
    "category": "Sequencer",
    "support": "COMMUNITY",
}

class MediaResolver:
    def __init__(self, base_paths: List[str]):
        """
        Initialize media resolver with multiple search paths
        
        Args:
            base_paths (List[str]): List of directories to search for media files
        """
        self.search_paths = base_paths
        self.file_cache = self._build_file_cache()
        self.logger = logging.getLogger(__name__)
    
    def _build_file_cache(self) -> Dict[str, str]:
        """
        Build comprehensive file cache across all search paths
        
        Returns:
            Dict[str, str]: Mapping of normalized filenames to full paths
        """
        file_cache = {}
        for path in self.search_paths:
            if not os.path.exists(path):
                continue
            
            for root, _, files in os.walk(path):
                for filename in files:
                    normalized_name = os.path.normcase(filename)
                    full_path = os.path.normpath(os.path.join(root, filename))
                    file_cache[normalized_name] = full_path
        
        return file_cache
    
    def resolve_media_path(self, original_path: str) -> str:
        """
        Resolve media file path with multiple fallback strategies
        
        Args:
            original_path (str): Original media file path from FCPXML
        
        Returns:
            str: Resolved absolute path to media file or empty string
        """
        # Extract base filename
        filename = os.path.basename(original_path)
        normalized_name = os.path.normcase(filename)
        
        # Direct cache lookup
        if normalized_name in self.file_cache:
            return self.file_cache[normalized_name]
        
        # Partial name matching
        matches = [
            path for name, path in self.file_cache.items() 
            if normalized_name in name
        ]
        
        return matches[0] if matches else ""

class FCPXMLParser:
    @staticmethod
    def parse(filepath: str) -> List[Dict[str, Any]]:
        """
        Parse FCPXML file and extract sequence information
        
        Args:
            filepath (str): Path to FCPXML file
        
        Returns:
            List[Dict[str, Any]]: List of parsed sequences
        """
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            sequences = []
            for sequence in root.findall(".//sequence"):
                seq_data = FCPXMLParser._extract_sequence_data(sequence)
                sequences.append(seq_data)
            
            return sequences
        except ET.ParseError as e:
            logging.error(f"XML Parse Error: {e}")
            return []
    
    @staticmethod
    def _extract_sequence_data(sequence: ET.Element) -> Dict[str, Any]:
        """
        Extract detailed sequence data from XML element
        
        Args:
            sequence (ET.Element): XML sequence element
        
        Returns:
            Dict[str, Any]: Parsed sequence metadata and track information
        """
        seq_name = sequence.find("name").text if sequence.find("name") is not None else "Unnamed Sequence"
        duration = int(sequence.find("duration").text or 0)
        rate = int(sequence.find("rate/timebase").text or 30)
        
        width = int(sequence.find(".//samplecharacteristics/width").text or 1920)
        height = int(sequence.find(".//samplecharacteristics/height").text or 1080)
        
        tracks = []
        for track in sequence.findall(".//track"):
            track_clips = []
            for clip in track.findall("clipitem"):
                clip_data = FCPXMLParser._extract_clip_data(clip)
                track_clips.append(clip_data)
            tracks.append({"clips": track_clips})
        
        return {
            "name": seq_name,
            "duration": duration,
            "rate": rate,
            "width": width,
            "height": height,
            "tracks": tracks
        }
    
    @staticmethod
    def _extract_clip_data(clip: ET.Element) -> Dict[str, Any]:
        """
        Extract detailed clip data from XML element
        
        Args:
            clip (ET.Element): XML clip element
        
        Returns:
            Dict[str, Any]: Parsed clip metadata
        """
        return {
            "type": "video" if clip.find(".//media/video") is not None else "audio",
            "name": clip.find("name").text if clip.find("name") is not None else "Unnamed Clip",
            "start": int(clip.find("start").text or 0),
            "end": int(clip.find("end").text or 0),
            "in_frame": int(clip.find("in").text or 0),
            "out_frame": int(clip.find("out").text or 0),
            "file_path": clip.find(".//file/pathurl").text if clip.find(".//file/pathurl") is not None else ""
        }

class FCPXMLImporter:
    @staticmethod
    def configure_scene(context, width: int, height: int, fps: int, duration: int):
        """
        Configure Blender scene settings based on imported sequence
        
        Args:
            context (bpy.context): Blender context
            width (int): Scene width
            height (int): Scene height
            fps (int): Frames per second
            duration (int): Sequence duration
        """
        scene = context.scene
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.fps = fps
        scene.frame_start = 1
        scene.frame_end = int(duration * fps)
        
        if not scene.sequence_editor:
            scene.sequence_editor_create()
    
    @staticmethod
    def import_sequence(context, sequence: Dict[str, Any], media_resolver: MediaResolver):
        """
        Import a single sequence into Blender's VSE
        
        Args:
            context (bpy.context): Blender context
            sequence (Dict[str, Any]): Parsed sequence data
            media_resolver (MediaResolver): Media file path resolver
        
        Returns:
            List[str]: List of missing media files
        """
        FCPXMLImporter.configure_scene(
            context, 
            sequence['width'], 
            sequence['height'], 
            sequence['rate'], 
            sequence['duration']
        )
        
        missing_files = []
        vse = context.scene.sequence_editor
        video_channel, audio_channel = 2, 1
        
        for track in sequence['tracks']:
            for clip in track['clips']:
                resolved_path = media_resolver.resolve_media_path(clip['file_path'])
                
                if not resolved_path:
                    missing_files.append(clip['file_path'])
                    continue
                
                strip_method = (
                    vse.sequences.new_movie 
                    if clip['type'] == 'video' 
                    else vse.sequences.new_sound
                )
                
                strip = strip_method(
                    name=clip['name'],
                    filepath=resolved_path,
                    channel=video_channel if clip['type'] == 'video' else audio_channel,
                    frame_start=clip['start']
                )
                
                strip.frame_final_end = clip['start'] + (clip['out_frame'] - clip['in_frame'])
                strip.frame_start = clip['start'] - clip['in_frame']
                strip.frame_offset_start = clip['start']
                strip.frame_final_duration = clip['out_frame'] - clip['in_frame']
        
        return missing_files

class SEQUENCER_OT_import_fcpxml(bpy.types.Operator):
    """Import FCPXML files with advanced media resolution"""
    bl_idname = "sequencer.import_enhanced_fcpxml"
    bl_label = "Import FCPXML"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    search_paths: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    
    def execute(self, context):
        base_path = os.path.dirname(self.filepath)
        search_paths = [base_path] + [path.name for path in self.search_paths]
        
        media_resolver = MediaResolver(search_paths)
        sequences = FCPXMLParser.parse(self.filepath)
        
        missing_files = []
        for sequence in sequences:
            sequence_missing = FCPXMLImporter.import_sequence(context, sequence, media_resolver)
            missing_files.extend(sequence_missing)
        
        if missing_files:
            self.report({'WARNING'}, f"Missing files: {len(missing_files)}")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(SEQUENCER_OT_import_fcpxml.bl_idname, text="Enhanced FCPXML (.xml)")

def register():
    bpy.utils.register_class(SEQUENCER_OT_import_fcpxml)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(SEQUENCER_OT_import_fcpxml)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()