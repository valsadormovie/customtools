#-------------------------------------------------
#-MODIFIERTOOLS_PANEL.py
#-------------------------------------------------

from .global_settings import *
disable_cache()
# ================== PANEL =================
class XTD_PT_ModifierTools(bpy.types.Panel):
    bl_label = "MODIFIER TOOLS"
    bl_idname = "XTD_PT_modifiertools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        
        return VisibilityController.check_visibility(context, panel_name = "modifiertools_panel", require_selected=True, require_prefix=False)
        
    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        box = layout.box()
        row = box.row(align=True)
        row.scale_x = 0.5
        for i in range(0, 2, 2):
            row = box.row(align=True)
            row.alignment = 'LEFT'
            row.scale_y = 0.5
            row.label(text="COPY ALL MODIFIERS WITH", icon="MOD_DATA_TRANSFER")
        for i in range(0, 2, 2):
            row = box.row(align=True)
            row.operator("xtd_tools.copy_modifiers_disabled_all", text="All Disabled", icon="PASTEFLIPDOWN")
            row.operator("xtd_tools.copy_modifiers_enabled_all", text="All Enabled", icon="PASTEFLIPUP")
            
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.scale_y = 0.5
        for i in range(0, 2, 2):
            row = box.row(align=True)
            row.alignment = 'LEFT'
            row.scale_y = 0.5
            row.label(text="APPLY ALL MODIFIERS", icon="MOD_ARRAY")
        for i in range(0, 2, 2):
            row = box.row(align=True)
            row.operator("xtd_tools.apply_all_modifiers_atonce", text="All at once", icon="GEOMETRY_SET")
            row.operator("xtd_tools.apply_all_modifiers_sequence", text="All at sequence", icon="THREE_DOTS")
        
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.scale_y = 0.5
        for i in range(0, 2, 2):
            row = box.row(align=True)
            row.alignment = 'LEFT'
            row.scale_y = 0.5
            row.label(text="SELECTED OBJECTS MODIFIERS", icon="MOD_INSTANCE")
        for i in range(0, 2, 2):
            row = box.row(align=True)
            row.operator("xtd_tools.enable_all_modifiers", text="Enable all", icon="CHECKMARK")
            row.operator("xtd_tools.disable_all_modifiers", text="Disable all", icon="X")
            row = box.row(align=True)
            row.operator("xtd_tools.remove_modifiers", text="Remove all", icon="TRASH")
            
        layout = self.layout
        row = layout.row()
        row.alignment = 'LEFT'
        row.prop(bpy.context.scene, "xtd_tools_unvisiblemodif", text="ADD UNVISIBLE MODIFIERS", emboss=False, icon_only=True, icon="TRIA_DOWN" if bpy.context.scene.xtd_tools_unvisiblemodif else "TRIA_RIGHT")
        if bpy.context.scene.xtd_tools_unvisiblemodif:
            box = layout.box()
            column_span = 2
            grid = box.grid_flow(columns=int(column_span), align=True)
            split = box.grid_flow(columns=1, align=True)
            grid.operator("xtd_tools.addremeshwithoutviewport", text="Remesh", icon='MOD_REMESH')
            grid.operator("xtd_tools.addweldwithoutviewport", text="Weld", icon='MOD_WARP')
            grid.operator("xtd_tools.addsubdividewithoutviewport", text="Subdivide", icon='MOD_SUBSURF')
            grid.operator("xtd_tools.addnormalswithoutviewport", text="WeightedNormal", icon='MOD_VERTEX_WEIGHT')
                

# =============== SCENES ====================
bpy.types.Scene.xtd_tools_unvisiblemodif = bpy.props.BoolProperty(name="ADD UNVISIBLE MODIFIERS", default=False)

# ================ OPERATORS ================

