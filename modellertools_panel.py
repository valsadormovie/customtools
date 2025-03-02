#-------------------------------------------------
#-MODELLERTOOLS_PANEL.py
#-------------------------------------------------
from .global_settings import *
disable_cache()
# ================== PANEL =================
class XTD_PT_ModellerTools(bpy.types.Panel):
    bl_label = "MODELLER TOOLS"
    bl_idname = "XTD_PT_modeller_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"

    @classmethod
    def poll(cls, context):
        return VisibilityController.check_visibility(context, panel_name = "modellertools_panel", require_selected=True, require_prefix=True)
        
    def draw(self, context):
        scene = bpy.context.scene
        layout = self.layout
        layout.label(text="EVALUATED MODE:")
        row = layout.row()
        box = layout.box()
        row = box.row(align=True)
        row.operator("xtd_tools.get_evaluated_mesh", text="GET EVAULATED MESH", icon='MESH_DATA')
        row.operator("xtd_tools.quad_jremesh_model", text="QUAD JREMESH", icon='MESH_DATA')
        row = box.row(align=True)
        row.separator()
        
        layout = self.layout
        layout.label(text="PRE SELECT ALL MODE:")
        row = layout.row()
        box = layout.box()
        row = box.row(align=True)
        row.prop(scene, "xtd_tools_modeller_select_all_mode", expand=True)
        
        row = box.row(align=True)
        row.separator()
        row.label(text="SELECT BY:")
        row = box.row(align=True)
        check_selected_active_button(row)
        row.operator("xtd_tools.select_loose_faces", text="LOOSE FACES", icon="OBJECT_DATAMODE")
        row.separator()
        row = box.row(align=True)
        check_selected_active_button(row)
        row.operator("xtd_tools.selectboundaryloops", text="BOUNDARY LOOPS", icon='SNAP_EDGE')
        row.label(text="", icon='EXPORT')
        row = box.row(align=True)
        row.scale_x = 0.50
        row.alignment = 'EXPAND'
        row.use_property_decorate = False
        split = row.split(factor=0.05)
        row.label(text="ONLY EDGE", icon='MOD_EDGESPLIT')
        row.prop(scene, "xtd_tools_only_edge", expand=True)
        row = box.row(align=True)
        grid = row.grid_flow(columns=2, align=True)
        grid.prop(scene, "xtd_tools_exclude_adjacent", text="Exclude Adjacents", expand=True)
        grid.prop(scene, "xtd_tools_exclude_adjacent_nearest", text="Exclude nearest adjacents", expand=True)
        row = box.row(align=True)
        row.prop(scene, "xtd_tools_exclude_adjacent_threshold", slider=True, icon='AXIS_SIDE')
        
        row = box.row(align=True)
        row.separator()
        layout = self.layout
        layout.label(text="TRIM OBJECT BY BOUNDING BOX:", icon="HANDLE_VECTOR")
        box = layout.box()
        row = box.row(align=True)
        grid = row.grid_flow(columns=2, align=True)
        grid.prop(scene, "xtd_tools_trim_x", slider=True, icon='AXIS_FRONT')
        grid.prop(scene, "xtd_tools_trim_y", slider=True, icon='AXIS_SIDE')
        row = box.row(align=True)
        row.operator("xtd_tools.trim_object_by_xy", text="TRIM", icon='MESH_CONE')
        row = box.row(align=True)
        row.operator("xtd_tools.separate_quad_by_xy", text="SEPARATE QUAD BY XY", icon='MOD_BOOLEAN')
        row = box.row(align=True)
        row.operator("xtd_tools.print_faces_vector_data", text="PRINT FACE VECTOR DATA", icon='FACESEL')
                  

# ================ OPERATORS ================

