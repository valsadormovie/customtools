#-------------------------------------------------
#-TRANSFORMTOOLS_PANEL.py
#-------------------------------------------------

from .global_settings import *
disable_cache()
# ================== PANEL ==================
class XTD_PT_TransformTools(bpy.types.Panel):
    bl_label = "TRANSFORM TOOLS"
    bl_idname = "XTD_PT_transform_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return VisibilityController.check_visibility(context, panel_name = "transformtools_panel", require_selected=True, require_prefix=True)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.scale_y = 0.5
        for i in range(0, 2, 2):
            row = box.row(align=True)
            row.alignment = 'LEFT'
            row.scale_y = 0.5
            row.label(text="TRANSFER OBJECT POSITIONS", icon="TRANSFORM_ORIGINS")
        for i in range(0, 2, 2):
            row = box.row(align=True)
             # Filepath for Transform File
            row.prop(bpy.context.scene, "transform_file_path", text="Filepath")
       
        for i in range(0, 2, 2):
            row = box.row(align=True)
            check_selected_active_button(row)
            row.operator("xtd_tools.apply_transform_from_file", text="Apply File Transforms", icon="FILE_TICK")
            row.operator("xtd_tools.apply_both_transforms", text="Apply Main Transforms", icon="CON_TRANSFORM")
            row = box.row(align=True)
            check_selected_active_button(row)
            row.operator("xtd_tools.save_transform_to_txt", text="Save to TXT", icon="EXPORT")
            row.operator("xtd_tools.generate_tile_txt", text="Generate Tile TXT", icon="TEXT")

# ================ PROPERTIES ================

bpy.types.Scene.transform_file_path = bpy.props.StringProperty(
    name="Transform File Path",
    description="Path to the transform file",
    default="",
    subtype='FILE_PATH'
)

# ================== OPERATORS ==================
# ----------- APPLY TRANSFORMS -----------
class XTD_OT_ApplyTransformFromFile(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.apply_transform_from_file"
    bl_label = "Apply Transformations from File"

    def process_object(self, obj):
        filepath = bpy.context.scene.transform_file_path
        if not filepath or not os.path.exists(filepath):
            self.report({'ERROR'}, "Invalid file path.")
            return

        transform_data = read_transform_from_file(filepath)
        set_active_object(obj)
        obj.location = Vector(transform_data["location"])
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = Quaternion(transform_data["rotation_quaternion"])
        obj.scale = Vector(transform_data["scale"])

        newobj = obj.copy()
        newobj.data = obj.data.copy()
        bpy.context.collection.objects.link(newobj)
        newobj.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)
        bpy.context.view_layer.update()

        datatransfer = obj.modifiers.new(name="DataTransfer", type='DATA_TRANSFER')
        datatransfer.use_loop_data = True
        datatransfer.data_types_loops = {'CUSTOM_NORMAL'}
        datatransfer.loop_mapping = 'TOPOLOGY'
        datatransfer.object = newobj
        bpy.ops.object.modifier_apply(modifier="DataTransfer")

        newobj.select_set(True)
        bpy.context.view_layer.objects.active = newobj
        bpy.ops.object.delete(use_global=True)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

