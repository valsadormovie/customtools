#----------------------------------------------------------
#-GLOBAL_SETTINGS.py
#----------------------------------------------------------
#  ================== IMPORTED LIBRARYS ================== 
import importlib
import inspect
import datetime
import random
import string
import json
import bpy
import os
import time
import threading
import keyboard
import sys
import bmesh
from pathlib import Path
from bpy.props import EnumProperty, StringProperty, BoolProperty
from mathutils import Vector, Quaternion
from bpy import context


# ================== THIRDPARTY MODULE LIBRARYS ==================
import grapheme
import numpy as np
from mathutils.kdtree import KDTree
from alive_progress import alive_bar
from about_time import about_time
from colorist import hex, bg_hex, ColorHex, BgColorHex


# ================== REGISTERED PANEL TOOLS ==================
panels = [
    "global_settings",
    "modifiertools_panel",
    "transformtools_panel",
    "vertexgrouptools_panel",
    "utilitytools_panel",
    "tiletools_panel",
    "scriptrunner_panel"
]


# ================== MAIN PANEL SCRIPTS ==================
panel_visibility = {panel: True for panel in panels}
registered_classes = []
global_functions = {}
registered_properties = []
global_settings = None


# ================== GLOBAL SETTINGS PANEL ==================
class XTD_GlobalSettingsPanel(bpy.types.Panel):
    bl_label = "GLOBAL SETTINGS"
    bl_idname = "XTD_PT_global_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        box = layout.box()
        row = box.row(align=True)
        row.scale_y = 0.5
        row.label(text="BATCH PROCESS SETTINGS", icon="MOD_MULTIRES")

        row = box.row(align=True)
        row.scale_y = 0.5
        row.prop(scene, "batch_mode", text="MODE")

        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.use_property_split = True
        row.use_property_decorate = False
        row.label(text="", icon='EXPORT')
        row.prop(scene, "export_ply", expand=True)

        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.use_property_split = True
        row.use_property_decorate = False
        row.label(text="", icon='SYSTEM')
        row.prop(scene, "shutdown_after", expand=True)

        row = box.row(align=True)
        row.separator()
        row.operator("xtd_tools.reloadapp", text="RELOAD APP", icon="RECOVER_LAST")

        row = box.row(align=True)
        row.separator()
        row.prop(scene, "tool_visibility_mode", expand=True)

        row = layout.row()
        row.alignment = 'LEFT'
        row.prop(scene, "xtd_tools_activepanels", text="ACTIVE PANELS", emboss=False, icon_only=True, 
                 icon="TRIA_DOWN" if scene.xtd_tools_activepanels else "TRIA_RIGHT")
        if scene.xtd_tools_activepanels:
            box = layout.box()
            for panel in panels:
                if panel == "global_settings":
                    continue
                prop_name = f"show_{panel}"
                row = box.row(align=True)
                row.alignment = 'EXPAND'
                row.use_property_decorate = False
                label_text = panel.replace("_panel", "").replace("_", " ").title()
                row.prop(scene, prop_name, text=label_text, icon="TOOL_SETTINGS")


