#-------------------------------------------------
#-TILELODCAMERA_PANEL.py
#-------------------------------------------------

from .global_settings import *

# ================== PANEL =================
class XTD_PT_TileToolsCamera(bpy.types.Panel):
    bl_label = "Tile Tools Camera"
    bl_idname = "XTD_PT_tilelodcamera"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        layout.label(text="TILE TRANSFER TARGETS:", icon="CAMERA_DATA")
        box = layout.box()
        row = layout.row()
        row = box.row(align=True)
        row.label(text="SELECT CAMERA:")
        row.prop(scene, "xtd_tools_selected_camera", text="", icon="VIEW_CAMERA")
        row = box.row(align=True)
        row.label(text="WORKING COLLECTION:")
        row.prop(scene, "xtd_tools_source_lod_objects", text="", icon="OUTLINER_COLLECTION")
        
        layout = self.layout

        layout.label(text="DISTANCE:", icon="DRIVER_DISTANCE")
        row = box.row(align=True)
        box = layout.box()
        row = layout.row()

        row = box.row(align=True)
        row.label(text="THRESHOLDS:")
        row = box.row(align=True)
        row.prop(scene, "xtd_tools_lod_near", text="NEAR DISTANCE")
        row.prop(scene, "xtd_tools_lod_mid", text="MID DISTANCE")
        row.prop(scene, "xtd_tools_lod_far", text="FAR DISTANCE")
        row = box.row(align=True)

        row.prop(scene, "xtd_tools_camera_lod_active", text="Enable Camera LOD")
        row = box.row(align=True)
        row.separator()
        row.operator("xtd_tools.update_camera_lod", text="Update")
        row.operator("xtd_tools.remove_camera_lods", text="Remove")

# ================ SCENES ================
bpy.types.Scene.xtd_tools_selected_camera = bpy.props.PointerProperty(
    name="Camera",
    type=bpy.types.Object,
    description="Select the camera for LOD adjustments",
    poll=lambda self, obj: obj.type == 'CAMERA'
)

bpy.types.Scene.xtd_tools_camera_lod_active = bpy.props.BoolProperty(
    name="Enable Camera LOD",
    description="Toggle camera-based LOD adjustments",
    default=False
)

bpy.types.Scene.xtd_tools_lod_near = bpy.props.FloatProperty(
    name="Near Distance",
    description="LOD distance threshold for near objects",
    default=200.0,
    min=1.0
)

bpy.types.Scene.xtd_tools_lod_mid = bpy.props.FloatProperty(
    name="Mid Distance",
    description="LOD distance threshold for mid-range objects",
    default=1000.0,
    min=10.0
)

bpy.types.Scene.xtd_tools_lod_far = bpy.props.FloatProperty(
    name="Far Distance",
    description="LOD distance threshold for far objects",
    default=2500.0,
    min=100.0
)

bpy.types.Scene.xtd_tools_source_lod_objects = bpy.props.PointerProperty(
    name="LOD Collection",
    type=bpy.types.Collection,
    description="Select the LOD collection for dynamic linking"
)