# ================== Select Boundary Loops ================== 
class XTD_OT_SelectLooseFaces(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.select_loose_faces"
    bl_label = "Operator label"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        select_mode = bpy.context.scene.xtd_tools_modeller_select_all_mode
        objmode, bm = check_bmmode_on(self, obj, select_mode)
        for face in bm.faces:
            is_loose = all(len(edge.link_faces) == 1 for edge in face.edges)
            if select_mode == "ALL":
                face.select = not is_loose
            elif select_mode == "DESELECT":
                face.select = is_loose
            elif select_mode == "NONE":
                if is_loose:
                    face.select = True
        check_bmmode_off(self, obj, bm, objmode, False)
        return {'FINISHED'}

class XTD_OT_xtdtools_selectboundaryloops(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.selectboundaryloops"
    bl_label = "Selected only boundary loops in objects"
    
    def process_object(self, obj):
        select_mode = bpy.context.scene.xtd_tools_modeller_select_all_mode
        only_edge = bpy.context.scene.xtd_tools_only_edge
        exclude_adjacent = bpy.context.scene.xtd_tools_exclude_adjacent
        merge_threshold = bpy.context.scene.xtd_tools_exclude_adjacent_threshold 
        
        objmode, bm = check_bmmode_on(self, obj, select_mode)
        
        for edge in bm.edges:
            for vert in edge.verts:
                if select_mode == "ALL":
                    if only_edge:
                        if vert.is_boundary:
                            vert.select = False
                    if edge.is_boundary:
                        edge.select = False
                elif select_mode == "DESELECT":
                    if only_edge:
                        if vert.is_boundary:
                            vert.select = True
                    if edge.is_boundary:
                        edge.select = True
                elif select_mode == "NONE":
                    if only_edge:
                        if vert.is_boundary:
                            vert.select = True
                    if edge.is_boundary:
                        edge.select = True
        
        if exclude_adjacent:
            if select_mode == "DESELECT":
                for vert in bm.verts:
                    if vert.select:
                        boundary_edge_count = sum(1 for edge in vert.link_edges if edge.is_boundary)
                        if boundary_edge_count > 2:
                            vert.select = False
                
                selected_boundary_edges = {edge for edge in bm.edges if edge.is_boundary and edge.select}
                
                for vert in bm.verts:
                    if not any(edge.is_boundary for edge in vert.link_edges):
                        continue
                    if not vert.select:
                        continue
                    for edge in vert.link_edges:
                        if edge.select:
                            if edge not in selected_boundary_edges:
                                edge.select = False
                
                if bpy.context.scene.xtd_tools_exclude_adjacent_nearest:
                    
                    
                    selected_boundary_verts = {vert for vert in bm.verts if vert.select}
                    selected_verts_count = len(selected_boundary_verts)
                    kdtree = KDTree(selected_verts_count)
                    print(f"Selected {selected_verts_count} verticles search nearst. Please wait")
                    for vert in selected_boundary_verts:
                        kdtree.insert(vert.co, vert.index)
                    kdtree.balance()
                    
                    near_verts = set()
    
                    for vert in selected_boundary_verts:
                        nearby = kdtree.find_range(vert.co, merge_threshold)
                        nearby = [item for item in nearby if item[1] != vert.index]
                        if len(nearby) > 1:
                            near_verts.add(vert)
                    
                    for vert in near_verts:
                        vert.select = False

        check_bmmode_off(self, obj, bm, objmode, False)
        return {'FINISHED'}


bpy.types.Scene.xtd_tools_exclude_adjacent_threshold = bpy.props.FloatProperty(
        name="THRESHOLD",
        default=0.1,
        subtype = "DISTANCE",
        min=0.0,
        max=800.0,
        step=0.001,
        precision=1
    )

bpy.types.Scene.xtd_tools_exclude_adjacent_nearest = bpy.props.BoolProperty(
        name="Exclude Adjacent nearest",
        description="Exclude boundary vertices that are connected to non-boundary vertices",
        default=False
    )

bpy.types.Scene.xtd_tools_exclude_adjacent = bpy.props.BoolProperty(
        name="Exclude Adjacent",
        description="Exclude boundary vertices that are connected to non-boundary vertices",
        default=False
    )

bpy.types.Scene.xtd_tools_exclude_adjacent_threshold = bpy.props.FloatProperty(
        name="THRESHOLD",
        default=0.1,
        subtype = "DISTANCE",
        min=0.0,
        max=800.0,
        step=0.001,
        precision=1
    )

bpy.types.Scene.xtd_tools_modeller_select_all_mode = bpy.props.EnumProperty(
    items=[
        ('NONE', "NONE", ""),
        ('ALL', "ALL", ""),
        ('DESELECT', "DESELECT", ""),
    ],
    name="SELECT ALL MODE",
    default="NONE"
)

bpy.types.Scene.xtd_tools_only_edge = bpy.props.EnumProperty(
    items=[
        ('ON', "ON", ""),
        ('OFF', "OFF", ""),
    ],
    name="SELECT ONLY EDGES",
    default="OFF"
)

# ================== Old Select Boundary Loops ================== 

# class XTD_OT_xtdtools_selectboundaryloops(global_settings.XTDToolsOperator):
    # bl_idname = "xtd_tools.selectboundaryloops"
    # bl_label = "Selected only boundary loops in objects"
    
    # def process_object(self, obj):
        # select_mode = bpy.context.scene.xtd_tools_modeller_select_all_mode
        # only_edge = bpy.context.scene.xtd_tools_only_edge
        # objmode, bm = check_bmmode_on(self, obj, select_mode)
        
        # for edge in bm.edges:
            # for vert in edge.verts:
                # if select_mode == "ALL":
                    # if only_edge:
                        # if vert.is_boundary:
                            # vert.select = False
                    # if edge.is_boundary:
                        # edge.select = False
                # elif select_mode == "DESELECT":
                    # if only_edge:
                        # if vert.is_boundary:
                            # vert.select = True
                    # if edge.is_boundary:
                        # edge.select = True
                # elif select_mode == "NONE":
                    # if only_edge:
                        # if vert.is_boundary:
                            # vert.select = True
                    # if edge.is_boundary:
                        # edge.select = True
                    
        # check_bmmode_off(self, obj, bm, objmode, False)
        # return {'FINISHED'}

# ================== Trim by XY dimensions ================== 
class XTD_OT_trim_object_by_XY(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.trim_object_by_xy"
    bl_label = "Trim by XY dimensions"
    bl_description = "Trim models beyond the specified XY dimensions"
    bl_options = {'REGISTER', 'UNDO'}

    processed_count = 0
    CACHE_CLEAR_INTERVAL = 8

    def process_object(self, obj):
        scene = bpy.context.scene
        X_CUT = float(scene.xtd_tools_trim_x)
        Y_CUT = float(scene.xtd_tools_trim_y)
        objmode, bm = check_bmmode_on(self, obj, "NONE")
        mat = obj.matrix_world

        min_x = float('inf')
        max_x = -float('inf')
        min_y = float('inf')
        max_y = -float('inf')
        
        for v in bm.verts:
            co = mat @ v.co
            min_x = min(min_x, co.x)
            max_x = max(max_x, co.x)
            min_y = min(min_y, co.y)
            max_y = max(max_y, co.y)

        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0
        center_global = Vector((center_x, center_y, 0))

        trim_min_x = center_x - (X_CUT / 2.0)
        trim_max_x = center_x + (X_CUT / 2.0)
        trim_min_y = center_y - (Y_CUT / 2.0)
        trim_max_y = center_y + (Y_CUT / 2.0)

        if min_x >= trim_max_x or max_x <= trim_min_x or min_y >= trim_max_y or max_y <= trim_min_y:
            print(f"Skipping {obj.name} - does not exceed given trim bounds.")
            check_bmmode_off(self, obj, bm, objmode, destructive=True)
            return

        geom = bm.faces[:] + bm.edges[:] + bm.verts[:]
        res_left = bmesh.ops.bisect_plane(
            bm, geom=geom, dist=0.001,
            plane_co=Vector((trim_min_x, center_y, 0)),
            plane_no=Vector((-1, 0, 0))
        )
        res_right = bmesh.ops.bisect_plane(
            bm, geom=geom, dist=0.001,
            plane_co=Vector((trim_max_x, center_y, 0)),
            plane_no=Vector((1, 0, 0))
        )

        geom = bm.faces[:] + bm.edges[:] + bm.verts[:]
        res_bottom = bmesh.ops.bisect_plane(
            bm, geom=geom, dist=0.001,
            plane_co=Vector((center_x, trim_min_y, 0)),
            plane_no=Vector((0, -1, 0))
        )
        res_top = bmesh.ops.bisect_plane(
            bm, geom=geom, dist=0.001,
            plane_co=Vector((center_x, trim_max_y, 0)),
            plane_no=Vector((0, 1, 0))
        )

        if not any([res_left.get("geom"), res_right.get("geom"), res_bottom.get("geom"), res_top.get("geom")]):
            print(f"No valid cuts made on {obj.name}, skipping deletion.")
            check_bmmode_off(self, obj, bm, objmode, destructive=True)
            return

        for face in bm.faces[:]:
            face_center = mat @ face.calc_center_median()
            if not (trim_min_x <= face_center.x <= trim_max_x and trim_min_y <= face_center.y <= trim_max_y):
                face.select = True

        faces_to_delete = [f for f in bm.faces if f.select]
        if faces_to_delete:
            bmesh.ops.delete(bm, geom=faces_to_delete, context='FACES')

        check_bmmode_off(self, obj, bm, objmode, destructive=True)

        self.processed_count += 1
        if self.processed_count % self.CACHE_CLEAR_INTERVAL == 0:
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
            clear_reports()

    def post_process_object(self, obj):
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        clear_reports()

bpy.types.Scene.xtd_tools_trim_x = bpy.props.FloatProperty(
        name="X",
        default=413,
        subtype = "DISTANCE",
        min=0.0,
        max=800.0,
        step=0.001,
        precision=1
    )

bpy.types.Scene.xtd_tools_trim_y = bpy.props.FloatProperty(
        name="Y",
        default=307,
        subtype = "DISTANCE",
        min=0.0,
        max=800.0,
        step=0.001,
        precision=1
    )

# ================== Separate Quad by XY ================== 
class XTD_OT_separate_quad_by_XY(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.separate_quad_by_xy"
    bl_label = "Separate Quad by XY coordinates"
    bl_description = "Join models based on predefined Empty Cube grid"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        
        bl_label = self.bl_label
        processed_count = 0 
        CACHE_CLEAR_INTERVAL = 4
        REMOVE_DUPLICATES_THRESHOLD = 0.2
        
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
                if not obj.visible_get():
                    continue
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                if not ProcessManager.is_running():
                    self.report({'INFO'}, "Process stopped by user.")
                    return {'CANCELLED'}

                objmode, bm = check_bmmode_on(self, obj, "NONE")

                mat = obj.matrix_world
                min_x = float('inf')
                max_x = -float('inf')
                min_y = float('inf')
                max_y = -float('inf')

                for v in bm.verts:
                    co = mat @ v.co
                    min_x = min(min_x, co.x)
                    max_x = max(max_x, co.x)
                    min_y = min(min_y, co.y)
                    max_y = max(max_y, co.y)

                center_global = Vector(((min_x + max_x) / 2, (min_y + max_y) / 2, 0))

                plane_co_x = Vector((center_global.x, 0, 0))
                plane_no_x = Vector((1, 0, 0))
                geom = bm.faces[:] + bm.edges[:] + bm.verts[:]
                bmesh.ops.bisect_plane(bm, geom=geom, dist=0.001, plane_co=plane_co_x, plane_no=plane_no_x)

                plane_co_y = Vector((0, center_global.y, 0))
                plane_no_y = Vector((0, 1, 0))
                geom = bm.faces[:] + bm.edges[:] + bm.verts[:]
                bmesh.ops.bisect_plane(bm, geom=geom, dist=0.001, plane_co=plane_co_y, plane_no=plane_no_y)

                check_bmmode_off(self, obj, bm, objmode, destructive=True)

                def separate_quadrant(original_obj, quadrant):
                    if not ProcessManager.is_running():
                        self.report({'INFO'}, "Process stopped by user.")
                        return {'CANCELLED'}
                    bpy.ops.object.select_all(action='DESELECT')
                    original_obj.select_set(True)
                    bpy.context.view_layer.objects.active = original_obj
                    bpy.ops.object.duplicate()
                    new_obj = bpy.context.active_object
                    
                    objmode, bm = check_bmmode_on(self, new_obj, "DESELECT")
                    
                    for face in bm.faces:
                        center_local = face.calc_center_median()
                        center_world = new_obj.matrix_world @ center_local
                        
                        if quadrant[0] == 1:
                            cond_x = center_world.x >= center_global.x
                        else:
                            cond_x = center_world.x < center_global.x
                        
                        if quadrant[1] == 1:
                            cond_y = center_world.y >= center_global.y
                        else:
                            cond_y = center_world.y < center_global.y
                        
                        if not (cond_x and cond_y):
                            face.select = True
                    
                    selected_faces = {face for face in bm.faces if face.select}
                    selected_faces= list(set(selected_faces))
                    bmesh.ops.delete(bm, geom=selected_faces, context='FACES')
                    check_bmmode_off(self, new_obj, bm, objmode, True)
                    
                    return new_obj

                quad1 = separate_quadrant(obj, (-1, -1))
                quad2 = separate_quadrant(obj, (1, -1))
                quad3 = separate_quadrant(obj, (-1, 1))
                quad4 = separate_quadrant(obj, (1, 1))

                bpy.data.objects.remove(obj, do_unlink=True)

                new_objs = [quad1, quad2, quad3, quad4]

                for o in new_objs:
                    bpy.ops.object.select_all(action='DESELECT')
                    o.select_set(True)
                    bpy.context.view_layer.objects.active = o
                    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
                
                processed_count += 1
                
                if processed_count % CACHE_CLEAR_INTERVAL == 0:
                    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
                    clear_reports()
                bar()
                
        bpy.ops.object.select_all(action='DESELECT')
        ProcessManager.reset()
        return {'FINISHED'}

# ================== Print faces ================== 
class XTD_OT_print_faces_vector_data(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.print_faces_vector_data"
    bl_label = "Purge Unused Materials"

    def process_object(self, obj):
        objmode, bm = check_bmmode_on(self, obj, "NONE")
        
        if len(bm.faces) < 200:
            print(f"Face normals for object '{obj.name}':")
            for i, face in enumerate(bm.faces):
                print(f"Face {i}: {face.normal}")
        else:
            print(f"Nagyon sok face-e van ({len(bm.faces)} db!!!). Meg vagy hülyülve?")
        
        check_bmmode_off(self, obj, bm, objmode, None)
        return {'FINISHED'}
        
# ================== Print faces ================== 
class XTD_OT_quad_jremesh_model(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.quad_jremesh_model"
    bl_label = "Jremesh model"

    def process_object(self, obj):
        obj = bpy.data.objects[obj.name]
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        objname= obj.name
        bpy.ops.object.jrt_remesh_op()
        remeshobj = bpy.data.objects.get(obj.name + "_rm")
        
        remeshobj.select_set(True)
        bpy.context.view_layer.objects.active = remeshobj
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        bpy.context.object.modifiers["Shrinkwrap"].target = obj
        bpy.ops.object.modifier_apply(modifier="Shrinkwrap")
        bpy.data.objects.remove(obj, do_unlink=True)
        
        remeshobj.name = objname
        return {'FINISHED'}
        

        
# ================== Print faces ================== 
class XTD_OT_get_evaluated_mesh(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.get_evaluated_mesh"
    bl_label = "Get evaluated mesh"
    
    suffix: bpy.props.StringProperty(
        name="Suffix",
        description="Suffix",
        default="_MESH"
    )
    
    def execute(self, context):
        obj = bpy.context.active_object
        location = obj.location
        rotation = obj.rotation_euler

        obj = bpy.data.objects.get(obj.name)
        if obj:
            if len(obj.modifiers) < 1:
                return {'CANCELLED'}
            new_mesh = self.get_evaluated_mesh(obj)
            
            new_obj = bpy.data.objects.new(obj.name + self.suffix, new_mesh)
            bpy.context.collection.objects.link(new_obj)
        new_obj.location = location
        new_obj.rotation_euler = rotation
        new_obj.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.context.view_layer.update()
        
        return {'FINISHED'}
        
    def get_evaluated_mesh(self, obj):
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        new_mesh = bpy.data.meshes.new_from_object(
            eval_obj, preserve_all_data_layers=True, depsgraph=depsgraph)
        return new_mesh