# ----------- Add remesh without viewport -----------
class XTD_OT_addremeshwithoutviewport(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.addremeshwithoutviewport"
    bl_label = "Add remesh without viewport"

    def process_object(self, obj):
        batch_size = float(999)
        remesh_modifier = obj.modifiers.new(name="Remesh", type='REMESH')
        remesh_modifier.show_viewport = False
        remesh_modifier.voxel_size = 10
        remesh_modifier.mode = 'VOXEL'
        return {'FINISHED'}
        
# ----------- Add remesh without viewport -----------
class XTD_OT_addsubdividewithoutviewport(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.addsubdividewithoutviewport"
    bl_label = "Add subdivide without viewport"

    def process_object(self, obj):
        batch_size = float(999)
        subdivide_modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        subdivide_modifier.show_viewport = False
        return {'FINISHED'}

# ----------- Add Weld without viewport -----------
class XTD_OT_addweldwithoutviewport(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.addweldwithoutviewport"
    bl_label = "Add Weld without viewport"

    def process_object(self, obj):
        batch_size = float(999)
        weld_modifier = obj.modifiers.new(name="Weld", type='WELD')
        weld_modifier.show_viewport = False
        weld_modifier.merge_threshold = 1.3
        return {'FINISHED'}

# ----------- Add and apply WeightedNormal -----------
class XTD_OT_addnormalswithoutviewport(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.addnormalswithoutviewport"
    bl_label = "Add and apply WeightedNormal"

    def process_object(self, obj):
        normal_modifier = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        normal_modifier.show_viewport = False
        normal_modifier.keep_sharp = True
        bpy.ops.object.modifier_apply(modifier="WeightedNormal")
        return {'FINISHED'}

# ----------- APPLY ALL MODIFIERS -----------
class XTD_OT_ApplyModifiersAllAtOnce(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.apply_all_modifiers_atonce"
    bl_label = "Apply All Modifiers at Once Per Batch"

    def pre_process_batch_objs(self, obj):
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        if int(bpy.context.scene.batch_mode) > 2:
            obj.hide_set(True)
        for mod in obj.modifiers:
            mod.show_viewport = True
        if int(bpy.context.scene.batch_mode) < 2:
            bpy.context.view_layer.update()
            bpy.ops.object.convert(target='MESH')
            return {'FINISHED'}
        return

    def process_object(self, obj):
        clear_reports()
        obj.hide_set(False)
        obj.select_set(True)
        # modifiers = [mod.name for mod in obj.modifiers]
        # if modifiers:
            # print(f"Obj: {obj.name} | Modifiers: {', '.join(modifiers)}")
        # else:
            # print(f"Obj: {obj.name} | No modifiers present.")
        return
    
    def post_process_batch_objs(self, context):
        bpy.context.view_layer.update()
        bpy.ops.object.convert(target='MESH')
        return {'FINISHED'}
        
# ----------- APPLY ALL MODIFIERS -----------
class XTD_OT_ApplyModifiersAllAtSequence(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.apply_all_modifiers_sequence"
    bl_label = "Apply All Modifiers at Sequence"
    
    def pre_process_object(self, context):
        batch_size = 1

    def process_object(self, obj):
        bpy.context.view_layer.objects.active = obj
        modifiers = [mod.name for mod in obj.modifiers]
        workmod = len(modifiers)
        reported_percentages = set()
        start = 0
        
        if modifiers:
            print(f"Obj: {obj.name} | Modifiers: {', '.join(modifiers)}")
        else:
            print(f"Obj: {obj.name} | No modifiers present.")
        for start, mod in enumerate(obj.modifiers, start=1):
            percent = int((start / workmod) * 100)
            if percent % 10 == 0 and percent not in reported_percentages:
                sys.stdout.write(f"\r{percent}% completed | Now working: {mod.name}")  # Sor elejére ugrik és felülírja
                sys.stdout.flush()
                reported_percentages.add(percent)
            bpy.ops.object.modifier_apply(modifier=mod.name)
        return {'FINISHED'}

# ----------- COPY MODIFIERS WITH DISABLED -----------
class XTD_OT_CopyModifiersDisabled(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.copy_modifiers_disabled_all"
    bl_label = "Copy Modifiers (Disabled All)"

    def pre_process_object(self, context):
        batch_size = 999
    
    def execute(self, context):
        active_obj = bpy.context.active_object
        if not active_obj:
            print("Nincs aktív objektum!")
            return {'CANCELLED'}
        
        selected_objs = [obj for obj in bpy.context.selected_objects if obj != active_obj]
        if not selected_objs:
            print("Nincs más kijelölt objektum!")
            return {'CANCELLED'}
            
        for obj in selected_objs:
            for mod in active_obj.modifiers:
                new_mod = obj.modifiers.new(name=mod.name, type=mod.type)
                new_mod.show_viewport = False

                for attr in dir(mod):
                    if not attr.startswith("_") and hasattr(new_mod, attr):
                        try:
                            setattr(new_mod, attr, getattr(mod, attr))
                        except AttributeError:
                            pass 

                for new_mod in obj.modifiers:
                    new_mod.show_viewport = False

        print(f"A modifierek sikeresen átmásolva {len(selected_objs)} objektumra.")
        return {'FINISHED'}

# ----------- COPY MODIFIERS WITH ENABLED -----------
class XTD_OT_CopyModifiersEnabled(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.copy_modifiers_enabled_all"
    bl_label = "Copy Modifiers (Enabled All)"

    def pre_process_object(self, context):
        batch_size = 999
    
    def execute(self, context):
        active_obj = bpy.context.active_object
        if not active_obj:
            print("Nincs aktív objektum!")
            return {'CANCELLED'}
        
        selected_objs = [obj for obj in bpy.context.selected_objects if obj != active_obj]
        
        if not selected_objs:
            print("Nincs más kijelölt objektum!")
            return {'CANCELLED'}
        
        for obj in selected_objs:
            for mod in active_obj.modifiers:
                new_mod = obj.modifiers.new(name=mod.name, type=mod.type)
                new_mod.show_viewport = True

                for attr in dir(mod):
                    if not attr.startswith("_") and hasattr(new_mod, attr):
                        try:
                            setattr(new_mod, attr, getattr(mod, attr))
                        except AttributeError:
                            pass 

            for new_mod in obj.modifiers:
                new_mod.show_viewport = True

        print(f"A modifierek sikeresen átmásolva {len(selected_objs)} objektumra.")
        return {'FINISHED'}

# ----------- ENABLE / DISABLE EXITING MODIFIERS -----------
class XTD_OT_EnableAllModifiers(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.enable_all_modifiers"
    bl_label = "Enable All Modifiers"

    def execute(self, context):
        selected_objs = [obj for obj in bpy.context.selected_objects]
        if not selected_objs:
            print("Nincs más kijelölt objektum!")
            return {'CANCELLED'}
        for obj in selected_objs:
            for mod in obj.modifiers:
                mod.show_viewport = True
        return {'FINISHED'}

class XTD_OT_DisableAllModifiers(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.disable_all_modifiers"
    bl_label = "Disable All Modifiers"

    def execute(self, context):
        selected_objs = [obj for obj in bpy.context.selected_objects]
        if not selected_objs:
            print("Nincs más kijelölt objektum!")
            return {'CANCELLED'}
        for obj in selected_objs:
            for mod in obj.modifiers:
                mod.show_viewport = False
        return {'FINISHED'}

# ----------- REMOVE MODIFIERS -----------
class XTD_OT_RemoveAllModifiers(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.remove_modifiers"
    bl_label = "Remove All Modifiers"

    def execute(self, context):
        selected_objs = [obj for obj in bpy.context.selected_objects]
        if not selected_objs:
            print("Nincs más kijelölt objektum!")
            return {'CANCELLED'}
        for obj in selected_objs:
            obj.modifiers.clear()
        return {'FINISHED'}