# ----------- SAVE TRANSFORMS -----------
class XTD_OT_SaveTransformToTXT(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.save_transform_to_txt"
    bl_label = "Save Location to TXT"

    def process_object(self, obj):
        folder = os.path.dirname(bpy.data.filepath)
        file_path = os.path.join(folder, f"{obj.name}_location.txt")
        location = obj.location
        rotation = obj.rotation_quaternion if obj.rotation_mode == 'QUATERNION' else obj.rotation_euler.to_quaternion()
        scale = obj.scale
        with open(file_path, 'w') as f:
            f.write(f"TX:{location.x}\nTY:{location.y}\nTZ:{location.z}\n")
            f.write(f"RW:{rotation.w}\nRX:{rotation.x}\nRY:{rotation.y}\nRZ:{rotation.z}\n")
            f.write(f"SX:{scale.x}\nSY:{scale.y}\nSZ:{scale.z}\n")
        print(f"Data saved: {file_path}")

# ----------- GENERATE TILE -----------
class XTD_OT_GenerateTileTXT(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.generate_tile_txt"
    bl_label = "Generate Tile TXT"

    def process_object(self, obj):
        all_objects = bpy.data.objects
        txt_lines = []

        for obj in all_objects:
            if not obj.visible_get():
                continue
            object_name = obj.name 
            blendfile_name = bpy.data.filepath.split('\\')[-1]
            zoom_level = blendfile_name.split('_')[0]

            line = f"{object_name} | {blendfile_name} | {zoom_level}\n"
            txt_lines.append(line)

        txt_filepath = bpy.data.filepath.replace('.blend', '.txt')
        with open(txt_filepath, 'w') as file:
            file.writelines(txt_lines)

        print(f"Tile adatok elmentve a: {txt_filepath} fájlba")

# ----------- APPLY MAIN TRANSFORMS -----------
class XTD_OT_ApplyBothTransforms(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.apply_both_transforms"
    bl_label = "Apply Main Transforms"

    def process_object(self, obj):
        context = bpy.context
        collection = bpy.data.collections.get("Collection")
        bpy.ops.object.select_all(action = 'DESELECT')
        obj = bpy.data.objects[obj.name]
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        for ob in bpy.context.selected_objects:
            filepath = r'C:\Movie\BP\MAIN_TRANSFORM_CENTER.txt'
            transform_data = read_transform_from_file(filepath)
            ob.location = Vector(transform_data["location"])
            ob.rotation_mode = 'QUATERNION'
            ob.rotation_quaternion = Quaternion(transform_data["rotation_quaternion"])
            ob.scale = Vector(transform_data["scale"])
            ob.location = Vector(transform_data["location"])
            ob.rotation_mode = 'QUATERNION'
            ob.rotation_quaternion = Quaternion(transform_data["rotation_quaternion"])
            ob.scale = Vector(transform_data["scale"])
            newobj = ob.copy()
            newobj.data = ob.data.copy()
            
            collection.objects.link(newobj)
            newobj.select_set(False)
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)
            bpy.context.view_layer.update()
            datatransfer = ob.modifiers.new(name="DataTransfer", type='DATA_TRANSFER')
            bpy.context.object.modifiers["DataTransfer"].show_viewport = False
            datatransfer.use_loop_data = True
            datatransfer.data_types_loops = {'CUSTOM_NORMAL'}
            datatransfer.loop_mapping = 'TOPOLOGY'
            datatransfer.object = newobj
            bpy.ops.object.modifier_apply(modifier="DataTransfer")
            ob.select_set(False)
            newobj.select_set(True)
            bpy.context.view_layer.objects.active = newobj
            bpy.ops.object.delete(use_global=True)
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.transform_apply(location=True, rotation=True, properties=True)
            bpy.context.view_layer.update()

        for ob in bpy.context.selected_objects:
            filepath = r'C:\Movie\BP\ROTATE.txt'
            transform_data = read_transform_from_file(filepath)
            ob.location = Vector(transform_data["location"])
            ob.rotation_mode = 'QUATERNION'
            ob.rotation_quaternion = Quaternion(transform_data["rotation_quaternion"])
            ob.scale = Vector(transform_data["scale"])
            ob.location = Vector(transform_data["location"])
            ob.rotation_mode = 'QUATERNION'
            ob.rotation_quaternion = Quaternion(transform_data["rotation_quaternion"])
            ob.scale = Vector(transform_data["scale"])
            newobj = ob.copy()
            newobj.data = ob.data.copy()
            collection.objects.link(newobj)
            newobj.select_set(False)
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)
            bpy.context.view_layer.update()
            datatransfer = ob.modifiers.new(name="DataTransfer", type='DATA_TRANSFER')
            bpy.context.object.modifiers["DataTransfer"].show_viewport = False
            datatransfer.use_loop_data = True
            datatransfer.data_types_loops = {'CUSTOM_NORMAL'}
            datatransfer.loop_mapping = 'TOPOLOGY'
            datatransfer.object = newobj
            bpy.ops.object.modifier_apply(modifier="DataTransfer")
            ob.select_set(False)
            newobj.select_set(True)
            bpy.context.view_layer.objects.active = newobj
            bpy.ops.object.delete(use_global=True)
            ob.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
            

    def post_process_object(self, context):
        area_type = 'VIEW_3D'
        areas  = [area for area in bpy.context.window.screen.areas if area.type == area_type]
        with bpy.context.temp_override(
            window=bpy.context.window,
            area=areas[0],
            region=[region for region in areas[0].regions if region.type == 'WINDOW'][0],
            screen=bpy.context.window.screen
        ):
            for obj in self.selected_objects:
                if not obj.visible_get():
                    continue
                if obj.type == 'MESH': 
                    obj = bpy.data.objects.get(obj.name)
                    if obj:
                        obj.select_set(True)
                        
            bpy.ops.view3d.view_selected()


     
# ================== FUNCTIONS ==================
def read_transform_from_file(filepath):
    transform_data = {
        "location": [0.0, 0.0, 0.0],
        "rotation_quaternion": [1.0, 0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
    }
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('TX:'):
                    transform_data["location"][0] = float(line.split(':')[1].strip())
                elif line.startswith('TY:'):
                    transform_data["location"][1] = float(line.split(':')[1].strip())
                elif line.startswith('TZ:'):
                    transform_data["location"][2] = float(line.split(':')[1].strip())
                elif line.startswith('RW:'):
                    transform_data["rotation_quaternion"][0] = float(line.split(':')[1].strip())
                elif line.startswith('RX:'):
                    transform_data["rotation_quaternion"][1] = float(line.split(':')[1].strip())
                elif line.startswith('RY:'):
                    transform_data["rotation_quaternion"][2] = float(line.split(':')[1].strip())
                elif line.startswith('RZ:'):
                    transform_data["rotation_quaternion"][3] = float(line.split(':')[1].strip())
                elif line.startswith('SX:'):
                    transform_data["scale"][0] = float(line.split(':')[1].strip())
                elif line.startswith('SY:'):
                    transform_data["scale"][1] = float(line.split(':')[1].strip())
                elif line.startswith('SZ:'):
                    transform_data["scale"][2] = float(line.split(':')[1].strip())
    return transform_data