# ================== GLOBAL EXECUTE OPERATOR ==================
class XTDToolsOperator(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}
    batch_mode = False
    _processed_objects = set()
    
    def execute(self, context):
        bl_label = self.bl_label
        self.__class__._processed_objects.clear()
        bpy.context.preferences.edit.use_global_undo = False
        
        selected_objects = bpy.context.selected_objects
       
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}
        
        keyboard.add_hotkey("esc", ProcessManager.stop)
        ProcessManager.start()

        batch_size = int(bpy.context.scene.batch_mode)
        total_objects = len(selected_objects)
        total_batches = (total_objects + batch_size - 1) // batch_size

        start_time = time.time()

        for batch_index in range(total_batches):
            batch_objects = selected_objects[batch_index * batch_size: (batch_index + 1) * batch_size]
            if not ProcessManager.is_running():
                self.report({'INFO'}, "Process stopped by user.")
                bpy.context.preferences.edit.use_global_undo = True
                return {'CANCELLED'}
            statusheader(bl_label, functiontext="Working selected objects...")
            if total_batches > 1: 
                print_status(batch_index + 1, total_batches, total_objects, batch_index * batch_size + len(batch_objects))
            with alive_bar(len(batch_objects), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
                for obj in batch_objects:
                    if not ProcessManager.is_running():
                        self.report({'INFO'}, "Process stopped by user.")
                        bpy.context.preferences.edit.use_global_undo = True
                        return {'CANCELLED'}
                    self.process_object(obj)
                    self.__class__._processed_objects.add(obj.name)
                    bpy.context.preferences.edit.use_global_undo = True
                    bar()

            if bpy.context.scene.export_ply == "YES":
                export_dir = os.path.dirname(bpy.data.filepath)
                for obj in batch_objects:
                    export_ply_object(obj, export_dir)
                        
        if bpy.context.scene.shutdown_after == "YES":
            threading.Thread(target=shutdown_computer).start()

        ProcessManager.reset()
        self.report({'INFO'}, "Process completed.")
        bpy.context.preferences.edit.use_global_undo = True
        return {'FINISHED'}

    def process_object(self, obj):
        raise NotImplementedError("Subclasses must implement process_object method")


# ================== PROCESS MANAGER ==================
class ProcessManager:
    _is_running = True

    @classmethod
    def is_running(cls):
        return cls._is_running

    @classmethod
    def stop(cls):
        cls._is_running = False
        print("Folyamat leállítva.")
        bpy.context.preferences.edit.use_global_undo = True

    @classmethod
    def start(cls):
        cls._is_running = True

    @classmethod
    def reset(cls):
        cls._is_running = True
        bpy.context.preferences.edit.use_global_undo = True


# ================== VisibilityController ==================
class VisibilityController:
    @classmethod
    def check_visibility(cls, context, panel_name, require_selected=False, require_active=False, require_prefix=None):
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.view_layer.objects.active
        visibility_mode = bpy.context.scene.tool_visibility_mode

        if visibility_mode == 'DEFAULT':
            return getattr(bpy.context.scene, f"show_{panel_name}", True)

        if visibility_mode == 'INTUITIVE':
            panel_visibility_state = getattr(bpy.context.scene, f"show_{panel_name}", True)
            if not panel_visibility_state:
                return False

            if require_selected and not selected_objects:
                return False

            if require_active and not active_object:
                return False

            if require_prefix:
                prefix = "SM_"
                if require_selected and not any(obj.name.startswith(prefix) for obj in selected_objects):
                    return False
                if require_active and (not active_object or not active_object.name.startswith(prefix)):
                    return False

        return True
    
    @classmethod
    def get_panel_class_name(cls, panel_name):
        return "XTD_PT_" + panel_name.split("_panel")[0].replace("_", " ").capitalize()

    @classmethod
    def toggle_panel_visibility(cls, panel_name, visible):
        panel_class_name = cls.get_panel_class_name(panel_name)
        panel_visibility[panel_name] = visible
        for cls in bpy.types.Panel.__subclasses__():
            if cls.__name__ == panel_class_name:
                cls.poll = lambda self, context: cls.check_visibility(context, panel_name)

    @classmethod
    def update_visibility(cls, panel=None):
        if bpy.context.scene.tool_visibility_mode == 'DEFAULT':
            if panel:
                panel_visibility[panel] = getattr(bpy.context.scene, f"show_{panel}", True)
            else:
                for panel_name in panels:
                    panel_visibility[panel_name] = getattr(bpy.context.scene, f"show_{panel_name}", True)
        else:
            if panel:
                cls.toggle_panel_visibility(panel, getattr(bpy.context.scene, f"show_{panel}", True))
            else:
                for panel_name in panels:
                    cls.toggle_panel_visibility(panel_name, getattr(bpy.context.scene, f"show_{panel_name}", True))

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

bpy.types.Scene.tool_visibility_mode = bpy.props.EnumProperty(
    items=[
        ('INTUITIVE', "Intuitive", ""),
        ('DEFAULT', "Default", ""),
        
    ],
    name="Tool Visibility Mode",
    default="DEFAULT"
)


# ================== UUIDManager ==================
class UUIDManager:
    @staticmethod
    def parse_project_uuid(project_uuid):
        if not project_uuid or "|" not in project_uuid:  # Ha üres vagy rossz formátumú
            return {
                "uuid_working_project": "",
                "uuid_base_tile_name": "",
                "uuid_source_blendfile": "",
                "uuid_transfertime": "",
                "uuid_transfermode": "",
                "uuid_unique_hash": ""
            }
        
        parts = project_uuid.split("|")
        return {
            "uuid_working_project": parts[0] if len(parts) > 0 else "",
            "uuid_base_tile_name": parts[1] if len(parts) > 1 else "",
            "uuid_source_blendfile": parts[2] if len(parts) > 2 else "",
            "uuid_transfertime": parts[3] if len(parts) > 3 else "",
            "uuid_transfermode": parts[4] if len(parts) > 4 else "",
            "uuid_unique_hash": parts[5] if len(parts) > 5 else ""
        }


    @staticmethod
    def generate_random_hash(length=8):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    @staticmethod
    def ensure_project_uuid():
        project_filename = os.path.basename(bpy.data.filepath).replace(".blend", "")

        for obj in bpy.data.objects:
            if "project_uuid" not in obj or not obj["project_uuid"]:
                unique_id = f"{obj.name[:12]}|{project_filename}"
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                obj["project_uuid"] = f"{project_filename}|{unique_id}|{timestamp}|APPEND|{UUIDManager.generate_random_hash()}"

    @staticmethod
    def deduplicate_project_uuids():
        seen_uuids = {}
        
        for obj in bpy.data.objects:
            if not obj.get("project_uuid"):
                uuid_data = UUIDManager.parse_project_uuid(obj["project_uuid"])
                if uuid_data["uuid_transfermode"] != "LINK":
                    base_uuid = "|".join(obj["project_uuid"].split("|")[:-1])

                    if base_uuid in seen_uuids and obj["project_uuid"] == seen_uuids[base_uuid]:
                        obj["project_uuid"] = f"{base_uuid}|{UUIDManager.generate_random_hash()}"
                    else:
                        seen_uuids[base_uuid] = True


# ================== MAIN TRANSFER ENGINE ==================
class XTD_OT_TransferModels(XTDToolsOperator):
    bl_idname = "xtd_tools.transfermodels"
    bl_label = "Transfer Models"
    bl_description = "Transfer models between files"
    bl_options = {'REGISTER', 'UNDO'}

    transfer_mode: bpy.props.EnumProperty(
        items=[('APPEND', "Append", ""), ('LINK', "Link", "")],
        name="Transfer Mode",
        default='APPEND'
    )

    source_mode: bpy.props.EnumProperty(
        items=[('BLENDFILE', "Blend File", ""), ('MASTERFILE', "Master File", "")],
        name="Source Mode",
        default='MASTERFILE'
    )

    file_name: bpy.props.StringProperty(
        name="File Name",
        description="Specify the blend file name for BLENDFILENAME mode",
        default=""
    )

    node_group: bpy.props.StringProperty(
        name="Node Group",
        description="Specify node group",
        default=""
    )

    world: bpy.props.StringProperty(
        name="World",
        description="Specify world",
        default=""
    )

    objects: bpy.props.EnumProperty(
        items=[('SELECTED', "Selected", ""), ('ALL', "All", ""), ('OBJECTNAME', "Object Name", "")],
        name="Objects",
        default='SELECTED'
    )

    replace_mode: bpy.props.EnumProperty(
        items=[('ADD', "Add", ""), ('REPLACE', "Replace", "")],
        name="Replace Mode",
        default='ADD'
    )

    object_name: bpy.props.StringProperty(
        name="Object Name",
        description="Specify an object name for OBJECTNAME mode",
        default=""
    )
    
    zoom_level: bpy.props.StringProperty(
        name="Zoom level",
        description="Zoom level resolution",
        default=""
    )

    base_collection: bpy.props.EnumProperty(
        items=[('TEMP_LINKED', "Temp linked", ""), ('SCENE', "Scene", ""), ('COLLECTIONNAME', "Collectionname", "")],
        name="Collection transfer destination",
        default='TEMP_LINKED'
    )
    
    collection_name: bpy.props.StringProperty(
        name="Collection Name",
        description="Specify collection bane",
        default=""
    )

    def execute(self, context):
        if self.node_group.strip() != "" or self.world.strip() != "":
            result = self.process_utils(context, source_file)
            if 'CANCELLED' in result:
                return result
            self.report({'INFO'}, "Successfully linked node group.")
            return {'FINISHED'}
        else:
            selected_project_uuids = set()
            
            linked_objects = []
    
            if self.objects == 'SELECTED':
                try:
                    selected_objs = [o for o in bpy.context.selected_objects if "project_uuid" in o]

                    selected_base_tile_names = set()
                    for obj in selected_objs:
                        uuid_data = UUIDManager.parse_project_uuid(obj["project_uuid"])
                        if uuid_data and uuid_data["uuid_base_tile_name"]:
                            selected_base_tile_names.add(uuid_data["uuid_base_tile_name"])
                    
                    if self.replace_mode == 'REPLACE':
                        self.replace_existing_objects(selected_base_tile_names)
                    
                    selected_objs = [o for o in bpy.context.selected_objects if "project_uuid" in o]
                    linked_objects = []

                    for obj in selected_objs:
                        uuid_data = UUIDManager.parse_project_uuid(obj["project_uuid"])
                        if not uuid_data["uuid_base_tile_name"]:
                            continue
                        
                        source_file = self.get_source_file_for_object(obj)
                        if not source_file or not os.path.exists(source_file):
                            self.report({'WARNING'}, f"Source file for {obj.name} is invalid or missing.")
                            continue
                        
                        # Itt hívjuk a transfer_objects-t
                        one_uuid_set = {uuid_data["uuid_base_tile_name"]}
                        newly_linked = self.transfer_objects(source_file, one_uuid_set)
                        if newly_linked:
                            linked_objects.extend(newly_linked)

                    if not linked_objects:
                        self.report({'ERROR'}, "No objects were transferred.")
                        return {'CANCELLED'}
                        
                except ValueError:
                    return {'CANCELLED'}
            else:
                source_file = self.get_source_file(context)
                if not source_file or not os.path.exists(source_file):
                    self.report({'ERROR'}, "Blend file path is invalid or missing.")
                    return {'CANCELLED'}

                if self.objects == 'ALL':
                    selected_project_uuids = {"ALL"}
                elif self.objects == 'OBJECTNAME':
                    obj = bpy.data.objects.get(self.object_name)
                    if obj and "project_uuid" in obj:
                        uuid_data = UUIDManager.parse_project_uuid(obj.get("project_uuid", ""))
                        if uuid_data and uuid_data["uuid_base_tile_name"]:
                            selected_project_uuids = {uuid_data["uuid_base_tile_name"]}
                        else:
                            self.report({'ERROR'}, f"Object '{self.object_name}' does not have a valid project_uuid.")
                            return {'CANCELLED'}
                    else:
                        self.report({'ERROR'}, f"Object '{self.object_name}' not found.")
                        return {'CANCELLED'}
                else:
                    self.report({'ERROR'}, "Invalid objects mode selected.")
                    return {'CANCELLED'}

                if self.replace_mode == 'REPLACE':
                    self.replace_existing_objects(selected_project_uuids)

                linked_objects = self.transfer_objects(source_file, selected_project_uuids)
            
            if not linked_objects:
                self.report({'ERROR'}, "No objects were transferred.")
                return {'CANCELLED'}

            self.report({'INFO'}, f"Successfully transferred {len(linked_objects)} objects.")
            return {'FINISHED'}
        
        self.report({'INFO'}, "Transfer process completed.")
        return {'FINISHED'}

    def get_source_file_for_object(self, obj):
        master_folder = os.path.dirname(bpy.context.scene.master_txt_filepath)
        if self.source_mode == 'MASTERFILE':
            master_txt_filepath = bpy.context.scene.master_txt_filepath
            if not os.path.exists(master_txt_filepath):
                print(f"Master TXT file not found: {master_txt_filepath}")
                return None

            with open(master_txt_filepath, 'r') as file:
                lines = file.readlines()

            for line in lines:
                try:
                    name, blendfile, zoom = line.strip().split(" | ")
                    if name == obj.name[:12] and zoom == self.zoom_level:
                        return os.path.join(master_folder, blendfile)
                except ValueError:
                    continue
            return None

        elif self.source_mode == 'BLENDFILE':
            return os.path.join(master_folder, self.file_name)
        
        return None

    def get_source_file(self, context):
        def get_source_file(self, context):
            master_folder = os.path.dirname(bpy.context.scene.master_txt_filepath)
            if self.source_mode == 'MASTERFILE':
                return self.get_master_file(context)
            elif self.source_mode == 'BLENDFILE':
                return os.path.join(master_folder, self.file_name)
            return None
    
    def get_master_file(self, context):
        master_txt_filepath = bpy.context.scene.master_txt_filepath
        if not os.path.exists(master_txt_filepath):
            print(f"Master TXT file not found: {master_txt_filepath}")
            return None

        with open(master_txt_filepath, 'r') as file:
            lines = file.readlines()

        for line in lines:
            try:
                name, blendfile, zoom = line.strip().split(" | ")
                if name == obj.name[:12] and zoom == zoom_level:
                    return os.path.join(os.path.dirname(bpy.context.scene.master_txt_filepath), blendfile)
            except ValueError:
                continue 
        return None

    def process_utils(self, context, source_file):
        linked_utils = []
        
        node_group = bpy.data.node_groups.get(self.node_group)
        if self.node_group:
            node_group = bpy.data.node_groups.get(self.node_group)
            try:
                with bpy.data.libraries.load(source_file, link=(self.transfer_mode == 'LINK')) as (data_from, data_to):
                    if self.node_group in data_from.node_groups:
                        data_to.node_groups = [self.node_group]
                    else:
                        self.report({'ERROR'}, "Node group not found in source file.")
                        return {'CANCELLED'}
                return {'FINISHED'}
            except Exception as e:
                self.report({'ERROR'}, f"Error transferring node group: {e}")
                return {'CANCELLED'}
        
        worlds = bpy.data.worlds.get(self.world)
        if self.world:
            try:
                bpy.data.worlds.remove(self.world)
            except Exception as e:
                print(f"Error transfering node group: {e}") 
            try:
                world = self.world
                with bpy.data.libraries.load(source_file, link=(self.transfer_mode == 'LINK')) as (data_from, data_to):
                    if hasattr(data_from, "worlds"):
                        data_to.worlds = [world_name for world_name in data_from.worlds if world_name in bpy.data.worlds]
                if not data_to.worlds:
                    print("No world found to transfer.")
                    return None
        
                return None
            except Exception as e:
                print(f"Error transfering world: {e}")
            return {'FINISHED'}
            
        return linked_utils


    def get_util_names(self, context):
        node_group = bpy.data.node_groups.get(self.node_group)
        if self.node_group:
            return [node_group.name for node_group in bpy.data.node_groups]
        worlds = bpy.data.worlds.get(self.world)
        if self.world:
            return [world.name for world in bpy.data.worlds]
        return []


    def collectionchecker(self):
        if self.base_collection == "SCENE":
            return bpy.context.scene.collection
            
        if self.base_collection == "COLLECTIONNAME":
            if self.collection_name == "":
                collection_destination = f"Collection"
            else:
                collection_destination = f"{self.collection_name}"
        else:
            collection_destination = f"{self.base_collection}"
        
        temp_collection = bpy.data.collections.get(collection_destination)
        if not temp_collection:
            temp_collection = bpy.data.collections.new(collection_destination)
            bpy.context.scene.collection.children.link(temp_collection)
        return temp_collection



    def replace_existing_objects(self, selected_project_uuids):
        temp_collection = self.collectionchecker()
        
        if not temp_collection or not temp_collection.objects:
            return {'FINISHED'}
        
        objects_to_replace = []
        
        if temp_collection and temp_collection.objects:
            for obj in temp_collection.objects:
                if "project_uuid" in obj:
                    uuid_data = UUIDManager.parse_project_uuid(obj["project_uuid"])
                    if uuid_data and uuid_data["uuid_base_tile_name"] in selected_project_uuids:
                        objects_to_replace.append((obj, uuid_data))
        
        for obj, uuid_data in objects_to_replace:
            if uuid_data["uuid_transfermode"] == "APPEND":
                bpy.data.objects.remove(obj)
            elif uuid_data["uuid_transfermode"] == "LINK":
                temp_collection.objects.unlink(obj)
        
        return {'FINISHED'}


    def transfer_objects(self, source_file, selected_project_uuids):
        linked_objects = []
        try:
            with bpy.data.libraries.load(source_file, link=(self.transfer_mode == 'LINK')) as (data_from, data_to):
                if "ALL" in selected_project_uuids:
                    data_to.objects = list(data_from.objects)
                else:
                    data_to.objects = [
                        obj_name for obj_name in data_from.objects
                        if any(obj_name[:12] == uuid_base for uuid_base in selected_project_uuids)
                    ]
        
            if not hasattr(data_to, "objects") or not data_to.objects:
                print("No objects found to transfer.")
                return None
        
            temp_collection = self.collectionchecker()
            project_filename = os.path.basename(bpy.data.filepath).replace(".blend", "")
        
            for obj in data_to.objects:
                if obj and isinstance(obj, bpy.types.Object):
                    temp_collection.objects.link(obj)
                    linked_objects.append(obj)
        
                    unique_id = obj.get("unique_id", "NO_ID")
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    obj["project_uuid"] = f"{project_filename}|{unique_id}|{timestamp}|{self.transfer_mode}|{UUIDManager.generate_random_hash()}"
        
                    if obj.override_library is None and obj.library is not None:
                        obj.override_library_create(hierarchy=True)
                    obj.select_set(False)
        
        except Exception as e:
            return {'CANCELLED'}
        
        return linked_objects


# ================== RELOAD ADDON ==================
class XTD_Reload_App(XTDToolsOperator):
    bl_idname = "xtd_tools.reloadapp"
    bl_label = "Reload Application"
    
    def execute(self, context):
        os.system("cls")
        print("Reload XTD Tools modules...")
        bpy.ops.script.reload()
        return {'FINISHED'}


# ================== DYNAMIC POPUP ENGINE ==================
def PopupController(title="Information", message="Message", icon='INFO', buttons=None):
    def draw(self, context):
        self.layout.label(text=message, icon=icon)
        
        if buttons:
            for btn_text, operator_name, btn_icon in buttons:
                if operator_name:
                    self.layout.operator(operator_name, text=btn_text, icon=btn_icon if btn_icon else "NONE")

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


# ================== DEFAULT GLOBAL PROPERTIES ==================
bpy.types.Scene.master_txt_filepath=  bpy.props.StringProperty(name="Master TXT Filepath",description="Path to the master TXT file",subtype='FILE_PATH',default=r"C:\Movie\BP\LINKEDPARTS\MASTER.txt")
bpy.types.Scene.xtd_tools_activepanels = bpy.props.BoolProperty(name="ACTIVE PANELS", default=False)
bpy.types.Scene.batch_mode = bpy.props.EnumProperty(
    name="BATCH SIZE",
    description="Control the batch process mode",
    items=[
        ('1', "DISABLED", ""),
        ('2', "2", ""),
        ('4', "4", ""),
        ('6', "6", ""),
        ('8', "8", ""),
        ('10', "10", ""),
        ('20', "20", ""),
        ('40', "40", ""),
        ('80', "80", ""),
        ('100', "100", ""),
        ('200', "200", ""),
        ('500', "500", ""),
        ('99999', "INFINITE", ""),
    ],
    default='1'
)
bpy.types.Scene.export_ply = bpy.props.EnumProperty(name='EXPORT AS PLY?',
        description='Export as PLY?',
        items =  (
            ('YES','YES',''),
            ('NO','NO','')
        ),
        default = 'NO'
    )
bpy.types.Scene.shutdown_after = bpy.props.EnumProperty(name='SHUTDOWN CPU?',
        description='Final shutdown cpu?',
        items =  (
            ('YES','YES',''),
            ('NO','NO','')
        ),
        default = 'NO'
    )
bpy.types.Scene.xtd_active_panels = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup,name="Active Panels")


