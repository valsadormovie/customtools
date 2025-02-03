#-------------------------------------------------
#-TILETOOLS_PANEL.py
#-------------------------------------------------

from .global_settings import *

# ================== PANEL =================
class XTD_PT_TileTools(bpy.types.Panel):
    bl_label = "TILE TOOLS"
    bl_idname = "XTD_PT_tiletools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return VisibilityController.check_visibility(
            context, 
            panel_name="tiletools_panel", 
            require_selected=True, 
            require_prefix=True
        )

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        # Első blokk: aktuális objektum kijelzése
        box = layout.box()
        row = box.row(align=True)
        if bpy.context.active_object:
            tile_name = bpy.context.active_object.name
            row.label(text=f"Selected Object: {tile_name}", icon="OBJECT_DATA")
        else:
            row.label(text="No object selected!", icon="ERROR")
            return  # Ha nincs aktív objektum, kilépünk a rajzolásból

        # Második blokk: mód kiválasztása és extra elemek
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene, "tiletools_mode", text="MODE")

        mode_ui_elements = {
            "ShowAvailable": {
                "label": "SHOW VISUALY ZOOM LEVEL:",
                "icon": "TRANSFORM_ORIGINS",
                "extra_buttons": [("Remove Shows", "xtd_tools.remove_shows", "CANCEL")],
            },
            "Bake": {
                "label": "ZOOM LEVEL TO BE BAKED:",
                "icon": "TRANSFORM_ORIGINS",
                "extra_props": [("bake_texture_resolution", "Bake Resolution")],
            },
            "Append": {
                "label": "APPEND ZOOM LEVEL:",
                "icon": "TRANSFORM_ORIGINS",
            },
            "Optimize": {
                "label": "OPTIMIZE ZOOM LEVEL:",
                "icon": "TRANSFORM_ORIGINS",
            },
            "Link": {
                "label": "LINK ZOOM LEVEL:",
                "icon": "TRANSFORM_ORIGINS",
            },
        }

        mode_settings = mode_ui_elements.get(scene.tiletools_mode, {})

        if "label" in mode_settings:
            row = box.row(align=True)
            row.alignment = 'LEFT'
            row.label(text=mode_settings["label"], icon=mode_settings["icon"])

        if "extra_props" in mode_settings:
            for prop_name, label in mode_settings["extra_props"]:
                row = box.row(align=True)
                row.prop(scene, prop_name, text=label)

        if "extra_buttons" in mode_settings:
            row = box.row(align=True)
            for btn_label, op_id, icon in mode_settings["extra_buttons"]:
                row.operator(op_id, text=btn_label, icon=icon)

        # Harmadik blokk: Zoom level gombok
        row = box.row(align=True)
        grid = row.grid_flow(columns=4, align=True)

        zoom_levels = ["BP18", "BP19", "BP20", "BP21"]
        operator_map = {
            "ShowAvailable": "xtd_tools.showavailable_tile_resolution",
            "Bake": "xtd_tools.bake_tile_resolution",
            "Append": "xtd_tools.append_tile_resolution",
            "Optimize": "xtd_tools.optimize_tile_resolution",
            "Link": "xtd_tools.link_tile_resolution"
        }
        operator_id = operator_map.get(scene.tiletools_mode, "xtd_tools.showavailable_tile_resolution")

        for zoom_level in zoom_levels:
            exists, blendfile = self.check_resolution_availability(tile_name, zoom_level)
            sub_row = grid.row(align=True)
            sub_row.alert = not exists  # Ha nincs, akkor figyelmeztető (piros)
            sub_row.enabled = exists    # Ha létezik, akkor engedélyezzük a gombot
            op = sub_row.operator(operator_id, text=zoom_level)
            op.resolution = zoom_level
            if scene.tiletools_mode != "Optimize":
                op.blend_file = blendfile

        # Negyedik blokk: Accordion szekciók (Tile Helper, Color Grade Node, stb.)
        self.draw_accordion_box(context, layout, "TILE HELPER", "xtd_tools_tile_helper", 3, [
            ("Cage", "append_cage", False),
            ("Empty", "append_empty", False),
            ("Plane", "append_plane", False),
            ("Pretopo", "append_pretopo", False),
            ("HQ Pretopo", "append_hqpretopo", False),
            ("HQ Land", "append_hq_land", False),
            ("True Land", "append_true_land", False),
            ("True House", "append_true_house", False),
        ])

        self.draw_accordion_box(context, layout, "COLOR GRADE NODE", "xtd_tools_colorgrade", 2, [
            ("Add", "add_colorgrade", False),
            ("Remove", "remove_colorgrade", False),
        ])

        self.draw_accordion_box(context, layout, "VERTEX COLORS", "xtd_tools_vertex_colors", 2, [
            ("Create Tree Color Attribute", "create_tree_color", False),
            ("Bake to Vertex Colors", "bake_vertex_colors", False),
        ])

        self.draw_accordion_box(context, layout, "GEOMETRY NODES", "xtd_tools_geometry_nodes", 1, [
            ("Hole Filler", "hole_filler", False),
            ("Shrinkwrap Remesh", "shrinkwrap_remesh", False),
            ("Z Separator", "z_separator", False),
            ("Tree Separator", "tree_separator", False),
        ])

        self.draw_accordion_box(context, layout, "MAIN SFX", "xtd_tools_main_sfx", 1, [
            ("Add Duna, World, Sun", "add_duna", False),
        ])
        
        self.draw_accordion_box(context, layout, "UUID", "xtd_tools_uuid", 1, [
            ("Create unique IDs", "adduuid", False),
        ])

    def draw_accordion_box(self, context, layout, label, prop_name, column_span, buttons):
        scene = bpy.context.scene
        row = layout.row()
        row.alignment = 'LEFT'
        # A prop nevét a scene property-kből vesszük, és az ikon attól függ, hogy az érték True (TRIA_DOWN) vagy False (TRIA_RIGHT)
        row.prop(scene, prop_name, text=label, emboss=False, icon_only=True, icon="TRIA_DOWN" if getattr(scene, prop_name) else "TRIA_RIGHT")
        if getattr(scene, prop_name):
            box = layout.box()
            grid = box.grid_flow(columns=int(column_span), align=True)
            for button_text, operator, full_width in buttons:
                if full_width:
                    grid.operator(f"xtd_tools.{operator}", text=button_text)
                else:
                    grid.operator(f"xtd_tools.{operator}", text=button_text)

    def check_resolution_availability(self, tile_name, zoom_level):
        master_txt_filepath = bpy.context.scene.master_txt_filepath
        if not os.path.exists(master_txt_filepath):
            return (False, "")
        
        with open(master_txt_filepath, 'r') as file:
            lines = file.readlines()

        for line in lines:
            try:
                name, blendfile, zoom = line.strip().split(" | ")
                # Feltételezzük, hogy a tile név első 12 karaktere elegendő az egyezéshez
                if name[:12] == tile_name[:12] and zoom == zoom_level:
                    # Ha a blendfile létezik (itt csak az útvonal összeállítását ellenőrizzük)
                    full_path = os.path.join(os.path.dirname(master_txt_filepath), blendfile)
                    if os.path.exists(full_path):
                        return (True, blendfile)
                    else:
                        return (False, blendfile)
            except ValueError:
                continue
        return (False, "")

