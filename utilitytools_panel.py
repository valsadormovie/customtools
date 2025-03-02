#-------------------------------------------------
#-UTILITYTOOLS_PANEL.py
#-------------------------------------------------

from .global_settings import *
disable_cache()
# ================== PANEL =================
class XTD_PT_UtilityTools(bpy.types.Panel):
    bl_label = "UTILITY TOOLS"
    bl_idname = "XTD_PT_utilitytools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return VisibilityController.check_visibility(context, panel_name = "utilitytools_panel", require_selected=True)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        for i in range(0,2,2):
            row = box.row(align=True)
            row.label(text="Merge Z AXIS by Distance:", icon="MESH_GRID")
            row = box.row(align=True)
            row.scale_x = 0.30
            row.label(text="Distance:")
            row.scale_x = 0.30
            row.prop(bpy.context.scene, "mergezaxis")
            row.scale_x = 0.40
            
            
            check_selected_active_button(row)
            row.operator("xtd_tools.merge_by_distance", text="MERGE", icon="AREA_JOIN")
            
            row = box.row(align=True)
            row.separator()
            row.operator("xtd_tools.smart_grid_merge", text="AUTO SMART MERGE", icon="AREA_JOIN")
            
        layout = self.layout
        box = layout.box()
        for i in range(0,2,2):
            row = box.row(align=True)
            row.label(text="LAND GENERATOR:", icon="MESH_DATA")
            row = box.row(align=True)
            check_selected_active_button(row)
            row.operator("xtd_tools.makehqland", text="MAKE HQ LAND", icon='SNAP_EDGE')
            
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.label(text="MESH TOOLS:", icon="MESH_DATA")
            
        for i in range(0,2,2):
            row = box.row(align=True)
            check_selected_active_button(row)
            row.operator("xtd_tools.tritoquad", text="Quad To Triangle", icon='MOD_TRIANGULATE')
            row.operator("xtd_tools.quadtotri", text="Triangle to Quad", icon='MOD_DECIM')
            
        for i in range(0,2,2):
            row = box.row(align=True)
            check_selected_active_button(row)
            row.operator("xtd_tools.disolvesharpedges", text="Disolve all sharp edges", icon='SHARPCURVE')
            row.operator("xtd_tools.nonmanifoldedgesplit", text="Nonmanifold Edgesplit", icon='MOD_EDGESPLIT')
            
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.label(text="MERGE BY NAME PREFIX LENGTH:", icon="MOD_BOOLEAN")
        row = box.row(align=True)
        row.scale_x = 0.30
        row.label(text="LENGTH:")
        row.scale_x = 0.30
        row.prop(bpy.context.scene, "xtd_tools_mergeprefix_length")
        row.scale_x = 0.40
        row = box.row(align=True)
        row.operator("xtd_tools.merge_by_nameprefix", text="MERGE BY NAME PREFIX", icon='MOD_BOOLEAN')

        row = box.row(align=True)
        row.operator("xtd_tools.lilycapturemerger", text="MERGE MATERIAL TEXTURES", icon='TEXTURE')
        
        layout = self.layout
        layout.label(text="EXCLUDE VECTORS:", icon="HANDLE_VECTOR")
        box = layout.box()
        row = layout.row()
        row.label(text=f"{float(10 ** int(bpy.context.scene.xtd_tools_uv_threshold_exp))}", icon="MOD_BOOLEAN")
        row = layout.row()
        row = box.row(align=True)
        grid = row.grid_flow(columns=2, align=True)
        grid.prop(bpy.context.scene, "xtd_tools_max_edge_length", slider=True, text="Edge length")
        grid.prop(bpy.context.scene, "xtd_tools_max_brightness", slider=True, text="Max brightness")
        row = box.row(align=True)
        grid = row.grid_flow(columns=2, align=True)
        grid.prop(bpy.context.scene, "xtd_tools_similarity_threshold", slider=True, text="Similarity")
        grid.prop(bpy.context.scene, "xtd_tools_uv_threshold_exp", slider=True, text="UV Sensivity")
        box = layout.box()
        row = box.row(align=True)
        grid = row.grid_flow(columns=3, align=True)
        grid.prop(bpy.context.scene, "xtd_tools_similarity_vector_x", slider=True, icon='AXIS_FRONT')
        grid.prop(bpy.context.scene, "xtd_tools_similarity_vector_y", slider=True, icon='AXIS_SIDE')
        grid.prop(bpy.context.scene, "xtd_tools_similarity_vector_z", slider=True, icon='AXIS_TOP')
        row = layout.row()
        row = box.row(align=True)
        row.operator("xtd_tools.optimizebp16", text="OPTIMIZE WITH VECTORS", icon='MOD_BOOLEAN') 
        row = layout.row()       
        row.scale_y = 2
        row.separator()
        
        layout = self.layout
        layout.label(text="MATERIAL TOOLS:", icon="HANDLE_VECTOR")
        row = layout.row()
        box = layout.box()
        row = box.row(align=True)
        row.operator("xtd_tools.purgeunusedmaterial", text="PURGE UNUSED", icon='MATERIAL_DATA')
        row = box.row(align=True)
        row.operator("xtd_tools.remove_allmaterials", text="REMOVE ALL", icon="TRASH")
        
        layout = self.layout
        box = layout.box()
        for i in range(0,2,2):
            row = box.row(align=True)
            row.label(text="OTHER:", icon="ORPHAN_DATA")
            row = box.row(align=True)
            check_selected_active_button(row)
            row.operator("xtd_tools.makeconvexhullobject", text="Transform to Convexhull", icon='MESH_CONE')

