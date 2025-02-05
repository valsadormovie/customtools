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
        tile_name = bpy.context.active_object.name
        
        row = layout.row(align=True)
        row.alignment = 'LEFT'
        box = layout.box()
        row = box.row(align=True)
        if bpy.context.active_object:
            tile_name = bpy.context.active_object.name
            row.label(text=f"Selected Object: {tile_name}", icon="OBJECT_DATA")
        else:
            row.label(text="No object selected!", icon="ERROR")
            return
            
        row.prop(bpy.context.scene, "xtd_tools_selectedobjectdata", text="OBJECT UUID DATA", emboss=False, icon_only=True, icon="TRIA_DOWN" if bpy.context.scene.xtd_tools_unvisiblemodif else "TRIA_RIGHT")
        if bpy.context.scene.xtd_tools_selectedobjectdata:
            box = layout.box()
            row = box.row(align=True)
            if "project_uuid" in bpy.context.active_object:
                grid = row.grid_flow(columns=1, align=True)
                uuid_data = UUIDManager.parse_project_uuid(bpy.context.active_object["project_uuid"])
                base_tile_name = uuid_data["uuid_base_tile_name"]
                base_tile_transfermode = uuid_data["uuid_transfermode"]
                base_tile_source = uuid_data["uuid_source_blendfile"]
                grid.label(text=f"TILE: {base_tile_name}", icon="ASSET_MANAGER")
                grid.label(text=f"TRANSFERMODE: {base_tile_transfermode}", icon="LINKED")
                grid.label(text=f"SOURCE: {base_tile_source}", icon="DECORATE_LIBRARY_OVERRIDE")
            else:
                row.label(text="Project UUID not found!", icon="ERROR")
        
        layout = self.layout
        layout.label(text=f"TILE TRANSFER MODE:", icon="AREA_JOIN")
        box = layout.box()
        row = box.row(align=True)
        row.scale_x = 0.50
        row.prop(scene, "xtd_tools_tiletools_mode", text="")

        mode_ui_elements = {
            "Append": {
                "label": "APPEND TILE OBJECT:",
                "icon": "APPEND_BLEND",
                "extra_props": [("xtd_tools_transferreplacemode", " REPLACE ")],
                "extra_text": "Choose a zoom level to be added",
            },
            "Link": {
                "label": "LINK TILE OBJECT:",
                "icon": "LINK_BLEND",
                "extra_props": [("xtd_tools_transferreplacemode", " REPLACE ")],
                "extra_text": "Choose a zoom level to be linked",
            },
            "Optimize": {
                "label": "OPTIMIZE ZOOM LEVEL:",
                "icon": "TRANSFORM_ORIGINS",
            },
            
            "Bake": {
                "label": "BAKE TEXTURE WITH ZOOM LEVEL:",
                "icon": "NODE_TEXTURE",
                "extra_text": "Choose a zoom level to be baked",
            },
            
            "ShowAvailable": {
                "label": "SHOW VISUALY ZOOM LEVEL:",
                "icon": "TRANSFORM_ORIGINS",
                "extra_buttons": [("Remove Shows", "xtd_tools.remove_shows", "CANCEL")],
            },
            
        }

        mode_settings = mode_ui_elements.get(scene.xtd_tools_tiletools_mode, {})
        
        if "extra_props" in mode_settings:
            for prop_name, label in mode_settings["extra_props"]:
                if prop_name == "xtd_tools_transferreplacemode":
                    row.scale_x = 0.50
                    row.alignment = 'EXPAND'
                    row.use_property_decorate = False
                    row.prop(scene, prop_name, text=label, icon="MOD_DATA_TRANSFER")
        
        if "label" in mode_settings:
            row = box.row(align=True)
            row.alignment = 'LEFT'
            if "extra_text" in mode_settings:
                row.scale_y = 0.5
                row.label(text=mode_settings["label"], icon=mode_settings["icon"])
                row = box.row(align=True)
                row.scale_y = 0.5
                row.scale_x = 0.5
                row.label(text=mode_settings["extra_text"])
            else:
                row.label(text=mode_settings["label"], icon=mode_settings["icon"])
        
        if scene.xtd_tools_tiletools_mode == "Bake":
            layout = self.layout
            row = box.row(align=True)
            row.separator()
            row.prop(scene, "xtd_tools_bake_texture_mode", expand=True)
            row = layout.row()
            row.alignment = 'LEFT'
            if scene.xtd_tools_bake_texture_mode == "EXTENDED":
                row = box.row(align=True)
                row.label(text="CREATE NEW:")
                row = box.row(align=True)
                row.alignment = 'EXPAND'
                row.use_property_split = True
                row.use_property_decorate = False
                row.label(text="", icon='UV')
                row.prop(scene, "xtd_tools_bake_unwrap", expand=True)
                
                row = box.row(align=True)
                row.alignment = 'EXPAND'
                row.use_property_split = True
                row.use_property_decorate = False
                row.label(text="", icon='UV_DATA')
                row.prop(scene, "xtd_tools_bake_newuvmap", expand=True)
                
                row = box.row(align=True)
                row.alignment = 'EXPAND'
                row.use_property_split = True
                row.use_property_decorate = False
                row.label(text="", icon='MATERIAL')
                row.prop(scene, "xtd_tools_bake_newmaterial", expand=True)
                
                row = box.row(align=True)
                row.alignment = 'EXPAND'
                row.use_property_split = True
                row.use_property_decorate = False
                row.label(text="", icon='TEXTURE')
                row.prop(scene, "xtd_tools_bake_texture_resolution", text="MODE")
                row = box.row(align=True)
                row.label(text="SOURCE TILE RESOLUTION:")
        
        if scene.xtd_tools_tiletools_mode == "Helper":
            layout = self.layout
            layout.separator()
            layout.label(text=f"TILE HELPER UTILITIES:", icon="MODIFIER_DATA")
            
            self.draw_accordion_box(context, layout, "ADD TILE HELPER OBJECT", "xtd_tools_tile_helper", 3, [
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
            
        else:
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
            operator_id = operator_map.get(scene.xtd_tools_tiletools_mode, "xtd_tools.showavailable_tile_resolution")

            for zoom_level in zoom_levels:
                exists, blendfile = self.check_resolution_availability(tile_name, zoom_level)
                sub_row = grid.row(align=True)
                sub_row.alert = not exists
                sub_row.enabled = exists
                op = sub_row.operator(operator_id, text=zoom_level)
                op.resolution = zoom_level
                if scene.xtd_tools_tiletools_mode != "Optimize":
                    op.blend_file = blendfile

            if "extra_props" in mode_settings:
                for prop_name, label in mode_settings["extra_props"]:
                    if prop_name != "xtd_tools_transferreplacemode":
                        row.alignment = 'LEFT' 
                        row = box.row(align=True)
                        row.scale_x = 0.5
                        row.label(text="TEXTURE RESOLUTION")
                        row.scale_x = 0.5
                        row.use_property_decorate = False
                        row.prop(scene, prop_name, text="")
                        

            if "extra_buttons" in mode_settings:
                row = box.row(align=True)
                for btn_label, op_id, icon in mode_settings["extra_buttons"]:
                    row.operator(op_id, text=btn_label, icon=icon)


    def draw_accordion_box(self, context, layout, label, prop_name, column_span, buttons):
        scene = bpy.context.scene
        row = layout.row()
        row.alignment = 'LEFT'
        
        row.prop(scene, prop_name, text=label, emboss=False, icon_only=True, icon="TRIA_DOWN" if getattr(scene, prop_name) else "TRIA_RIGHT")
        if prop_name == "xtd_tools_tile_helper":
            if getattr(scene, prop_name):
                box = layout.box()
                row = box.row(align=True)
                row.label(text="COLLECTION DESTINATION:")
                row = box.row(align=True)
                row.scale_x = 0.30
                row.prop(bpy.context.scene, "xtd_custom_collection_name")
                row = box.row(align=True)
                grid = box.grid_flow(columns=int(column_span), align=True)
                for button_text, operator, full_width in buttons:
                    if full_width:
                        grid.operator(f"xtd_tools.{operator}", text=button_text)
                    else:
                        grid.operator(f"xtd_tools.{operator}", text=button_text)
        else:
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

                if name[:12] == tile_name[:12] and zoom == zoom_level:
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
bpy.types.Scene.xtd_tools_selectedobjectdata = bpy.props.BoolProperty(name="OBJECT DATA", default=False)
bpy.types.Scene.xtd_custom_collection_name = bpy.props.StringProperty(name="NAME", description="Custom destination", default="")
bpy.types.Scene.xtd_tools_transferreplacemode = bpy.props.BoolProperty(name="Replace mode", default=False)
bpy.types.Scene.xtd_tools_colorgrade = bpy.props.BoolProperty(name="Colorgrade Node", default=False)
bpy.types.Scene.xtd_tools_vertex_colors = bpy.props.BoolProperty(name="Vertex Colors", default=False)
bpy.types.Scene.xtd_tools_geometry_nodes = bpy.props.BoolProperty(name="Geometry Nodes", default=False)
bpy.types.Scene.xtd_tools_main_sfx = bpy.props.BoolProperty(name="Main SFX", default=False)
bpy.types.Scene.xtd_tools_uuid = bpy.props.BoolProperty(name="UUID", default=False)
bpy.types.Scene.xtd_tools_tiletools_mode = bpy.props.EnumProperty(
    name="Tile Tools Mode",
    items=[
        ("Append", "Append", ""),
        ("Link", "Link", ""),
        ("Bake", "Bake", ""),
        ("Optimize", "Optimize", ""),
        ("ShowAvailable", "Show Available", ""),
        ("Helper", "Helper", ""),
    ],
    default="Append"
)

bpy.types.Scene.xtd_tools_bake_texture_mode = bpy.props.EnumProperty(
    name="Mode",
    description="Choose the bake mode",
    items=[
        ("SIMPLE", "SIMPLE", "Simple bake"),
        ("EXTENDED", "EXTENDED", "Extended bake")
    ],
    default="SIMPLE"
)

bpy.types.Scene.xtd_tools_bake_unwrap = bpy.props.EnumProperty(name='UNWRAP',
        description='UNWRAP',
        items =  (
            ('YES','YES',''),
            ('NO','NO','')
        ),
        default = 'NO'
)

bpy.types.Scene.xtd_tools_bake_newuvmap = bpy.props.EnumProperty(name='UVMAP',
        description='UVMAP',
        items =  (
            ('YES','YES',''),
            ('NO','NO','')
        ),
        default = 'NO'
)
    
bpy.types.Scene.xtd_tools_bake_newmaterial = bpy.props.EnumProperty(name='MATERIAL',
        description='MATERIAL',
        items =  (
            ('YES','YES',''),
            ('NO','NO','')
        ),
        default = 'NO'
)
    
bpy.types.Scene.xtd_tools_bake_texture_resolution = bpy.props.EnumProperty(
    name="Bake Texture Resolution",
    items=[
        ("1024", "1024x1024", ""),
        ("2048", "2048x2048", ""),
        ("4096", "4096x4096", ""),
    ],
    default="4096"
)

# ================== Show Available Operators ==================
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



# ================== Auto add UUID Operators ==================
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
            PopupController(title="UUID GENERATOR", message=f"{blend_name}.blend fájl {len(bpy.data.objects)} objektuma frissítve lett egyedi azonosítókkal!", buttons=[("Mentés", "wm.save_mainfile", "CHECKMARK"), ("Nem", "", "CHECKMARK")])
        else:
            PopupController(title="UUID GENERATOR", message=f"{blend_name}.blend fájl már tartalmazza az összes szükséges property-t.", buttons=[("OK", None, "CHECKMARK")])
        return {'FINISHED'}



# ================== Tile Append/Link Operators ==================
class XTD_OT_AppendTileResolution(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_tile_resolution"
    bl_label = "Append tile resolution"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: bpy.props.StringProperty()
    blend_file: bpy.props.StringProperty()

    def execute(self, context):
        global_settings.UUIDManager.ensure_project_uuid()
        global_settings.UUIDManager.deduplicate_project_uuids()
        transferreplacemode = bpy.context.scene.xtd_tools_transferreplacemode
        if transferreplacemode:
            selected_replace_mode = "REPLACE"
        else:
            selected_replace_mode = "ADD"
        return bpy.ops.xtd_tools.transfermodels(transfer_mode="APPEND", source_mode="MASTERFILE", objects="SELECTED", replace_mode=selected_replace_mode, zoom_level=self.resolution)
        
class XTD_OT_LinkTileResolution(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.link_tile_resolution"
    bl_label = "Show Available Resolution"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: bpy.props.StringProperty()
    blend_file: bpy.props.StringProperty()

    def execute(self, context):
        global_settings.UUIDManager.ensure_project_uuid()
        global_settings.UUIDManager.deduplicate_project_uuids()
        transferreplacemode = bpy.context.scene.xtd_tools_transferreplacemode
        if transferreplacemode:
            selected_replace_mode = "REPLACE"
        else:
            selected_replace_mode = "ADD"
        return bpy.ops.xtd_tools.transfermodels(transfer_mode="LINK", source_mode="MASTERFILE", objects="SELECTED", replace_mode=selected_replace_mode, zoom_level=self.resolution)

# ================ Bake Tile Operators ================
class XTD_OT_BakeTileResolution(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.bake_tile_resolution"
    bl_label = "Bake tile Resolution"
    bl_options = {'REGISTER', 'UNDO'}

    resolution: bpy.props.StringProperty()
    blend_file: bpy.props.StringProperty()

    def execute(self, context):
        import io
        from contextlib import redirect_stdout

        stdout = io.StringIO()
        statusheader(bl_label="Bake tile Resolution", functiontext="Working selected objects...")
        with redirect_stdout(stdout):
            scene = bpy.context.scene
            scene.render.engine = 'CYCLES'
            scene.cycles.feature_set = 'EXPERIMENTAL'
            scene.cycles.device = 'GPU'
            scene.cycles.use_denoising = False
            scene.cycles.samples = 4
            scene.cycles.preview_samples = 4
            scene.cycles.max_bounces = 4
            scene.cycles.diffuse_bounces = 4
            scene.cycles.glossy_bounces = 0
            scene.cycles.transmission_bounces = 0
            scene.cycles.volume_bounces = 0
            scene.cycles.transparent_max_bounces = 0
            scene.cycles.sample_clamp_direct = 0
            scene.cycles.sample_clamp_indirect = 2
            scene.cycles.blur_glossy = 1
            scene.cycles.caustics_reflective = False
            scene.cycles.caustics_refractive = False
            scene.cycles.use_auto_tile = False
            scene.cycles.bake_type = 'DIFFUSE'
            scene.render.bake.use_pass_direct = False
            scene.render.bake.use_pass_indirect = False
            scene.render.bake.use_selected_to_active = True
            scene.render.bake.cage_extrusion = 0.5
            scene.render.bake.max_ray_distance = 50
            
            selected_objects = bpy.context.selected_objects
            if not selected_objects:
                self.report({'WARNING'}, "No objects selected.")
                return {'CANCELLED'}

            selected_objects = [obj for obj in selected_objects]
            temp_collection_name = "TEMP_BAKE"
            texture_resolution = int(scene.xtd_tools_bake_texture_resolution)
            
            bpy.ops.object.select_all(action = 'DESELECT')
            global_settings.UUIDManager.ensure_project_uuid()
            global_settings.UUIDManager.deduplicate_project_uuids()
            
            
            with alive_bar(len(selected_objects), title='   ', length=50, max_cols=98, bar='filling') as bar:
                
                for obj in selected_objects:
                    bpy.ops.object.select_all(action = 'DESELECT')
                    obj = bpy.data.objects[obj.name]
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj
                    if scene.xtd_tools_bake_newuvmap == "YES":
                        for uvmap in obj.data.uv_layers[:-1]:
                            obj.data.uv_layers.remove(obj.data.uv_layers[0])
                    
                    uuid_data = global_settings.UUIDManager.parse_project_uuid(obj["project_uuid"])
                    tile_name_base = uuid_data["uuid_base_tile_name"] 
                    tile_name = f"{tile_name_base}_{UUIDManager.generate_random_hash()}"
                    
                    if scene.xtd_tools_bake_newmaterial == "YES":
                        obj.data.materials.clear()
                        
                        material_name = f"M_{tile_name}"
                        material = bpy.data.materials.new(name=material_name)
                        material.use_nodes = True
                        obj.data.materials.append(material)
                        
                        image_name = f"T_{tile_name}"
                        image = bpy.data.images.new(name=image_name, width=texture_resolution, height=texture_resolution, alpha=False)
                        
                        nodes = material.node_tree.nodes
                        links = material.node_tree.links
                        
                        for node in nodes:
                            nodes.remove(node)
                        
                        texture_node = nodes.new('ShaderNodeTexImage')
                        texture_node.image = image
                        texture_node.select = True
                        material.node_tree.nodes.active = texture_node
                        
                        bsdf_node = nodes.new('ShaderNodeBsdfDiffuse')
                        output_node = nodes.new('ShaderNodeOutputMaterial')
                        
                        links.new(texture_node.outputs['Color'], bsdf_node.inputs['Color'])
                        links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

                    if scene.xtd_tools_bake_unwrap == "YES":
                        bpy.ops.object.mode_set(mode = 'EDIT')
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.uv.smart_project()
                        bpy.ops.object.mode_set(mode = 'OBJECT')

                    bpy.ops.xtd_tools.transfermodels(
                        transfer_mode="LINK",
                        source_mode="MASTERFILE",
                        objects="SELECTED",
                        base_collection="COLLECTIONNAME",
                        collection_name=temp_collection_name,
                        zoom_level=self.resolution
                    )

                    temp_collection = bpy.data.collections.get(temp_collection_name)
                    if not temp_collection:
                        self.report({'WARNING'}, "TEMP_BAKE collection not found after linking.")
                        return {'CANCELLED'}

                    linked_objects = [o for o in temp_collection.objects if o.library]
                    if not linked_objects:
                        self.report({'WARNING'}, "No linked objects found in TEMP_BAKE.")
                        return {'CANCELLED'}

                    bpy.ops.object.select_all(action='DESELECT')
                    for linked_obj in linked_objects:
                        linked_obj.select_set(True)

                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)

                    try:
                        bpy.ops.object.bake(type='DIFFUSE')
                    except Exception as e:
                        self.report({'ERROR'}, f"Bake failed: {e}")
                        return {'CANCELLED'}

                    for linked_obj in linked_objects:
                        temp_collection.objects.unlink(linked_obj)
                    bar()
                bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
                bpy.ops.object.select_all(action = 'DESELECT')
                    
            bpy.ops.object.select_all(action = 'DESELECT')
            bpy.data.collections.remove(temp_collection)
            
            self.report({'INFO'}, f"Successfully baked {self.resolution} resolution for {obj.name}.")
            return {'FINISHED'}

# ================== Tile Optimizer Operator ==================
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



# ================== Helper Object Tiles Operators ==================
class XTD_OT_AppendCage(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_cage"
    bl_label = "Append Cage"
    bl_description = "Append the cage object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global_settings.UUIDManager.ensure_project_uuid()
        global_settings.UUIDManager.deduplicate_project_uuids()
        if bpy.context.scene.xtd_custom_collection_name == "":
            collection_name = "CAGE"
        else:
            collection_name = f"{bpy.context.scene.xtd_custom_collection_name}"
        return bpy.ops.xtd_tools.transfermodels(source_mode="BLENDFILE", file_name="HQ_GRID_FINAL_DECIMATED.blend", base_collection="COLLECTIONNAME", collection_name=collection_name)

class XTD_OT_AppendEmpty(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_empty"
    bl_label = "Append Empty"
    bl_description = "Append the empty object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global_settings.UUIDManager.ensure_project_uuid()
        global_settings.UUIDManager.deduplicate_project_uuids()
        
        if bpy.context.scene.xtd_custom_collection_name == "":
            collection_name = "EMPTY"
        else:
            collection_name = f"{bpy.context.scene.xtd_custom_collection_name}"
        return bpy.ops.xtd_tools.transfermodels(source_mode="BLENDFILE", file_name="BPEmptyCubeGrid.blend", base_collection="COLLECTIONNAME", collection_name=collection_name)

class XTD_OT_AppendPlane(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_plane"
    bl_label = "Append Plane"
    bl_description = "Append Plane objects with a unique suffix"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global_settings.UUIDManager.ensure_project_uuid()
        global_settings.UUIDManager.deduplicate_project_uuids()
        
        if bpy.context.scene.xtd_custom_collection_name == "":
            collection_name = "CAGE"
        else:
            collection_name = f"{bpy.context.scene.xtd_custom_collection_name}"
        return bpy.ops.xtd_tools.transfermodels(source_mode="BLENDFILE", file_name="BPMAINPROJECT_GRID_PLANE_FINAL.blend", base_collection="COLLECTIONNAME", collection_name=collection_name)

class XTD_OT_AppendPretopo(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_pretopo"
    bl_label = "Append Pretopo"
    bl_description = "Append the pretopo object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global_settings.UUIDManager.ensure_project_uuid()
        global_settings.UUIDManager.deduplicate_project_uuids()
        if bpy.context.scene.xtd_custom_collection_name == "":
            collection_name = "CAGE"
        else:
            collection_name = f"{bpy.context.scene.xtd_custom_collection_name}"
        return bpy.ops.xtd_tools.transfermodels(source_mode="BLENDFILE", file_name="BPMAINPROJECT_GRID_PLANE_PRETOPO_FINAL.blend", base_collection="COLLECTIONNAME", collection_name=collection_name)

class XTD_OT_AppendHQPretopo(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_hqpretopo"
    bl_label = "Append HQ Pretopo"
    bl_description = "Append the hq pretopo object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global_settings.UUIDManager.ensure_project_uuid()
        global_settings.UUIDManager.deduplicate_project_uuids()
        if bpy.context.scene.xtd_custom_collection_name == "":
            collection_name = "CAGE"
        else:
            collection_name = f"{bpy.context.scene.xtd_custom_collection_name}"
        return bpy.ops.xtd_tools.transfermodels(source_mode="BLENDFILE", file_name="BPMAINPROJECT_GRID_PLANE_HQ_PRETOPO_FINAL.blend", base_collection="COLLECTIONNAME", collection_name=collection_name)

class XTD_OT_AppendHQLand(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_hq_land"
    bl_label = "Append HQ Land"
    bl_description = "Append the high-quality land object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global_settings.UUIDManager.ensure_project_uuid()
        global_settings.UUIDManager.deduplicate_project_uuids()
        if bpy.context.scene.xtd_custom_collection_name == "":
            collection_name = "HELPER"
        else:
            collection_name = f"{bpy.context.scene.xtd_custom_collection_name}"
        return bpy.ops.xtd_tools.transfermodels(source_mode="BLENDFILE", file_name="HQ_GRID_FINAL.blend", base_collection="COLLECTIONNAME", collection_name=collection_name)

class XTD_OT_AppendTrueLand(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_true_land"
    bl_label = "Append True Land"
    bl_description = "Append the true land object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global_settings.UUIDManager.ensure_project_uuid()
        global_settings.UUIDManager.deduplicate_project_uuids()
        if bpy.context.scene.xtd_custom_collection_name == "":
            collection_name = "HELPER"
        else:
            collection_name = f"{bpy.context.scene.xtd_custom_collection_name}"
        return bpy.ops.xtd_tools.transfermodels(source_mode="BLENDFILE", file_name="BP19_LAND_TRUECAGE.blend", base_collection="COLLECTIONNAME", collection_name=collection_name)

class XTD_OT_AppendTrueHouse(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.append_true_house"
    bl_label = "Append True House"
    bl_description = "Append the true house object."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global_settings.UUIDManager.ensure_project_uuid()
        global_settings.UUIDManager.deduplicate_project_uuids()
        if bpy.context.scene.xtd_custom_collection_name == "":
            collection_name = "HELPER"
        else:
            collection_name = f"{bpy.context.scene.xtd_custom_collection_name}"
        return bpy.ops.xtd_tools.transfermodels(source_mode="BLENDFILE", file_name="TRUE_HOUSE.blend", base_collection="COLLECTIONNAME", collection_name=collection_name)


# ================ Colorgrade Node Operators ================
class XTD_OT_AddColorgrade(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.add_colorgrade"
    bl_label = "Add Colorgrade"
    bl_description = "Add color grading to materials."
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
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



# ================ Vertex Colors Operators ================
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



# ================ Geometry Nodes Operators ================
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



# ================ Main SFX Operators ================
class XTD_OT_AddDuna(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.add_duna"
    bl_label = "Add Duna, World, Sun"
    bl_description = "Add water, world environment, and sun."
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        print("Dummy operator executed: Add Duna")
        return {'FINISHED'}