# ================== TIME AND STATUS ==================
class Timer:
    def __init__(self):
        self.start_time = time.time()

    def elapsed(self):
        return time.time() - self.start_time

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def colors():
    darkgrey = ColorHex('#212121')
    grey = ColorHex('#efefef')
    yellow = ColorHex('#fcc219')
    
    wq = 106
    ws = " "
    wl = "_"
    return darkgrey, grey, yellow, wq, ws, wl
    
def make_update_callback(panel):
    def update(self, context):
        if bpy.context.scene.tool_visibility_mode == 'DEFAULT':
            global_settings.VisibilityController.update_visibility(panel)
        return None
    return update

def statusheader(bl_label, functiontext):
    os.system("cls")
    darkgrey, grey, yellow, wq, ws, wl = colors()
    bl_c=len(bl_label)
    ft_c=len(functiontext)
    bl_q =int(wq - bl_c)
    ft_q =int(wq - ft_c)
    bg_hex(f"{darkgrey}  {wq * ws}{darkgrey.OFF}", "#161616")
    bg_hex(f"{darkgrey}  {grey}{bl_label}{bl_q * ws}{grey.OFF}{darkgrey.OFF}", "#161616")
    bg_hex(f"{darkgrey}__{wq * wl}{darkgrey.OFF}", "#161616")
    bg_hex(f"{darkgrey}  {yellow}{functiontext}{ft_q * ws}{yellow.OFF}{darkgrey.OFF}", "#161616")
    bg_hex(f"{darkgrey}__{wq * wl}{darkgrey.OFF}", "#161616")
    bg_hex(f"\n", "#161616")