bpy.types.Scene.mergezaxis = bpy.props.StringProperty(name="", description="Distance", default="200")



# ================ OPERATORS ================

# ----------- Merge By Distance -----------
class XTD_OT_MergeByDistance_OnlyXY(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.merge_by_distance_onlyxy"
    bl_label = "Merge Z AXIS by Distance"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        all_objects = bpy.context.scene.objects
        objects_to_join = [base_obj]
        
        for obj in all_objects:
            if not obj.visible_get():
                continue
            if obj == base_obj or obj.type != 'MESH':
                continue
            
            if is_within_origin_distance(base_obj, obj, distance_limit):
                objects_to_join.append(obj)
        
        if len(objects_to_join) > 1:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in objects_to_join:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = base_obj
            bpy.ops.object.join()
            print(f"{len(objects_to_join)} objektum összeillesztve a(z) {base_obj.name} objektummal.")
        else:
            print(f"A(z) {base_obj.name} objektumhoz nem található másik objektum {distance_limit} méteres origin távolságon belül.")
        return {'FINISHED'}
        
def is_within_origin_distance(obj1, obj2, distance_limit=100):
    o1 = obj1.matrix_world.translation
    o2 = obj2.matrix_world.translation
    
    o1_xy = Vector((o1.x, o1.y))
    o2_xy = Vector((o2.x, o2.y))
    
    distance = (o1_xy - o2_xy).length
    return distance <= distance_limit


def is_above_and_within_distance(obj1, obj2, distance_limit=100):
    obj1_bb_min_z = min(
        [(obj1.matrix_world @ Vector(corner)).z for corner in obj1.bound_box]
    )
    obj2_bb_max_z = max(
        [(obj2.matrix_world @ Vector(corner)).z for corner in obj2.bound_box]
    )
    if obj2_bb_max_z <= obj1_bb_min_z:
        return False
    
    obj1_xy = Vector(obj1.location.xy)
    obj2_xy = Vector(obj2.location.xy)
    xy_distance = (obj1_xy - obj2_xy).length
    
    return xy_distance <= distance_limit
    
# ----------- Merge By Distance -----------
class XTD_OT_MergeByDistance(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.merge_by_distance"
    bl_label = "Merge Z AXIS by Distance"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bl_label = self.bl_label
        selected_objs = [obj for obj in bpy.context.selected_objects]
        
        mergezaxis = float(bpy.context.scene.mergezaxis)
        if not selected_objs:
            print("Nincs más kijelölt objektum!")
            return
            
        bpy.ops.object.select_all(action='DESELECT')
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Detect small size base grids...")
        #-STATUS-BAR--------------------------------------------------------------------------
        
        smallbaseobjects = []
        
        with alive_bar(len(bpy.context.scene.objects), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            for obj in bpy.context.scene.objects:
                if not obj.visible_get():
                    continue
                obj.select_set(True)

                if not global_settings.ProcessManager.is_running():
                    self.report({'INFO'}, "Process stopped by user.")
                    
                    return {'CANCELLED'}
                baseobject = bpy.context.scene.objects.get(obj.name)
                if not baseobject:
                    continue
                if baseobject:
                    if baseobject.dimensions[0] < 415: 
                        smallbaseobjects.append(baseobject)
                        continue
                        
                    if baseobject.dimensions[1] < 306:
                        smallbaseobjects.append(baseobject)
                        continue
                bar() 
                
            bpy.ops.object.select_all(action='DESELECT')
        
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext=f"Merge small size grids ({len(smallbaseobjects)}) to base grids...")
        #-STATUS-BAR--------------------------------------------------------------------------
        
        selected_objs = [obj for obj in bpy.context.scene.objects if obj in selected_objs and obj.type == 'MESH']
        
        smallbaseobjects = [obj for obj in bpy.context.scene.objects if obj in smallbaseobjects and obj.type == 'MESH']
        
        with alive_bar(len(selected_objs), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            for base_obj in selected_objs:
                if not obj.visible_get():
                    continue
                if not global_settings.ProcessManager.is_running():
                    clear_reports()
                    self.report({'INFO'}, "Process stopped by user.")
                    
                    return {'CANCELLED'}
                objects_to_join = [base_obj]
                
                for obj in smallbaseobjects:
                    if obj == base_obj:
                        continue
                    
                    try:
                        if is_above_and_within_distance(base_obj, obj, distance_limit=mergezaxis) and obj.type == 'MESH':
                            objects_to_join.append(obj)
                    except:
                        continue
                
                if len(objects_to_join) > 0:
                    bpy.context.view_layer.objects.active = base_obj
                    
                    for obj in objects_to_join:
                        try:
                            obj.select_set(True)
                        except:
                            self.report({'ERROR'}, f"Merge failed: {e}")
                            return {'CANCELLED'}
                    
                        if len(bpy.context.selected_objects) > 1:
                            bpy.ops.object.join()
                        else:
                            obj.name = obj.name + "_szar"
                            clear_reports()
                        
                    bpy.ops.object.select_all(action = 'DESELECT')


                bar() 
        bpy.ops.object.select_all(action = 'DESELECT')
        return {'FINISHED'}

def is_above_and_within_distance(obj1, obj2, distance_limit=100):
    obj1_bb_min_z = min(
        [(obj1.matrix_world @ Vector(corner)).z for corner in obj1.bound_box]
    )
    obj2_bb_max_z = max(
        [(obj2.matrix_world @ Vector(corner)).z for corner in obj2.bound_box]
    )
    if obj2_bb_max_z <= obj1_bb_min_z:
        return False
    
    obj1_xy = Vector(obj1.location.xy)
    obj2_xy = Vector(obj2.location.xy)
    xy_distance = (obj1_xy - obj2_xy).length
    
    return xy_distance <= distance_limit
    
# -------------------- Smart Merge -------------------------
class XTD_OT_SmartGridMerge(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.smart_grid_merge"
    bl_label = "Smart Grid Merge"
    bl_description = "Join models based on predefined Empty Cube grid"
    bl_options = {'REGISTER', 'UNDO'}
    batch_mode = False
    
    def execute(self, context):
        bl_label = self.bl_label
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Search Helper Grid blend file...")
        #-STATUS-BAR--------------------------------------------------------------------------
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
        bpy.ops.object.select_all(action='DESELECT')
        temp_collection = bpy.data.collections.get("TEMP_WORKING")
        if not temp_collection:
            temp_collection = bpy.data.collections.new("TEMP_WORKING")
            bpy.context.scene.collection.children.link(temp_collection)
            
        external_blend_path = os.path.join(os.path.dirname(bpy.context.scene.master_txt_filepath), "BPEMPTY.blend")
        scene_objects = {obj.name[:11] for obj in bpy.context.scene.objects}
        matched_objects = set()

        with bpy.data.libraries.load(external_blend_path, link=True) as (data_from, data_to):
            external_objects = {obj[:11]: obj for obj in data_from.objects}
            matched_objects = {external_objects[key] for key in scene_objects if key in external_objects}
            data_to.objects = list(matched_objects)

        for obj in data_to.objects:
            if not obj.visible_get():
                continue
            if obj is not None:
                temp_collection.objects.link(obj)
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Copy plane origin to small base objects...")
        #-STATUS-BAR--------------------------------------------------------------------------
        
        temp_collection_objects = [o for o in temp_collection.objects]

        saved_location = bpy.data.scenes['Scene'].cursor.location.xyz
        
        with alive_bar(len(temp_collection_objects), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            for obj in temp_collection_objects:
                if not obj.visible_get():
                    continue
                bpy.context.view_layer.objects.active = obj
                baseobject = bpy.data.objects.get(obj.name[:11])
                if baseobject:
                    baseobject["merge"] = True
                    bpy.data.scenes['Scene'].cursor.location = obj.location
                    baseobject.select_set(True)
                    bpy.context.view_layer.objects.active = baseobject
                    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                    obj.select_set(False)
                    baseobject.select_set(False)
                bar()
            bpy.ops.object.select_all(action='DESELECT')
        bpy.data.scenes['Scene'].cursor.location.xyz = saved_location
        
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Purge helpers...")
        #-STATUS-BAR--------------------------------------------------------------------------
        
        if len(temp_collection.objects) > 0:
            for obj in temp_collection.objects:
                temp_collection.objects.unlink(obj)
        
        if len(temp_collection.objects) == 0:
            bpy.data.collections.remove(temp_collection)
        
        main_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and "merge" in obj]
        with alive_bar(len(main_objects), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            for obj in main_objects:
                if not obj.visible_get():
                    continue
                obj.select_set(True)
                bar()
        
        try:
            bpy.ops.xtd_tools.merge_by_distance()
        except:
            return {'CANCELLED'}
        
        for obj in bpy.data.objects:
            UUIDManager.ensure_project_uuid()
        
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        clear_reports()
        self.report({'INFO'}, "Smart Grid Merge completed successfully!")
        PopupController(title="UUID GENERATOR", message=f"{len(bpy.data.objects)} objektuma frissítve lett az új nevekkel!", buttons=[("Mentés", "wm.save_mainfile", "CHECKMARK"), ("Nem", "", "CHECKMARK")])
        return {'FINISHED'}
    
class XTD_OT_optimizebp16(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.optimizebp16"
    bl_label = "Merge and optimize"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        
        
        bl_label = self.bl_label
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Separate objects only by XY coordinates to Quad...")
        #-STATUS-BAR--------------------------------------------------------------------------
        keyboard.add_hotkey("esc", ProcessManager.stop)
        ProcessManager.start()
        
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        selected_objs = list(bpy.context.selected_objects)
        if not selected_objs:
            return {'CANCELLED'}
        
        with alive_bar(len(selected_objs), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            bpy.ops.object.select_all(action = 'DESELECT')
            for obj in selected_objs:
                bpy.ops.object.select_all(action = 'DESELECT')
                if not obj.visible_get():
                    continue
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                if not ProcessManager.is_running():
                    self.report({'INFO'}, "Process stopped by user.")
                    return {'CANCELLED'}
                if obj is None or obj.type != 'MESH':
                    return
                
                # Minimalizáljuk a módváltásokat
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_mode(type='FACE')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                
                bm = bmesh.new()
                bm.from_mesh(obj.data)
                # Egyszer hívjuk meg az ensure_lookup_table függvényeket
                bm.faces.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
                bm.verts.ensure_lookup_table()
                
                uv_layer = bm.loops.layers.uv.get("UVMap")
                if uv_layer is None:
                    bm.free()
                    raise ValueError(f"UV layer not found on the object.")
                
                helper_faces = set()
                up_vec = Vector((bpy.context.scene.xtd_tools_similarity_vector_x, bpy.context.scene.xtd_tools_similarity_vector_y, bpy.context.scene.xtd_tools_similarity_vector_z)).normalized()
                similarity_threshold = bpy.context.scene.xtd_tools_similarity_threshold
                # Egyetlen ciklusban végigmegyünk a face-eken
                for face in bm.faces:
                    if face.normal.normalized().dot(up_vec) > similarity_threshold:
                        continue
                    uv_coords = [loop[uv_layer].uv for loop in face.loops]
                    if len(uv_coords) < 3:
                        return 0

                    area = 0
                    for i in range(1, len(uv_coords) - 1):
                        v1 = uv_coords[0]
                        v2 = uv_coords[i]
                        v3 = uv_coords[i + 1]
                        area += abs((v2.x - v1.x) * (v3.y - v1.y) - (v3.x - v1.x) * (v2.y - v1.y)) / 2
                    uv_area = area
                    # Rövid él vizsgálata
                    has_short_edge = any(
                        (edge.verts[0].co - edge.verts[1].co).length < int(bpy.context.scene.xtd_tools_max_edge_length)
                        for edge in face.edges
                    )
                    brightness = face.normal.dot(up_vec)
                    # Két feltétel alapján gyűjtjük a segédface-eket
                    if has_short_edge and uv_area < (-10 * int(bpy.context.scene.xtd_tools_uv_threshold_exp)):
                        helper_faces.add(face)
                    if uv_area < (-10 * int(bpy.context.scene.xtd_tools_uv_threshold_exp)) * 100 and brightness < int(bpy.context.scene.xtd_tools_max_brightness):
                        helper_faces.add(face)
                
                # Egyszerűsítve: helper_faces-t közvetlenül set-ként tároljuk
                combined_faces = list(helper_faces)
                
                # Egy ciklusban gyűjtjük az él alapú adatokat
                to_split = set()
                to_splitmerge = set()
                for edge in bm.edges:
                    if edge.is_boundary:
                        to_splitmerge.update(edge.verts)
                    else:
                        edge_length = (edge.verts[0].co - edge.verts[1].co).length
                        if edge_length > 40:
                            to_split.add(edge)
                        else:
                            to_splitmerge.update(edge.verts)
                
                # Például: finalmerge az olyan vert-ek, amelyek szerepelnek a hosszú élekből, de nincsenek a to_splitmerge-ben
                finalmerge = set()
                for edge in to_split:
                    finalmerge.update(edge.verts)
                finalmerge = finalmerge - to_splitmerge
                
                # Gyűjtjük az összes él vertjét egyszer
                finalmergeverts = set()
                for edge in bm.edges:
                    finalmergeverts.update(edge.verts)
                
                # Jelöljük ki a combined_faces-et
                for face in combined_faces:
                    face.select = True   
                    
                bmesh.ops.delete(bm, geom=combined_faces, context='FACES')

                # Egyetlen lookup table frissítés, ha szükséges
                bm.faces.ensure_lookup_table()      
                bm.edges.ensure_lookup_table()
                bm.verts.ensure_lookup_table()
                
                # Ha van finalmerge, állítsuk az éleket nem simára
                if finalmerge:
                    for edge in bm.edges:
                        edge.smooth = False
                
                bm.edges.ensure_lookup_table()
                bm.verts.ensure_lookup_table() 
                
                finalmergeverts = {vert for vert in finalmergeverts if vert.is_valid}  
                finalmergeverts = list(finalmergeverts)
                if finalmergeverts:
                    bmesh.ops.remove_doubles(bm, verts=finalmergeverts, dist=0.01)
                    
                bm.to_mesh(obj.data)
                obj.data.update()
                bm.free()
                
                bpy.ops.object.mode_set(mode='OBJECT')
                
                bpy.ops.mesh.customdata_custom_splitnormals_clear()

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                try:
                    bpy.ops.mesh.faces_select_linked_flat(sharpness=0.244346)
                    bpy.ops.mesh.split()
                    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                    bpy.ops.mesh.select_similar(type='VERT_NORMAL', compare='EQUAL', threshold=1.5e-05)
                except Exception as e:
                    print(f"Hiba: {e}")
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
                bpy.ops.mesh.delete(type='FACE')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=True)
                
                bpy.ops.object.mode_set(mode='OBJECT')
               
                bar()
                
        bpy.ops.object.select_all(action='DESELECT')
        ProcessManager.reset()

        return {'FINISHED'}

bpy.types.Scene.xtd_tools_uv_threshold_exp = bpy.props.FloatProperty(
        name="UV Sensivity",
        default=-1,
        min=-100,
        max=-1,
        step=1, 
        precision=0
    )
    
bpy.types.Scene.xtd_tools_max_edge_length = bpy.props.FloatProperty(
        name="Max Edge_length",
        default=1,
        min=0,
        max=15,
        step=1, 
        precision=1
    )

bpy.types.Scene.xtd_tools_max_brightness = bpy.props.FloatProperty(
        name="Max normal brightness",
        default=1,
        min=-1,
        max=1,
        step=1, 
        precision=1
    )

bpy.types.Scene.xtd_tools_similarity_threshold = bpy.props.FloatProperty(
        name="Similarity Threshold",
        default=0.999,
        min=0.0,
        max=1.0,
        step=1,
        precision=3
    )

bpy.types.Scene.xtd_tools_similarity_vector_x = bpy.props.FloatProperty(
        name="X",
        default=0,
        min=-1.0,
        max=1.0,
        step=1,
        precision=3
    )

bpy.types.Scene.xtd_tools_similarity_vector_y = bpy.props.FloatProperty(
        name="Y",
        default=0,
        min=-1.0,
        max=1.0,
        step=1,
        precision=3
    )

bpy.types.Scene.xtd_tools_similarity_vector_z = bpy.props.FloatProperty(
        name="Z",
        default=1,
        min=-1.0,
        max=1.0,
        step=1,
        precision=3
    )

class XTD_OT_makehqland(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.makehqland"
    bl_label = "Make HQ land"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        scene = bpy.context.scene
        import io
        from contextlib import redirect_stdout
        processed_count = 0 
        CACHE_CLEAR_INTERVAL = 4
        keyboard.add_hotkey("esc", ProcessManager.stop)
        ProcessManager.start()
        stdout = io.StringIO()
        
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected.")
            return {'CANCELLED'}
        selected_objects = [obj for obj in selected_objects]
        
        statusheader(bl_label="MAKE HQ LANDS", functiontext="Working selected objects...")
        with alive_bar(len(selected_objects), title='   ', length=50, max_cols=98, bar='filling') as bar:
            with redirect_stdout(stdout):
                bpy.ops.object.select_all(action = 'DESELECT')
                global_settings.UUIDManager.ensure_project_uuid()
                global_settings.UUIDManager.deduplicate_project_uuids()
                
                for obj in selected_objects:
                    if not obj.visible_get():
                        continue
                    if not ProcessManager.is_running():
                        self.report({'INFO'}, "Process stopped by user.")
                        return {'CANCELLED'}
                    bpy.ops.object.select_all(action = 'DESELECT')
                    obj = bpy.data.objects[obj.name]
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.xtd_tools.transfermodels(transfer_mode="APPEND", source_mode="MASTERFILE", objects="SELECTED", replace_mode="ADD", base_collection="COLLECTIONNAME", collection_name="TEMP_LINKED", zoom_level="BP19")
                    temp_collection = bpy.data.collections.get("TEMP_LINKED")
                    bpy.ops.object.select_all(action = 'DESELECT')
                    if len(temp_collection.objects) > 0:
                        for hqtile in temp_collection.objects:
                            hqtile = bpy.data.objects.get(hqtile.name)
                            if hqtile:
                                if hqtile.name[:12] == obj.name[:12]:
                                    print(f'Megvan a geci neve (hq): {hqtile.name}')
                                    hqtile.select_set(True)
                                    bpy.context.view_layer.objects.active = hqtile
                                    hqtile.name = obj.name[:12] + "_READYHQ"
                                    bpy.ops.object.modifier_add(type='NODES')
                                    geo_mod = hqtile.modifiers.get("GeometryNodes")
                                    if geo_mod:
                                        hqtile.modifiers["GeometryNodes"].node_group = bpy.data.node_groups["LAND_GENERATOR_WITH_DECIMATE"]
                                        hqtile.modifiers["GeometryNodes"].show_viewport = False
                                else:
                                    print(f'Nincs meg a geci neve (hq): {hqtile.name}')
                                    hqtile.select_set(False)
                                    return {'CANCELLED'}
                                
                    bpy.ops.object.select_all(action = 'DESELECT')
                    obj.hide_set(False)
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj
                    
                    bpy.ops.xtd_tools.append_hq_land()
                    
                    helper_collection = bpy.data.collections.get("HELPER")
                    bpy.ops.object.select_all(action = 'DESELECT')
                    if len(helper_collection.objects) > 0:
                        for helpertile in helper_collection.objects:
                            helpertile = bpy.data.objects.get(helpertile.name)
                            if helpertile.name[:12] == obj.name[:12]:
                                print(f'Megvan a geci neve (helper): {helpertile.name}')
                                helpertile.select_set(True)
                                bpy.context.view_layer.objects.active = helpertile
                                helpertile.name = helpertile.name[:12] + "_HELPER"
                                hqtileobj = bpy.data.objects.get(obj.name[:12] + "_READYHQ")
                                if hqtileobj:
                                    helpertile.select_set(False)
                                    hqtileobj.select_set(True)
                                    bpy.context.view_layer.objects.active = hqtileobj
                                    hqtileobj.modifiers["GeometryNodes"]["Socket_2"] = helpertile
                                    bpy.ops.object.modifier_apply(modifier="GeometryNodes")
                                    
                                    bpy.data.objects.remove(helpertile, do_unlink=True)
                                     
                                    hqtileobj.modifiers.new(name='Decimate' , type='DECIMATE')
                                    hqtileobj.modifiers["Decimate"].show_viewport = False
                                    hqtileobj.modifiers["Decimate"].ratio = 0.25
                                    hqtileobj.modifiers["Decimate"].use_collapse_triangulate = True
                                    hqtileobj.modifiers["Decimate"].use_symmetry = True
                                    hqtileobj.modifiers["Decimate"].symmetry_axis = 'Z'
                                    bpy.ops.object.modifier_apply(modifier="Decimate")
                                    
                                    
                                    ready_collection = bpy.data.collections.get("READYHQ")
                                    temp_collection.objects.unlink(hqtileobj)
                                    ready_collection.objects.link(hqtileobj)
                            else:
                                print(f'Nincs meg a geci neve (helper): {helpertile.name}')
                                return {'CANCELLED'}
                                
                    processed_count += 1
                    if processed_count % CACHE_CLEAR_INTERVAL == 0:
                        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
                        clear_reports()
                    bar()
                bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_all(action='DESELECT')
        ProcessManager.reset()
        return {'FINISHED'}
    
class XTD_OT_mergebyname_grid_empty_cage(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.mergebyname_grid_empty_cage"
    bl_label = "Merge by name _E Grid empty cage"
    bl_description = "Join models based on predefined Empty Cube grid"
    bl_options = {'REGISTER', 'UNDO'}
    def process_object(self, obj):
        batch_size = float(999)
        
        baseobject = bpy.data.objects.get(obj.name[:12])
        if baseobject:
            bpy.data.objects.remove(obj)
            baseobject.name= baseobject.name + "_E"

        return {'FINISHED'}

        
class XTD_OT_select_small_baseobjects(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.select_small_baseobjects"
    bl_label = "Select small base objects"

    def process_object(self, obj):
 
        obj = bpy.data.objects[obj.name]
        bpy.context.view_layer.objects.active = obj
        if obj.dimensions[0] > 412.3: 
            if obj.dimensions[1] > 305.5:
                obj.select_set(False)

        return {'FINISHED'}

# ----------- Triangles to quads -----------
class XTD_OT_tritoquad(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.tritoquad"
    bl_label = "Convert Triangles to quads"

    def process_object(self, obj):
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.mesh.tris_convert_to_quads()    
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        return {'FINISHED'}

# ----------- Quads to triangles -----------
class XTD_OT_quadtotri(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.quadtotri"
    bl_label = "Convert Quads to triangles"

    def process_object(self, obj):
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        bpy.ops.mesh.tris_convert_to_quads()    
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        return {'FINISHED'}

# ----------- Disolve sharps -----------
class XTD_OT_disolvesharpedges(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.disolvesharpedges"
    bl_label = "Disolve all sharp"

    def process_object(self, obj):
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.edges_select_sharp(sharpness=0.523599)
        bpy.ops.mesh.dissolve_edges(use_face_split=True)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        return {'FINISHED'}



# ----------- Nonmanifold Edgesplit -----------
class XTD_OT_nonmanifoldedgesplit(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.nonmanifoldedgesplit"
    bl_label = "Nonmanifold Edgesplit"

    def process_object(self, obj):
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.edge_split()
        bpy.ops.object.mode_set(mode = 'OBJECT')
        return {'FINISHED'}

# ----------- Nonmanifold Edgesplit -----------
class XTD_OT_merge_by_nameprefix(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.merge_by_nameprefix"
    bl_label = "Merge by name prefix"

    def execute(self, context):
        bl_label = self.bl_label
        keyboard.add_hotkey("esc", ProcessManager.stop)
        ProcessManager.start()
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Merge objects by name prefix...")
        #-STATUS-BAR--------------------------------------------------------------------------
        
        prefix_length= int(bpy.context.scene.xtd_tools_mergeprefix_length)
        purge_interval=40
        
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        selected_objs = list(bpy.context.selected_objects)
        if not selected_objs:
            print("Nincs kijelölt objektum!")
            return
        
        groups = {}
        for obj in selected_objs:
            key = obj.name[:prefix_length]
            groups.setdefault(key, []).append(obj)
        
        join_count = 0
        with alive_bar(len(groups.items()), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            for key, group in groups.items():
                if not ProcessManager.is_running():
                    self.report({'INFO'}, "Process stopped by user.")
                    return {'CANCELLED'}
                if len(group) < 2:
                    continue
                bpy.ops.object.select_all(action='DESELECT')
                for obj in group:
                    obj.select_set(True)
                bpy.context.view_layer.objects.active = group[0]
                bpy.ops.object.join()
                join_count += 1

                if join_count % purge_interval == 0:
                    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
                    clear_reports()
                bar()
        print("Join finished. Total groups joined:", join_count)
        ProcessManager.reset()
        return {'FINISHED'}

bpy.types.Scene.xtd_tools_mergeprefix_length = bpy.props.StringProperty(name="", description="Prefix Length", default="8")

# ----------- Nonmanifold Edgesplit -----------
class XTD_OT_lilycapturemerger(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.lilycapturemerger"
    bl_label = "Lily capture merger"
    
    def execute(self, context):
        processed_count = 0 
        CACHE_CLEAR_INTERVAL = 4
        REMOVE_DUPLICATES_THRESHOLD = 0.2
        bpy.context.scene.view_settings.view_transform = 'Standard'
        bpy.context.scene.render.image_settings.file_format = 'JPEG'
        bpy.context.scene.render.image_settings.color_management = 'OVERRIDE'
        bpy.context.scene.view_settings.view_transform = 'Standard'
        bpy.context.scene.render.compositor_device = 'GPU'

        bl_label = self.bl_label
        keyboard.add_hotkey("esc", ProcessManager.stop)
        ProcessManager.start()
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Merge material images by Lily Capture Packer...")
        #-STATUS-BAR--------------------------------------------------------------------------
        
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        selected_objs = list(bpy.context.selected_objects)
        if not selected_objs:
            print("Nincs kijelölt objektum!")
            return
        
        with alive_bar(len(selected_objs), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            bpy.ops.object.select_all(action = 'DESELECT')
            for obj in selected_objs:
                if not ProcessManager.is_running():
                    self.report({'INFO'}, "Process stopped by user.")
                    return {'CANCELLED'}
                if not obj.visible_get():
                    continue
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.mark_sharp(clear=True)
                bpy.ops.mesh.separate(type='MATERIAL')
                bpy.ops.object.mode_set(mode='OBJECT')
                active_obj = bpy.context.active_object
                if len(bpy.context.selected_objects) > 1:
                    bpy.ops.object.lily_texture_packer(spacing=0)
                    active_obj.select_set(True)
                    bpy.context.view_layer.objects.active = active_obj
                    bpy.ops.object.join()
                    
                    if obj and obj.type == 'MESH' and obj.active_material:
                        active_material = obj.active_material
                        obj.data.materials.clear() 
                        obj.data.materials.append(active_material)
                        active_material.name = "M_" + str(obj.name)
                        if active_material and active_material.node_tree:
                            active_material.node_tree.nodes["Principled BSDF"].inputs[13].default_value = 0

                            base_color = active_material.node_tree.nodes['Image Texture']
                            image = base_color.image
                            base_color.select = True
                            bpy.data.images[image.name].scale( 2048, 2048 )
                            image.name = "T_" + str(obj.name)
                            filepathimage = image.name + ".jpg"
                            texturepath = bpy.data.scenes["Scene"].render.filepath
                            filepath = os.path.join(texturepath, filepathimage)
                            bpy.data.images[image.name].save_render(filepath)
                            image.source = 'FILE'
                            image.filepath = filepath
                            image.file_format = 'JPEG'
                            image.reload()
                            
                objmode, bm = check_bmmode_on(self, active_obj, "NONE")
                bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=REMOVE_DUPLICATES_THRESHOLD)
                check_bmmode_off(self, active_obj, bm, objmode, True)

                processed_count += 1
                
                if processed_count % CACHE_CLEAR_INTERVAL == 0:
                    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
                    clear_reports()
                    #-STATUS-BAR--------------------------------------------------------------------------
                    global_settings.statusheader(bl_label,functiontext="Merge material images by Lily Capture Packer...")
                    #-STATUS-BAR--------------------------------------------------------------------------
                bar()
                
            bpy.ops.object.select_all(action='DESELECT')
        ProcessManager.reset()
        return {'FINISHED'}


        
# ----------- Purge Unused Materials -----------
class XTD_OT_purgeunusedmaterial(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.purgeunusedmaterial"
    bl_label = "Purge Unused Materials"

    def process_object(self, obj):
        batch_size = float(999)
        bpy.ops.object.material_slot_remove_unused()
        return {'FINISHED'}
        
# ----------- Purge Unused Materials -----------
class XTD_OT_remove_allmaterials(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.remove_allmaterials"
    bl_label = "Remove All Materials"

    def process_object(self, obj):
        batch_size = float(999)
        while len(bpy.context.active_object.material_slots) > 0:
            bpy.ops.object.material_slot_remove()
        return {'FINISHED'}

# ----------- Transform to convexhull -----------
class XTD_OT_makeconvexhullobject(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.makeconvexhullobject"
    bl_label = "Transform to convexhull"

    def process_object(self, obj):
        context = bpy.context
        removeallmaterials(context)
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.convex_hull()
        bpy.ops.object.mode_set(mode = 'OBJECT')
        decimate_modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')
        decimate_modifier.show_viewport = False
        decimate_modifier.decimate_type = 'DISSOLVE'
        decimate_modifier.angle_limit = 1.48353
        bpy.ops.object.modifier_apply(modifier="Decimate")
        return {'FINISHED'}

