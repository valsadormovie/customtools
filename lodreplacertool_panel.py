#-------------------------------------------------
#-LODREPLACERTOOL_PANEL.py
#-------------------------------------------------
from .global_settings import *
disable_cache()
# ================== PANEL =================
class XTD_PT_LODReplacer(bpy.types.Panel):
    bl_label = "LOD Replacer"
    bl_idname = "XTD_PT_lod_replacer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"

    @classmethod
    def poll(cls, context):
        return VisibilityController.check_visibility(
            context,
            panel_name="lodreplacertool_panel",
            require_selected=True,
            require_prefix=True
        )

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        
        layout.label(text="Target Collection:")
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene, "lod_target_collection", text="")
        
        layout.separator()
        
        layout.label(text="Replace LOD:")
        row = layout.row(align=True)
        row.operator("xtd_tools.replace_lod", text="Low").lod_level = "LOW"
        row.operator("xtd_tools.replace_lod", text="Medium").lod_level = "MEDIUM"
        row.operator("xtd_tools.replace_lod", text="High").lod_level = "HIGH"
        row = layout.row(align=True)
        row.operator("xtd_tools.replace_lod", text="UNLINK ALL").lod_level = "UNLINK"
        
        layout.separator()
        
        layout.label(text="Prefix Matching (Optional):")
        row = layout.row(align=True)
        row.prop(scene, "lod_prefix", text="Prefix")
        
        layout = self.layout
        layout.separator()
        box = layout.box()
        row = box.row(align=True)
        
        row.prop(scene, "xtd_tools_lodfiles", text="Select LOD Files:", emboss=False, icon_only=True, icon="TRIA_DOWN" if scene.xtd_tools_lodfiles else "TRIA_RIGHT")

        row = layout.row()
        row.alignment = 'LEFT'
        
        if scene.xtd_tools_lodfiles:
            row = box.row(align=True)
            row.prop(scene, "lod_low_file", text="Low")
            row = box.row(align=True)
            row.prop(scene, "lod_medium_file", text="Medium")
            row = box.row(align=True)
            row.prop(scene, "lod_high_file", text="High")

# ================ SCENES ================
bpy.types.Scene.xtd_tools_lodfiles = bpy.props.BoolProperty(name="LODFILES", default=False)
bpy.types.Scene.lod_low_file = bpy.props.StringProperty(name="Low LOD File", subtype='FILE_PATH')
bpy.types.Scene.lod_medium_file = bpy.props.StringProperty(name="Medium LOD File", subtype='FILE_PATH')
bpy.types.Scene.lod_high_file = bpy.props.StringProperty(name="High LOD File", subtype='FILE_PATH')
bpy.types.Scene.lod_unlink = bpy.props.StringProperty(name="UNLINK ALL", subtype='FILE_PATH')
bpy.types.Scene.lod_prefix = bpy.props.StringProperty(name="LOD Prefix", description="Optional prefix for batch replacement")
bpy.types.Scene.lod_target_collection = bpy.props.PointerProperty(
    name="Target Collection",
    type=bpy.types.Collection,
    description="Select the collection to replace LODs"
)

# ================ OPERATORS ================
class XTD_OT_ReplaceLOD(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.replace_lod"
    bl_label = "Replace LOD"
    bl_options = {'REGISTER', 'UNDO'}

    lod_level: bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        target_collection = scene.lod_target_collection
        lod_prefix = scene.lod_prefix.strip()
        
        if not target_collection:
            self.report({'WARNING'}, "No collection selected for LOD replacement.")
            return {'CANCELLED'}
        
        lod_file = ""
        if self.lod_level == "LOW":
            lod_file = bpy.path.abspath(scene.lod_low_file)
        elif self.lod_level == "MEDIUM":
            lod_file = bpy.path.abspath(scene.lod_medium_file)
        elif self.lod_level == "HIGH":
            lod_file = bpy.path.abspath(scene.lod_high_file)
        elif self.lod_level == "UNLINK":
            lod_file == "UNLINK"
        
        temp_collection_name = f"{target_collection.name}_LOD"
        target_collection = bpy.data.collections.get(target_collection.name)
        if target_collection:
            bpy.data.collections[target_collection.name].hide_viewport = False
        
        temp_collection = bpy.data.collections.get(temp_collection_name)
        if not temp_collection:
            temp_collection = bpy.data.collections.new(temp_collection_name)
            temp_collection.color_tag = "COLOR_01"
            bpy.context.scene.collection.children.link(temp_collection)
        
        for obj in list(target_collection.objects):
            obj.hide_set(True)
        
        for obj in list(temp_collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        
        replaceable_objects = [obj for obj in target_collection.objects]
        if lod_file == "UNLINK":
            return {'FINISHED'}
            
        if not lod_file:
            for obj in target_collection.objects:
                obj.hide_set(False)
            temp_collection = bpy.data.collections.get(temp_collection_name)
            if temp_collection:
                bpy.data.collections.remove(temp_collection)
            target_collection = bpy.data.collections.get(target_collection.name)
            if target_collection:
                bpy.data.collections[target_collection.name].hide_viewport = False
            
            self.report({'WARNING'}, f"No file specified for {self.lod_level} LOD replacement.")
            return {'CANCELLED'}
        
        replaceable_objects = [obj for obj in target_collection.objects if lod_prefix and obj.name.startswith(lod_prefix)]
        with bpy.data.libraries.load(lod_file, link=True) as (data_from, data_to):
            with bpy.data.libraries.load(lod_file, link=True) as (data_from, data_to):
                if lod_prefix:
                    data_to.objects = [obj_name for obj_name in data_from.objects if obj_name.startswith(lod_prefix)]
                else:
                    data_to.objects = [obj_name for obj_name in data_from.objects if obj_name in replaceable_objects]
                    
        with bpy.data.libraries.load(lod_file, link=True) as (data_from, data_to):
            if lod_prefix:
                data_to.objects = [obj_name for obj_name in data_from.objects if obj_name.startswith(lod_prefix)]
            else:
                data_to.objects = [obj_name for obj_name in data_from.objects if obj_name in [o.name for o in replaceable_objects]]
        
        if not data_to.objects:
            self.report({'WARNING'}, f"No matching objects found in {lod_file}.")
            return {'CANCELLED'}
        
        for obj in data_to.objects:
            if obj and isinstance(obj, bpy.types.Object):
                temp_collection.objects.link(obj)
                if lod_prefix:
                    ref_obj = obj
                    for obj in replaceable_objects:
                        new_obj = ref_obj.copy()
                        new_obj.location = obj.location
                        new_obj.rotation_euler = obj.rotation_euler
                        new_obj.scale = obj.scale
                        temp_collection.objects.link(new_obj)
                    temp_collection.objects.unlink(ref_obj)
                bpy.data.collections[target_collection.name].hide_viewport = True
        
        self.report({'INFO'}, f"Replaced LODs in {target_collection.name} with {self.lod_level} models.")
        return {'FINISHED'}