def print_status(batch_index, total_batches, total_objects, current_index):
    darkgrey, grey, yellow, wq, ws, wl = colors()
    bg_hex(f"{darkgrey}  {grey}BATCH READY: {batch_index} | TOTAL: {total_batches} | OBJECT READY: {current_index} | ALL OBJECTS: {total_objects}{grey.OFF} {darkgrey.OFF}", "#161616")


# ================== BASE FUNCTIONS ==================
def global_deselect(context, all_objects=False):
    if all_objects:
        for obj in bpy.context.scene.objects:
            obj.select_set(False)
    else:
        for obj in bpy.context.selected_objects:
            obj.select_set(False)

def set_active_object(context, obj):
    global_deselect(context)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

def apply_transforms(context, obj):
    set_active_object(context, obj)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)
    bpy.context.view_layer.update()

def remove_doubles(context, obj):
    set_active_object(context, obj)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode='OBJECT')

def apply_modifiers(context, obj):
    set_active_object(context, obj)
    for mod in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.update()
    
def check_master_file_availability(self, context):
    master_txt_filepath = bpy.context.scene.master_txt_filepath

    if not os.path.exists(master_txt_filepath):
        self.report({'WARNING'}, f"Master TXT file not found: {master_txt_filepath}")
        return {'CANCELLED'}

    with open(master_txt_filepath, 'r') as file:
        lines = file.readlines()

    tile_names = []
    for line in lines:
        try:
            name, blendfile, zoom = line.strip().split(" | ")
            if self.resolution:
                if zoom == self.resolution:
                    tile_names.append(name)
            else:
                tile_names.append(name)
        except ValueError:
            continue
            
    return tile_names
    
