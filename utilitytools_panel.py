#-------------------------------------------------
#-UTILITYTOOLS_PANEL.py
#-------------------------------------------------

from .global_settings import *

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
            row.label(text="MESH TOOLS:", icon="MESH_DATA")
            row = box.row(align=True)
            check_selected_active_button(row)
            row.operator("xtd_tools.selectboundaryloops", text="Select Boundry loops", icon='SNAP_EDGE')
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
        for i in range(0,2,2):
            row = box.row(align=True)
            row.label(text="MATERIAL TOOLS:", icon="TEXTURE_DATA")
            row = box.row(align=True)
            check_selected_active_button(row)
            row.operator("xtd_tools.lilycapturemerger", text="MERGE MATERIAL TEXTURES", icon='IMAGE_RGB')
            row = box.row(align=True)
            row.operator("xtd_tools.merge_by_nameprefix", text="MERGE BY NAME PREFIX", icon='IMAGE_RGB')
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
                if not global_settings.ProcessManager.is_running():
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
                
                if len(objects_to_join) > 1:
                    bpy.context.view_layer.objects.active = base_obj
                    
                    for obj in objects_to_join:
                        try:
                            obj.select_set(True)
                        except:
                            self.report({'ERROR'}, f"Merge failed: {e}")
                            return {'CANCELLED'}
                    try:
                        bpy.ops.object.join()
                    except:
                        return {'CANCELLED'}
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
        scene_objects = {obj.name[:12] for obj in bpy.context.scene.objects}
        matched_objects = set()

        with bpy.data.libraries.load(external_blend_path, link=True) as (data_from, data_to):
            external_objects = {obj[:12]: obj for obj in data_from.objects}
            matched_objects = {external_objects[key] for key in scene_objects if key in external_objects}
            data_to.objects = list(matched_objects)

        for obj in data_to.objects:
            if obj is not None:
                temp_collection.objects.link(obj)
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Copy plane origin to small base objects...")
        #-STATUS-BAR--------------------------------------------------------------------------
        
        temp_collection_objects = [o for o in temp_collection.objects]

        saved_location = bpy.data.scenes['Scene'].cursor.location.xyz
        
        with alive_bar(len(temp_collection_objects), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            for obj in temp_collection_objects:
                bpy.context.view_layer.objects.active = obj
                baseobject = bpy.data.objects.get(obj.name[:12])
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
                obj.select_set(True)
                bar()
        
        bpy.ops.xtd_tools.merge_by_distance()
        
        for obj in bpy.data.objects:
            UUIDManager.ensure_project_uuid()
        
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        self.report({'INFO'}, "Smart Grid Merge completed successfully!")
        PopupController(title="UUID GENERATOR", message=f"{len(bpy.data.objects)} objektuma frissítve lett az új nevekkel!", buttons=[("Mentés", "wm.save_mainfile", "CHECKMARK"), ("Nem", "", "CHECKMARK")])
        return {'FINISHED'}

    
class XTD_OT_mergebyname_grid_empty_cage(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.mergebyname_grid_empty_cage"
    bl_label = "Merge by name _E Grid empty cage"

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
        
class XTD_OT_xtdtools_selectboundaryloops(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.selectboundaryloops"
    bl_label = "Selected only boundary loops in objects"

    def process_object(self, obj):

        if not global_settings.ProcessManager.is_running():
            self.report({'INFO'}, "Process stopped by user.")
            
            return {'CANCELLED'}
        global_deselect(context, all_objects=False)
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        obj = bpy.data.objects[obj.name]
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.edges.ensure_lookup_table()
        bm.verts.ensure_lookup_table()
        for vert in bm.verts:
            vert.select = False
        for edge in bm.edges:
            if edge.is_boundary:
                edge.select = True
        bm.to_mesh(obj.data)
        bm.free()
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
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Merge objects by name prefix...")
        #-STATUS-BAR--------------------------------------------------------------------------
        
        prefix_length=10, 
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
                if len(group) < 2:
                    continue
                bpy.ops.object.select_all(action='DESELECT')
                for obj in group:
                    obj.select_set(True)
                bpy.context.view_layer.objects.active = group[0]
                bpy.ops.object.join()
                join_count += 1
                print(f"Join group {key} -> join count: {join_count}")
                
                if join_count % purge_interval == 0:
                    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
                    print(f"Purge executed after {join_count} join operations.")
                bar()
        print("Join finished. Total groups joined:", join_count)

        return {'FINISHED'}
        
# ----------- Nonmanifold Edgesplit -----------
class XTD_OT_lilycapturemerger(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.lilycapturemerger"
    bl_label = "Lily capture merger"
    
    def execute(self, context):
        processed_count = 0 
        CACHE_CLEAR_INTERVAL = 4
        REMOVE_DUPLICATES_THRESHOLD = 0.5
        
        bl_label = self.bl_label
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
            for obj in selected_objs:
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
                            bpy.data.images[image.name].scale( 1024, 1024 )
                            image.name = "T_" + str(obj.name)
                            filepathimage = image.name + ".jpg"
                            texturepath = os.path.dirname("G:/PORTAL_BP_PROJECT_RENDSZEREZETT/GLTF/BP17BAKED/")
                            filepath = os.path.join(texturepath, filepathimage)
                            bpy.data.images[image.name].save_render(filepath)
                mesh = active_obj.data
                bm = bmesh.new()
                bm.from_mesh(mesh)
                bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=REMOVE_DUPLICATES_THRESHOLD)
                bm.to_mesh(mesh)
                bm.free()
                mesh.update()

                processed_count += 1
                
                if processed_count % CACHE_CLEAR_INTERVAL == 0:
                    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
                    #-STATUS-BAR--------------------------------------------------------------------------
                    global_settings.statusheader(bl_label,functiontext="Merge material images by Lily Capture Packer...")
                    #-STATUS-BAR--------------------------------------------------------------------------
                bar()
                
            bpy.ops.object.select_all(action='DESELECT')
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