# ================ OPERATORS ================
class XTD_OT_UpdateCameraLOD(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.update_camera_lod"
    bl_label = "Update Camera-Based LODs"
    
    def execute(self, context):
        context = bpy.context
        scene = context.scene
        camera = scene.xtd_tools_selected_camera
        if not camera:
            self.report({'WARNING'}, "No camera selected for LOD adjustment.")
            return {'CANCELLED'}
        
        source_lod_objects = scene.xtd_tools_source_lod_objects
        if not source_lod_objects:
            self.report({'WARNING'}, "No LOD collection selected.")
            return {'CANCELLED'}
        source_lod_objects = [obj for obj in source_lod_objects.objects]
        
        
                
        xtd_tools_lod_nears=[]
        xtd_tools_lod_mids=[]
        xtd_tools_lod_fars=[]
        for obj in source_lod_objects:
            if obj.type == 'MESH':
                obj.hide_set(False)
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                distance = (camera.location - obj.location).length
                if distance < scene.xtd_tools_lod_near:
                    xtd_tools_lod_nears.append(obj)
                if distance < scene.xtd_tools_lod_mid and distance > scene.xtd_tools_lod_near:
                    xtd_tools_lod_mids.append(obj)
                if distance < scene.xtd_tools_lod_far and distance > scene.xtd_tools_lod_mid:
                    xtd_tools_lod_fars.append(obj)
                else:
                    obj.hide_set(False)
        
        objects_to_delete = []
        objects_except = []
        base_tile_name = None
        source_blendfile = None
        temp_lod_collection = bpy.data.collections.get("LODS")
        if not temp_lod_collection:
            temp_lod_collection = bpy.data.collections.new("LODS")
            bpy.context.scene.collection.children.link(temp_lod_collection)
        if temp_lod_collection:
            master_txt_filepath = bpy.context.scene.master_txt_filepath
            if not os.path.exists(master_txt_filepath):
                print(f"Master TXT file not found: {master_txt_filepath}")
                return None

            with open(master_txt_filepath, 'r') as file:
                lines = file.readlines()
            for obj in temp_lod_collection.objects:
                if "project_uuid" in obj:
                    uuid_data = UUIDManager.parse_project_uuid(obj["project_uuid"])
                    if uuid_data and uuid_data["uuid_base_tile_name"]:
                        base_tile_name == {uuid_data["uuid_base_tile_name"]}
                        source_blendfile == {uuid_data["uuid_source_blendfile"]}
                        for line in lines:
                            name, blendfile, zoom = line.strip().split(" | ")
                            if obj in xtd_tools_lod_nears:
                                if name == base_tile_name and zoom == "BP20" and blendfile == source_blendfile:
                                    continue
                            elif obj in xtd_tools_lod_mids:
                                if name == base_tile_name and zoom == "BP19" and blendfile == source_blendfile:
                                    continue
                            elif obj in xtd_tools_lod_fars:
                                if name == base_tile_name and zoom == "BP18" and blendfile == source_blendfile:
                                    continue
                            else:
                                objects_to_delete.append((obj, uuid_data))
        
        
        temp_lod_collection = bpy.data.collections.get("LODS")
        temp_lod_collection = [obj for obj in temp_lod_collection.objects]
        for obj, uuid_data in objects_to_delete:
            if uuid_data and uuid_data["uuid_base_tile_name"]:
                if uuid_data["uuid_transfermode"] == "APPEND":
                    bpy.data.objects.remove(obj)
                    bpy.data.objects[base_tile_name].hide_set(True)
                elif uuid_data["uuid_transfermode"] == "LINK":
                    try:
                        temp_lod_collection.objects.unlink(obj)
                        bpy.data.objects.remove(obj)
                        bpy.data.objects[base_tile_name].hide_set(True)
                    except:
                        obj.hide_set(True)
                        continue
        

        xtd_tools_lod_nears = [obj for obj in xtd_tools_lod_nears]
        if len(xtd_tools_lod_nears) > 0:
            bpy.ops.object.select_all(action = 'DESELECT')
            for obj in xtd_tools_lod_nears:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
            bpy.ops.xtd_tools.transfermodels(transfer_mode="LINK", base_collection="COLLECTIONNAME", collection_name="LODS", source_mode="MASTERFILE", replace_mode="REPLACE", zoom_level="BP20")
            for obj in xtd_tools_lod_nears:
                obj.hide_set(True)
        
        xtd_tools_lod_mids = [obj for obj in xtd_tools_lod_mids]
        if len(xtd_tools_lod_mids) > 0:
            bpy.ops.object.select_all(action = 'DESELECT')
            for obj in xtd_tools_lod_mids:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
            bpy.ops.xtd_tools.transfermodels(transfer_mode="LINK", base_collection="COLLECTIONNAME", collection_name="LODS", source_mode="MASTERFILE", replace_mode="REPLACE", zoom_level="BP19")
            for obj in xtd_tools_lod_mids:
                obj.hide_set(True)
        
        xtd_tools_lod_fars = [obj for obj in xtd_tools_lod_fars]
        if len(xtd_tools_lod_fars) > 0:
            bpy.ops.object.select_all(action = 'DESELECT')
            for obj in xtd_tools_lod_fars:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
            bpy.ops.xtd_tools.transfermodels(transfer_mode="LINK", base_collection="COLLECTIONNAME", collection_name="LODS", source_mode="MASTERFILE", replace_mode="REPLACE", zoom_level="BP18")
            for obj in xtd_tools_lod_fars:
                obj.hide_set(True)
            
            
        return {'FINISHED'}

class XTD_OT_RemoveCameraLODS(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.remove_camera_lods"
    bl_label = "Remove Camera-Based LODs"

    def execute(self, context):
        scene = context.scene
        source_lod_objects = scene.xtd_tools_source_lod_objects
        if not source_lod_objects:
            self.report({'WARNING'}, "No LOD collection selected.")
            return {'CANCELLED'}
        source_lod_objects = [obj for obj in source_lod_objects.objects]
        
        temp_lod_collection = bpy.data.collections.get("LODS")
        if temp_lod_collection:
            temp_lod_objs = [obj for obj in temp_lod_collection.objects]
            if len(temp_lod_objs) > 0:
                for obj in source_lod_objects:
                    if obj.type == 'MESH':
                        obj.hide_set(False)
                        self.detectexits (temp_lod_collection)
        
        return {'FINISHED'}
        
    def detectexits (self, temp_lod_collection):
        objects_to_delete = []
        for obj in temp_lod_collection.objects:
            uuid_data = UUIDManager.parse_project_uuid(obj["project_uuid"])
            if uuid_data and uuid_data["uuid_base_tile_name"]:
                objects_to_delete.append((obj, uuid_data))

        for obj, uuid_data in objects_to_delete:
            if uuid_data["uuid_transfermode"] == "APPEND":
                bpy.data.objects.remove(obj)
            elif uuid_data["uuid_transfermode"] == "LINK":
                temp_lod_collection.objects.unlink(obj)
                bpy.data.objects.remove(obj)
        
        return {'FINISHED'}