# ================ SCENES ================
bpy.types.Scene.xtd_tools_tile_helper = bpy.props.BoolProperty(name="Tile Helper", default=False)
bpy.types.Scene.xtd_tools_colorgrade = bpy.props.BoolProperty(name="Colorgrade Node", default=False)
bpy.types.Scene.xtd_tools_vertex_colors = bpy.props.BoolProperty(name="Vertex Colors", default=False)
bpy.types.Scene.xtd_tools_geometry_nodes = bpy.props.BoolProperty(name="Geometry Nodes", default=False)
bpy.types.Scene.xtd_tools_main_sfx = bpy.props.BoolProperty(name="Main SFX", default=False)
bpy.types.Scene.xtd_tools_uuid = bpy.props.BoolProperty(name="UUID", default=False)
bpy.types.Scene.tiletools_mode = bpy.props.EnumProperty(
    name="Tile Tools Mode",
    items=[
        ("Optimize", "Optimize", ""),
        ("Link", "Link", ""),
        ("Append", "Append", ""),
        ("Bake", "Bake", ""),
        ("ShowAvailable", "Show Available", ""),
    ],
    default="Optimize"
)
bpy.types.Scene.bake_texture_resolution = bpy.props.EnumProperty(
    name="Bake Texture Resolution",
    items=[
        ("1024x1024", "1024x1024", ""),
        ("2048x2048", "2048x2048", ""),
        ("4096x4096", "4096x4096", ""),
    ],
    default="4096x4096"
)

