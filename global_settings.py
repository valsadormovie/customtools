#-------------------------------------------------
#-GLOBAL_SETTINGS.py
#-------------------------------------------------
#  ================== IMPORTED LIBRARYS ================== 
import importlib
import inspect
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

# ================== MAIN PANEL SCRIPTS ================== 
panels = [
    "global_settings",
    "modifiertools_panel",
    "transformtools_panel",
    "vertexgrouptools_panel",
    "utilitytools_panel",
    "tiletools_panel"
]

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

# ----------------- MAIN execute operator --------------
# ================== GLOBAL OPERATORS ==================
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

# ----------- PROCESS MANAGER -----------
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

# ------------------MAIN object transfer engine -------------------------
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


# EnumProperty for visibility mode
bpy.types.Scene.tool_visibility_mode = bpy.props.EnumProperty(
    items=[
        ('INTUITIVE', "Intuitive", ""),
        ('DEFAULT', "Default", ""),
        
    ],
    name="Tool Visibility Mode",
    default="DEFAULT"
)

# ------------------MAIN object transfer engine -------------------------
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
        description="Specify the blend file name for BLENDFILENAME mode",
        default=""
    )
    
    world: bpy.props.StringProperty(
        name="World",
        description="Specify the blend file name for BLENDFILENAME mode",
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

    def execute(self, context):
        source_file = self.get_source_file(context)
        if not source_file or not os.path.exists(source_file):
            self.report({'ERROR'}, "Blend file path is invalid or missing.")
            return {'CANCELLED'}

        if self.node_group.strip() != "":
            result = self.process_utils(context, source_file)
            if 'CANCELLED' in result:
                return result
            self.report({'INFO'}, "Successfully linked node group.")
            return {'FINISHED'}

        object_names = self.object_name.split(",")
        linked_objects = self.transfer_objects(source_file, object_names)

        if not linked_objects:
            self.report({'ERROR'}, "No objects were transferred.")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Successfully transferred {len(linked_objects)} objects.")
        return {'FINISHED'}

    def process(self, context, source_file):
        object_names = self.get_object_names(context)
        if not object_names:
            print("No matching objects found.")
            return None

        if self.replace_mode == 'REPLACE':
            self.replace_existing_objects(object_names)

        linked_objects = self.transfer_objects(source_file, object_names)
        return linked_objects
        
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
        if worlds:
            try:
                bpy.data.worlds.remove(self.world)
            except Exception as e:
                print(f"Error transfering node group: {e}") 
            try:
                world = self.world
                with bpy.data.libraries.load(source_file, link=(self.transfer_mode == 'LINK')) as (data_from, data_to):
                    data_to.worlds = [world_name for world_name in util_names if world_name in data_from.worlds]
                if not data_to.worlds:
                    print("No world found to transfer.")
                    return None

                return None
            except Exception as e:
                print(f"Error transfering world: {e}")
            return {'FINISHED'}
            
        return linked_utils

    def get_source_file(self, context):
        master_folder = os.path.dirname(bpy.context.scene.master_txt_filepath)
        if self.source_mode == 'MASTERFILE':
            return self.get_master_file(context)
        elif self.source_mode == 'BLENDFILE':
            return os.path.join(master_folder, self.file_name)
        return None

    def get_object_names(self, context):
        if self.objects == 'SELECTED':
            return [obj.name[:12] for obj in context.selected_objects if obj.type == 'MESH']
        elif self.objects == 'ALL':
            return [obj.name for obj in bpy.data.objects if obj.type == 'MESH']
        elif self.objects == 'OBJECTNAME':
            return [self.object_name]
        return []
    
    def get_util_names(self, context):
        node_group = bpy.data.node_groups.get(self.node_group)
        if self.node_group:
            return [self.node_group for node_group in bpy.data.node_groups]
        worlds = bpy.data.worlds.get(self.world)
        if self.world:
            return [self.world for world in bpy.data.worlds in data_from.worlds]
        return []
        
    def collectionchecker(obj_name, context):
        if "TEMP_LINKED" not in bpy.data.collections:
            if obj_name not in context.scene.collection.objects:
                print("No objects were transferred.")
                return None
            else:
                return context.scene.collection.objects
        else:
            temp_collection = bpy.data.collections.get("TEMP_LINKED")
            if obj_name not in temp_collection.objects and obj_name not in context.scene.collection.objects:
                print("No objects were transferred.")
                return None
            else:
                if obj_name in temp_collection.objects:
                    return temp_collection.objects
                else:
                    return context.scene.collection.objects

    def replace_existing_objects(self, object_names):
        for obj_name in object_names:
            temp_collection = collectionchecker(obj_name)
            if temp_collection:
                obj = bpy.data.objects.get(obj_name)
                bpy.data.objects.remove(obj)
                if temp_collection == bpy.context.scene.collection.objects:
                    return {'FINISHED'}
                else:
                    if len(temp_collection.all_objects) == 0:
                        bpy.data.collections.remove(temp_collection)
        
        return {'FINISHED'}

    def transfer_objects(self, source_file, object_names):
        linked_objects = []
        try:
            with bpy.data.libraries.load(source_file, link=(self.transfer_mode == 'LINK')) as (data_from, data_to):
                data_to.objects = [obj_name for obj_name in object_names if obj_name in data_from.objects]
            if not data_to.objects:
                print("No objects found to transfer.")
                return None

            if "TEMP_LINKED" not in bpy.data.collections:
                temp_collection = bpy.data.collections.new("TEMP_LINKED")
                bpy.context.scene.collection.children.link(temp_collection)
            else:
                temp_collection = bpy.data.collections["TEMP_LINKED"]

            for obj in data_to.objects:
                if obj:
                    temp_collection.objects.link(obj)
                    linked_objects.append(obj)
        except Exception as e:
            print(f"Error transferring objects: {e}")
        return linked_objects

# ================== RELOAD ==================
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

# ----------- TIME AND STATUS -----------
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

# ----------- BASE FUNCTIONS -----------

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
    
def selected_objects_names(self, context):
    selected_objects = bpy.context.selected_objects
    if not selected_objects:
        self.report({'WARNING'}, "No objects selected.")
        return {'CANCELLED'}

    object_names = [obj.name for obj in selected_objects]
    object_names = ",".join(object_names)
    
    return object_names

# ---------------- Export ply ---------------------
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

# ---------------- Batch process ---------------------
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
        

# ---------------- Shutdown pc ---------------------
def shutdown_computer():
    os_name = os.name
    if os_name == "nt":
        os.system("shutdown /s /t 1")
    elif os_name == "posix":
        os.system("shutdown now")
    else:
        print("Az operációs rendszer nem támogatott.")

# ----------- HOTKEY SETUP -----------
def setup_hotkeys():
    keyboard.add_hotkey("esc", ProcessManager.stop)


