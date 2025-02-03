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
            row.operator("xtd_tools.merge_by_distance", text="MERGE", icon="AREA_JOIN")
            
            row = box.row(align=True)
            row.separator()
            row.operator("xtd_tools.smart_grid_merge", text="SMART MERGE", icon="AREA_JOIN")
            
        layout = self.layout
        box = layout.box()
        for i in range(0,2,2):
            row = box.row(align=True)
            row.label(text="MESH TOOLS:", icon="MESH_DATA")
            row = box.row(align=True)
            row.operator("xtd_tools.selectboundaryloops", text="Select Boundry loops", icon='SNAP_EDGE')
        for i in range(0,2,2):
            row = box.row(align=True)
            row.operator("xtd_tools.tritoquad", text="Quad To Triangle", icon='MOD_TRIANGULATE')
            row.operator("xtd_tools.quadtotri", text="Triangle to Quad", icon='MOD_DECIM')
            
        for i in range(0,2,2):
            row = box.row(align=True)
            row.operator("xtd_tools.disolvesharpedges", text="Disolve all sharp edges", icon='SHARPCURVE')
            row.operator("xtd_tools.nonmanifoldedgesplit", text="Nonmanifold Edgesplit", icon='MOD_EDGESPLIT')
            
        layout = self.layout
        box = layout.box()
        for i in range(0,2,2):
            row = box.row(align=True)
            row.label(text="MATERIAL TOOLS:", icon="TEXTURE_DATA")
            row = box.row(align=True)
            row.operator("xtd_tools.purgeunusedmaterial", text="PURGE UNUSED", icon='MATERIAL_DATA')
            row.operator("xtd_tools.remove_allmaterials", text="REMOVE ALL", icon="TRASH")
        
        layout = self.layout
        box = layout.box()
        for i in range(0,2,2):
            row = box.row(align=True)
            row.label(text="OTHER:", icon="ORPHAN_DATA")
            row = box.row(align=True)
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
                    bpy.context.preferences.edit.use_global_undo = True
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
                    bpy.context.preferences.edit.use_global_undo = True
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
    bpy.context.preferences.edit.use_global_undo = False
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
    bpy.context.preferences.edit.use_global_undo = True
    
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
        keyboard.add_hotkey("esc", global_settings.ProcessManager.stop)
        global_settings.ProcessManager.start()
        if not global_settings.ProcessManager.is_running():
            self.report({'INFO'}, "Process stopped by user.")
            bpy.context.preferences.edit.use_global_undo = True
            return {'CANCELLED'}
        bpy.ops.object.select_all(action = 'DESELECT')

        blendfile_name = "BPEMPTY.blend"
        master_txt_path = bpy.context.scene.master_txt_filepath
        if not os.path.exists(master_txt_path):
            print("ERROR: Master.txt file not found!")
            return {'CANCELLED'}

        master_data = {}
        with open(master_txt_path, 'r') as file:
            for line in file:
                try:
                    name, blendfile, _ = line.strip().split(" | ")
                    master_data[name] = blendfile
                except ValueError:
                    continue
        
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Search Helper Grid blend file...")
        #-STATUS-BAR--------------------------------------------------------------------------
        
        blendfile_path = os.path.join(os.path.dirname(master_txt_path), blendfile_name)
        if not os.path.exists(blendfile_path):
            hex(f"ERROR: Blend file not found: {blendfile_path}", "#ff0000")
            return {'CANCELLED'}
        print(f"Blend file found: {blendfile_name} in {os.path.join(os.path.dirname(master_txt_path))}")
        
        
        with bpy.data.libraries.load(blendfile_path, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
            
        with alive_bar(len(data_to.objects), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            for obj in data_to.objects:
                bpy.context.scene.collection.objects.link(obj)
                bar()
                
                
        bpy.context.view_layer.update()
        
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Detect small size base grids...")
        #-STATUS-BAR--------------------------------------------------------------------------
        
        planes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and obj.name.endswith('_E')]

        bpy.ops.object.select_all(action='DESELECT')
        
        smallbaseobjects = []
        with alive_bar(len(planes), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            for plane in planes:
                if not global_settings.ProcessManager.is_running():
                    self.report({'INFO'}, "Process stopped by user.")
                    bpy.context.preferences.edit.use_global_undo = True
                    return {'CANCELLED'}
                baseobject = bpy.data.objects.get(plane.name[:12])
                plane=bpy.data.objects.get(plane.name)
                if not baseobject:
                    continue
                if baseobject:
                    # if baseobject.dimensions[0] < 412.3: 
                    if baseobject.dimensions[0] < 412.5: 
                        smallbaseobjects.append(baseobject)
                        continue
                        
                    # if baseobject.dimensions[1] < 305.5: 
                    if baseobject.dimensions[1] < 305.5:
                        smallbaseobjects.append(baseobject)
                        continue
                    baseobject.name = baseobject.name + "_A"
                bar() 
                
            bpy.ops.object.select_all(action='DESELECT')
        
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Copy plane origin to small base objects...")
        #-STATUS-BAR--------------------------------------------------------------------------
 
        bpy.ops.object.select_all(action='DESELECT')
        smallbaseobjects = [obj for obj in smallbaseobjects if obj.type == 'MESH']
        
        bpy.context.preferences.edit.use_global_undo = False
        with alive_bar(len(smallbaseobjects), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            for obj in smallbaseobjects:
                if not global_settings.ProcessManager.is_running():
                    self.report({'INFO'}, "Process stopped by user.")
                    bpy.context.preferences.edit.use_global_undo = True
                    return {'CANCELLED'}
                bpy.ops.object.select_all(action='DESELECT')
                plane = bpy.data.objects[obj.name[:12] + "_E"]
                baseobject = bpy.data.objects[obj.name]
                
                source_obj = plane
                source_obj.select_set(True)
                
                saved_location = bpy.data.scenes['Scene'].cursor.location.xyz
                bpy.data.scenes['Scene'].cursor.location = plane.location
                
                target_obj = baseobject
                target_obj.select_set(True)
                bpy.context.view_layer.objects.active = target_obj
                
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                
                bpy.data.scenes['Scene'].cursor.location.xyz = saved_location
                baseobject.name = baseobject.name + "_A"
                plane.select_set(True)
                bpy.context.view_layer.objects.active = plane
                bpy.data.objects.remove(plane)
                bar()
                
            bpy.ops.object.select_all(action='DESELECT')
        bpy.context.preferences.edit.use_global_undo = True
        
        bpy.context.view_layer.update()
        
        #-STATUS-BAR--------------------------------------------------------------------------
        global_settings.statusheader(bl_label,functiontext="Clean unused helper planes...")
        #-STATUS-BAR--------------------------------------------------------------------------
        
        bpy.ops.object.select_all(action='DESELECT')
        
        deleteotherplanes = [dobj for dobj in bpy.context.scene.objects if dobj.type == 'MESH' and dobj.name.endswith('_E')]
                
        bpy.context.preferences.edit.use_global_undo = False
        with alive_bar(len(deleteotherplanes), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            for dobj in deleteotherplanes:
                if not global_settings.ProcessManager.is_running():
                    self.report({'INFO'}, "Process stopped by user.")
                    bpy.context.preferences.edit.use_global_undo = True
                    return {'CANCELLED'}
                if dobj.name.endswith('_E'):
                    dobj.select_set(True)
                    bpy.context.view_layer.objects.active = dobj
                    bpy.data.objects.remove(dobj)
            
                bar()
                
            bpy.ops.object.select_all(action='DESELECT')
            
        bpy.context.view_layer.update()
        smallbaseobjectsfinal = [aobj for aobj in bpy.context.scene.objects if aobj.type == 'MESH' and aobj.name.endswith('_A')]
        bpy.context.preferences.edit.use_global_undo = False
        with alive_bar(len(smallbaseobjectsfinal), title='   ', enrich_print=True, enrich_offset=3, length=50, force_tty=True, max_cols=98, bar='filling') as bar:
            for aobj in smallbaseobjectsfinal:
                if not global_settings.ProcessManager.is_running():
                    self.report({'INFO'}, "Process stopped by user.")
                    bpy.context.preferences.edit.use_global_undo = True
                    return {'CANCELLED'}
                if aobj.name.endswith('_A'):
                    aobj.select_set(True)
                
                bpy.context.view_layer.objects.active = aobj
            
                bar()

        
        bpy.context.view_layer.update()

        self.report({'INFO'}, "Smart Grid Merge completed successfully!")
        ProcessManager.reset()
        bpy.context.preferences.edit.use_global_undo = True
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
            bpy.context.preferences.edit.use_global_undo = True
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