# ================ OPERATORS ================
# Dummy Operator Template

class XTD_OT_BakeTileResolution(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.bake_tile_resolution"
    bl_label = "Bake tile Resolution"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: bpy.props.StringProperty()
    blend_file: bpy.props.StringProperty()

    def process_object(self, obj):
        print(f"Dummy operator executed for resolution: {self.resolution}")
        return {'FINISHED'}

class XTD_OT_ShowAvailableTileResolution(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.showavailable_tile_resolution"
    bl_label = "Show Available Resolution"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: bpy.props.StringProperty()
    blend_file: bpy.props.StringProperty()

    def execute(self, context):
        zoom_colors = {
            "BP18": (1.0, 0.0, 0.0, 1.0),  
            "BP19": (0.0, 1.0, 0.0, 1.0),  
            "BP20": (0.0, 0.0, 1.0, 1.0),  
            "BP21": (1.0, 1.0, 0.0, 1.0)   
        }
        color = zoom_colors.get(self.resolution, (1.0, 1.0, 1.0, 1.0)) 
        
        tile_names = check_master_file_availability(self, context)
        bpy.context.space_data.shading.color_type = 'VERTEX'

        for obj in bpy.data.objects:
            if obj.name in tile_names and obj.library is None:
                obj.color = color
            elif obj.name in tile_names and obj.library is not None:
                continue

        self.report({'INFO'}, f"{self.resolution} zoom level highlighted.")
        return {'FINISHED'}

class XTD_OT_RemoveShows(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.remove_shows"
    bl_label = "Remove Show Zooms"
    bl_options = {'REGISTER', 'UNDO'}
    
    resolution: bpy.props.StringProperty()
    blend_file: bpy.props.StringProperty()

    def execute(self, context):
        tile_names = check_master_file_availability(self, context)
        bpy.context.space_data.shading.color_type = 'MATERIAL'

        for obj in bpy.data.objects:
            if obj.name in tile_names and obj.library is None:
                obj.color = (1.0, 1.0, 1.0, 1.0)
            elif obj.name in tile_names and obj.library is not None:
                continue

        self.report({'INFO'}, "Zoom level highlights removed.")
        return {'FINISHED'}
        
class XTD_OT_AddUUID(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.adduuid"
    bl_label = "Add unique IDs to objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        def sanitize_name(name):
            return name.replace(" ", "_")
        
        PROPERTY_UNIQUE_ID = "unique_id"
        PROPERTY_PROJECT_UUID = "project_uuid"
        blend_name = sanitize_name(os.path.splitext(os.path.basename(bpy.data.filepath))[0])
        has_changes = False

        for obj in bpy.data.objects:
            obj.data.name = obj.name
            if obj.type == 'MESH':
                object_name = sanitize_name(obj.name)
                unique_id = f"{object_name}|{blend_name}"

                if PROPERTY_UNIQUE_ID not in obj:
                    obj[PROPERTY_UNIQUE_ID] = unique_id
                    has_changes = True

                if PROPERTY_PROJECT_UUID not in obj:
                    obj[PROPERTY_PROJECT_UUID] = ""
                    has_changes = True

                obj.id_properties_ensure()
                
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                if PROPERTY_PROJECT_UUID in obj:
                    obj.property_overridable_library_set('["project_uuid"]', True)

        if has_changes:
            PopupController.show(f"{blend_name}.blend fájl {len(bpy.data.objects)} objektuma frissítve lett egyedi azonosítókkal!", buttons=[("Mentés", "bpy.ops.wm.save_mainfile"), ("Nem", None)])
        else:
            PopupController.show(f"{blend_name}.blend fájl már tartalmazza az összes szükséges property-t.", buttons=[("OK", None)])        
        return {'FINISHED'}

class XTD_OT_AppendTileResolution(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_tile_resolution"
    bl_label = "Append tile resolution"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: bpy.props.StringProperty()
    blend_file: bpy.props.StringProperty()

    def execute(self, context):
        object_names = selected_objects_names(self, context)
        bpy.ops.xtd_tools.transfermodels(transfer_mode="APPEND", source_mode="BLENDFILE", file_name=self.blend_file, objects="SELECTED", replace_mode="REPLACE", object_name=object_names)
        return {'FINISHED'}
        
class XTD_OT_LinkTileResolution(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.link_tile_resolution"
    bl_label = "Show Available Resolution"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: bpy.props.StringProperty()
    blend_file: bpy.props.StringProperty()

    def execute(self, context):
        object_names = selected_objects_names(self, context)
        bpy.ops.xtd_tools.transfermodels(transfer_mode="LINK", source_mode="BLENDFILE", file_name=self.blend_file, objects="SELECTED", replace_mode="REPLACE", object_name=object_names)
        return {'FINISHED'}
        
class XTD_OT_OptimizeTileResolution(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.optimize_tile_resolution"
    bl_label = "Optimize Tile Resolution"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: bpy.props.StringProperty()

    def execute(self, context):
        optimize_settings = {
            "BP18": {"UV_THRESHOLD": 0.00000001, "MIN_EDGE_LENGTH": 2.6, "SEARCH_DISTANCE": 0.5},
            "BP19": {"UV_THRESHOLD": 0.000000001, "MIN_EDGE_LENGTH": 1.5, "SEARCH_DISTANCE": 0.2},
            "BP20": {"UV_THRESHOLD": 0.00000001, "MIN_EDGE_LENGTH": 0.75, "SEARCH_DISTANCE": 0.2},
            "BP21": {"UV_THRESHOLD": 0.00000001, "MIN_EDGE_LENGTH": 0.6, "SEARCH_DISTANCE": 0.1},
        }
        with alive_bar(len(bpy.context.selected_objects), title='OPTIMALIZATION', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            for obj in bpy.context.selected_objects:
                bpy.context.view_layer.objects.active = obj
                if self.resolution not in optimize_settings:
                    self.report({'WARNING'}, f"No optimization parameters found for resolution {self.resolution}.")
                    return {'CANCELLED'}

                params = optimize_settings[self.resolution]
                UV_THRESHOLD = params["UV_THRESHOLD"]
                MIN_EDGE_LENGTH = params["MIN_EDGE_LENGTH"]
                SEARCH_DISTANCE = params["SEARCH_DISTANCE"]

                bpy.ops.object.mode_set(mode='OBJECT')

                bm = bmesh.new()
                bm.from_mesh(obj.data)
                bm.faces.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
                bm.verts.ensure_lookup_table()

                uv_layer = bm.loops.layers.uv.get("UVMap")
                if not uv_layer:
                    self.report({'ERROR'}, "UVMap not found.")
                    return {'CANCELLED'}

                def get_uv_area(face):
                    uv_coords = [loop[uv_layer].uv for loop in face.loops]
                    if len(uv_coords) < 3:
                        return 0
                    area = 0
                    for i in range(1, len(uv_coords) - 1):
                        v1, v2, v3 = uv_coords[0], uv_coords[i], uv_coords[i + 1]
                        area += abs((v2.x - v1.x) * (v3.y - v1.y) - (v3.x - v1.x) * (v2.y - v1.y)) / 2
                    return area

                to_delete = []
                for face in bm.faces:
                    uv_area = get_uv_area(face)
                    if uv_area < UV_THRESHOLD:
                        to_delete.append(face)

                bmesh.ops.delete(bm, geom=to_delete, context='FACES')
                bm.to_mesh(obj.data)
                obj.data.update()
                bm.free()
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
                bar()
            self.report({'INFO'}, f"Optimization completed for {len(bpy.context.selected_objects)} tiles at {self.resolution} resolution.")
            return {'FINISHED'}

class XTD_OT_SetResolution(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.set_resolution"
    bl_label = "Set Resolution"
    bl_description = "Set the tile resolution."
    bl_options = {'REGISTER', 'UNDO'}

    resolution: bpy.props.StringProperty()

    def process_object(self, obj):
        print(f"Dummy operator executed for resolution: {self.resolution}")
        return {'FINISHED'}

# Tile Helper Operators
class XTD_OT_AppendCage(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_cage"
    bl_label = "Append Cage"
    bl_description = "Append the cage object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object_names = selected_objects_names(self, context)
        bpy.ops.xtd_tools.transfermodels(transfer_mode="APPEND", source_mode="BLENDFILE", file_name="HQ_GRID_FINAL_DECIMATED.blend", objects="SELECTED", replace_mode="ADD", object_name=object_names)
        return {'FINISHED'}

class XTD_OT_AppendEmpty(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_empty"
    bl_label = "Append Empty"
    bl_description = "Append the empty object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object_names = selected_objects_names(self, context)
        bpy.ops.xtd_tools.transfermodels(transfer_mode="APPEND", source_mode="BLENDFILE", file_name="BPEmptyCubeGrid.blend", objects="SELECTED", replace_mode="ADD", object_name=object_names)
        return {'FINISHED'}

class XTD_OT_AppendPlane(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_plane"
    bl_label = "Append Plane"
    bl_description = "Append Plane objects with a unique suffix"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object_names = selected_objects_names(self, context)
        bpy.ops.xtd_tools.transfermodels(transfer_mode="APPEND", source_mode="BLENDFILE", file_name="BPMAINPROJECT_GRID_PLANE_FINAL.blend", objects="SELECTED", replace_mode="ADD", object_name=object_names)
        return {'FINISHED'}

class XTD_OT_AppendPretopo(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_pretopo"
    bl_label = "Append Pretopo"
    bl_description = "Append the pretopo object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object_names = selected_objects_names(self, context)
        bpy.ops.xtd_tools.transfermodels(transfer_mode="APPEND", source_mode="BLENDFILE", file_name="BPMAINPROJECT_GRID_PLANE_PRETOPO_FINAL.blend", objects="SELECTED", replace_mode="ADD", object_name=object_names)
        return {'FINISHED'}

class XTD_OT_AppendHQPretopo(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_hqpretopo"
    bl_label = "Append HQ Pretopo"
    bl_description = "Append the hq pretopo object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object_names = selected_objects_names(self, context)
        bpy.ops.xtd_tools.transfermodels(transfer_mode="APPEND", source_mode="BLENDFILE", file_name="BPMAINPROJECT_GRID_PLANE_HQ_PRETOPO_FINAL.blend", objects="SELECTED", replace_mode="ADD", object_name=object_names)
        return {'FINISHED'}

class XTD_OT_AppendHQLand(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_hq_land"
    bl_label = "Append HQ Land"
    bl_description = "Append the high-quality land object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object_names = selected_objects_names(self, context)
        bpy.ops.xtd_tools.transfermodels(transfer_mode="APPEND", source_mode="BLENDFILE", file_name="HQ_GRID_FINAL.blend", objects="SELECTED", replace_mode="ADD", object_name=object_names)
        return {'FINISHED'}

class XTD_OT_AppendTrueLand(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_true_land"
    bl_label = "Append True Land"
    bl_description = "Append the true land object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object_names = selected_objects_names(self, context)
        bpy.ops.xtd_tools.transfermodels(transfer_mode="APPEND", source_mode="BLENDFILE", file_name="BP19_LAND_TRUECAGE.blend", objects="SELECTED", replace_mode="ADD", object_name=object_names)
        return {'FINISHED'}

class XTD_OT_AppendTrueHouse(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_true_house"
    bl_label = "Append True House"
    bl_description = "Append the true house object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object_names = selected_objects_names(self, context)
        bpy.ops.xtd_tools.transfermodels(transfer_mode="APPEND", source_mode="BLENDFILE", file_name="TRUE_HOUSE.blend", objects="SELECTED", replace_mode="ADD", object_name=object_names)
        return {'FINISHED'}

# Colorgrade Node Operators
class XTD_OT_AddColorgrade(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.add_colorgrade"
    bl_label = "Add Colorgrade"
    bl_description = "Add color grading to materials."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.preferences.edit.use_global_undo = False
        object_names = [obj.name for obj in bpy.context.scene.objects if obj.type == 'MESH']
        object_names = ",".join(object_names)
        for mat in bpy.data.materials:
            colorgrade = bpy.data.node_groups.get("PROCEDURAL_TEXTURE_LAND")
            if colorgrade:
                continue
            else:
                bpy.ops.xtd_tools.transfermodels(transfer_mode="LINK", source_mode="BLENDFILE", file_name="COLORGRADE.blend", node_group="PROCEDURAL_TEXTURE_LAND")
                break
        all_scene_object = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        for obj in all_scene_object:
            set_active_object(context, obj)
            for mat in obj.data.materials:
                bpy.ops.object.material_slot_remove_unused()
                node_tree= mat.node_tree
                nodes = mat.node_tree.nodes
                principled = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
                principled.inputs['Base Color']
                base_color = principled.inputs['Base Color'] 
                mat.node_tree.nodes['Image Texture'].location = (-600, 200)
                link = base_color.links[0]
                link_node = link.from_node
                node_group = bpy.data.node_groups.get('PROCEDURAL_TEXTURE_LAND')
                if node_group is None:
                    node_group = bpy.data.node_groups.new(name='PROCEDURAL_TEXTURE_LAND', type='ShaderNodeTree')
                group_node = mat.node_tree.nodes.new(type='ShaderNodeGroup')
                group_node.node_tree = node_group
                group_node.location = (-200, 200)
                node_tree.links.new(group_node.outputs[0], principled.inputs[0])
                node_tree.links.new(group_node.outputs[1], principled.inputs[5])
                node_tree.links.new(group_node.outputs[2], principled.inputs[2])
                node_tree.links.new(group_node.outputs[3], principled.inputs[12])
                node_tree.links.new(group_node.outputs[4], principled.inputs[3])
                node_tree.links.new(link_node.outputs[0], group_node.inputs[0])
                principled.inputs[12].default_value = 0
            
           
        bpy.context.preferences.edit.use_global_undo = True
        return {'FINISHED'}

class XTD_OT_RemoveColorgrade(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.remove_colorgrade"
    bl_label = "Remove Colorgrade"
    bl_description = "Remove color grading from materials."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.preferences.edit.use_global_undo = False
        all_scene_object = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        for obj in all_scene_object:
            set_active_object(context, obj)
            for mat in obj.data.materials:
                colorgrade = bpy.data.node_groups.get("PROCEDURAL_TEXTURE_LAND")
                if colorgrade:
                    material.node_tree.links.remove(input_socket.links[0])
                    continue
                node_tree= mat.node_tree
                nodes = mat.node_tree.nodes
                principled = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
                base_color = principled.inputs['Base Color'] 
                # Get the link
                link = base_color.links[0]
                link_node = link.from_node

                node_tree.links.new(link_node.outputs[0], principled.inputs[0])
        return {'FINISHED'}

# Vertex Colors Operators
class XTD_OT_CreateTreeColor(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.create_tree_color"
    bl_label = "Create Tree Color Attribute"
    bl_description = "Create tree color attribute."
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        print("Dummy operator executed: Create Tree Color")
        return {'FINISHED'}

class XTD_OT_BakeVertexColors(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.bake_vertex_colors"
    bl_label = "Bake to Vertex Colors"
    bl_description = "Bake materials to vertex colors."
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        print("Dummy operator executed: Bake to Vertex Colors")
        return {'FINISHED'}

# Geometry Nodes Operators
class XTD_OT_HoleFiller(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.hole_filler"
    bl_label = "Hole Filler"
    bl_description = "Fill holes in the mesh."
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        print("Dummy operator executed: Hole Filler")
        return {'FINISHED'}

class XTD_OT_ShrinkwrapRemesh(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.shrinkwrap_remesh"
    bl_label = "Shrinkwrap Remesh"
    bl_description = "Remesh with shrinkwrap."
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        print("Dummy operator executed: Shrinkwrap Remesh")
        return {'FINISHED'}

class XTD_OT_ZSeparator(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.z_separator"
    bl_label = "Z Separator"
    bl_description = "Separate mesh by Z axis."
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        print("Dummy operator executed: Z Separator")
        return {'FINISHED'}

class XTD_OT_TreeSeparator(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.tree_separator"
    bl_label = "Tree Separator"
    bl_description = "Separate trees based on vertex colors."
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        print("Dummy operator executed: Tree Separator")
        return {'FINISHED'}

# Main SFX Operators
class XTD_OT_AddDuna(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.add_duna"
    bl_label = "Add Duna, World, Sun"
    bl_description = "Add water, world environment, and sun."
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        print("Dummy operator executed: Add Duna")
        return {'FINISHED'}