def selected_objects(self, context):
    selected_objects = bpy.context.selected_objects
    if not selected_objects:
        self.report({'WARNING'}, "No objects selected.")
        return {'CANCELLED'}

    selected_objects = [obj for obj in selected_objects]
    
    return selected_objects


# ================== Export ply ==================
def export_ply_object(obj, export_dir):
    filepath = os.path.join(export_dir, f"{obj.name}.ply")
    bpy.ops.wm.ply_export(
        filepath=filepath,
        export_selected_objects=True,
        apply_modifiers=True,
        export_normals=False,
        export_uv=False,
        export_triangulated_mesh=False
    )
    bpy.data.objects.remove(obj, do_unlink=True)


# ================== BATCH PROCESSOR ==================
def process_batch(context, objects):
    prefs = bpy.context.scene.xtd_tools_props
    export_dir = os.path.dirname(bpy.data.filepath)

    batch_size = prefs.batch_size if prefs.batch_mode != "DISABLED" else 1

    start_time = time.time()
    total_objects = len(objects)

    for i, obj in enumerate(objects):
        if i % batch_size == 0 and prefs.show_status:
            elapsed = time.time() - start_time
            print(f"Processed {i}/{total_objects} objects. Elapsed time: {elapsed:.2f}s")

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        print(f"Processing {obj.name} ({i + 1}/{total_objects})")

        if prefs.export_ply:
            export_ply_object(obj, export_dir)

        obj.select_set(False)

    if prefs.shutdown_after:
        threading.Thread(target=shutdown_computer).start()
        

# ================== Shutdown pc ==================
def shutdown_computer():
    os_name = os.name
    if os_name == "nt":
        os.system("shutdown /s /t 1")
    elif os_name == "posix":
        os.system("shutdown now")
    else:
        print("Az operációs rendszer nem támogatott.")

# ================== HOTKEY SETUP ==================
def setup_hotkeys():
    keyboard.add_hotkey("esc", ProcessManager.stop)

