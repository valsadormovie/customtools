#-------------------------------------------------
#-VERTEXGROUPTOOLS_PANEL.py
#-------------------------------------------------

from .global_settings import *
disable_cache()
# ================== PANEL =================
class XTD_PT_VertexGroupTools(bpy.types.Panel):
    bl_label = "VERTEX GROUP TOOLS"
    bl_idname = "XTD_PT_vertexgrouptools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return VisibilityController.check_visibility(context, panel_name = "vertexgrouptools_panel", require_selected=True)
        
    def draw(self, context):
        scene = bpy.context.scene
        layout = self.layout
        layout.label(text="BASE VERTEX GROUP TOOLS:", icon="HANDLE_VECTOR")
        row = layout.row()
        row.label(text="VERTEX GROUP NAME:")
        row.prop(scene, "vertexgroupname")
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        check_selected_active_button(row)
        row.operator("xtd_tools.create_vertex_groups", text="CREATE NEW VERTEX GROUP")
            
        for i in range(0,2,2):
            row = box.row(align=True)
            check_selected_active_button(row)
            row.operator("xtd_tools.addgeometrynodesvertexgroup", text="ASSING TO GEOMETRY NODES")
        for i in range(0,2,2):
            row = box.row(align=True)
            check_selected_active_button(row)
            row.operator("xtd_tools.addselected_vertex_groups", text="ADD SELECTED VERTICLES")
        for i in range(0,2,2):
            row = box.row(align=True)
            row.scale_x = 0.40
            check_selected_active_button(row)
            row.operator("xtd_tools.removevertexgroups", text="REMOVE All", icon="TRASH")
            row.scale_x = 0.60
            row.prop(scene, "remove_hiddenattributes", text="Hidden attributes too?")

        row.separator()
        layout = self.layout
        layout.label(text="VERTEX PROXIMITY:", icon="HANDLE_VECTOR")
        box = layout.box()
        row = box.row(align=True)
        grid = row.grid_flow(columns=2, align=True)
        grid.prop(scene, "xtd_tools_proximity_min_dist", slider=True, icon='AXIS_FRONT')
        grid.prop(scene, "xtd_tools_proximity_max_dist", slider=True, icon='AXIS_SIDE')
        row = box.row(align=True)
        row.prop(context.scene, "xtd_tools_proximity_invert_falloff", text="Invert Falloff")
        row = box.row(align=True)
        row.prop(context.scene, "xtd_tools_proximity_target_object", text="Target Object")
        row = box.row(align=True)
        row.operator("xtd_tools.add_vertex_weight_modifiers", text="CREATE PROXIMITY") 
            
# ================ PROPERTIES ================

bpy.types.Scene.vertexgroupname = bpy.props.StringProperty(
        name="",
        description="Vertex group name",
        default="Group"
    )
    
bpy.types.Scene.remove_hiddenattributes = bpy.props.BoolProperty(name="Remove hidden attributes?", description="", default=False)

# ================ OPERATORS ================
# ----------- APPLY ALL MODIFIERS -----------
class XTD_OT_CreateVertexGroups(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.create_vertex_groups"
    bl_label = "Vertex Group Létrehozása"
    bl_description = "Létrehoz egy vertex group-ot az aktív objektumokon"
    bl_options = {'REGISTER', 'UNDO'}
    
    def process_object(self, obj):
        vertexgroupname = bpy.context.scene.vertexgroupname
        vertexgroup=obj.vertex_groups.get(vertexgroupname) or obj.vertex_groups.new(name="Group")
        vertexgroup.name = vertexgroupname
        return {'FINISHED'}

class XTD_OT_AddSelectedVertexGroups(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.addselected_vertex_groups"
    bl_label = "Vertex Group Assign Selected"
    bl_description = "Létrehoz egy vertex group-ot az aktív objektumokon"
    bl_options = {'REGISTER', 'UNDO'}
    

    def process_object(self, obj):
        vertexgroupname = bpy.context.scene.vertexgroupname
        vertex_group = obj.vertex_groups.get(vertexgroupname)
        if vertex_group:
            obj.vertex_groups.remove(vertex_group)
        else:
            vertex_group = obj.vertex_groups.new(name="Group")
            vertex_group.name = vertexgroupname
        mesh = obj.data
        for v in mesh.vertices:
            if v.select:
                vertex_group.add([v.index], 1.0, 'ADD')
            else:
                vertex_group.add([v.index], 0.0, 'ADD')
        return {'FINISHED'}
        
class XTD_OT_addgeometrynodesvertexgroup(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.addgeometrynodesvertexgroup"
    bl_label = "Vertex Group hozzáadása Geometry nodeshoz. "
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        vertexgroupname = bpy.context.scene.vertexgroupname
        vg = obj.vertex_groups.get(vertexgroupname)
        if vg:
            for mod in obj.modifiers:
                if mod.type == 'NODES':
                    first_socket_name = list(mod.node_group.inputs.keys())[0]
                    if mod[first_socket_name + "_attribute_name"] != vertexgroupname:
                        bpy.ops.object.geometry_nodes_input_attribute_toggle(
                        input_name=first_socket_name,
                        modifier_name=mod.name
                    )
                    mod[first_socket_name + "_attribute_name"] = vertexgroupname
        return {'FINISHED'}

class OBJECT_OT_xtdtools_removevertexgroups(XTDToolsOperator):
    bl_idname = "xtd_tools.removevertexgroups"
    bl_label = "Remove Vertex Groups"

    def process_object(self, obj):
        
        
        if bpy.context.scene.remove_hiddenattributes:
            attributes_names = [attr.name for attr in obj.data.attributes if not attr.is_internal]
            for aname in attributes_names:
                attr = obj.data.attributes[aname]
                try:
                    obj.data.attributes.remove(attr)
                except Exception as error:
                    print("", error)

        obj.vertex_groups.clear()
        return {'FINISHED'}

class XTD_OT_AddVertexWeightModifiers(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.add_vertex_weight_modifiers"
    bl_label = "Add Vertex Weight Modifiers"
    bl_description = "Create Vertex Group and Add Weight Modifiers"
    bl_options = {'REGISTER', 'UNDO'}
    
    target_object: bpy.props.StringProperty(name="Target Object")
    min_dist: bpy.props.FloatProperty(name="Min Distance")
    max_dist: bpy.props.FloatProperty(name="Max Distance")
    invert_falloff: bpy.props.BoolProperty(name="Invert Falloff")
    
    def pre_process_object(self, context):
        bpy.ops.xtd_tools.create_vertex_groups()
    
    def process_object(self, obj):
        context = bpy.context
        vertexgroupname = bpy.context.scene.vertexgroupname
        
        vw_edit = next((mod for mod in obj.modifiers if mod.type == 'VERTEX_WEIGHT_EDIT'), None)
        if not vw_edit:
            vw_edit = obj.modifiers.new(name="VertexWeightEdit", type='VERTEX_WEIGHT_EDIT')

        vw_proximity = next((mod for mod in obj.modifiers if mod.type == 'VERTEX_WEIGHT_PROXIMITY'), None)
        if not vw_proximity:
            vw_proximity = obj.modifiers.new(name="VertexWeightProximity", type='VERTEX_WEIGHT_PROXIMITY')
        
        vw_edit.vertex_group = vertexgroupname
        vw_edit.default_weight = 1
        vw_edit.use_add = True
        vw_edit.add_threshold = 1
        vw_edit.show_in_editmode = True

        vw_proximity.vertex_group = vertexgroupname
        vw_proximity.proximity_mode = 'GEOMETRY'
        vw_proximity.proximity_geometry = {'FACE'}
        
        vw_proximity.min_dist = self.min_dist if self.min_dist else bpy.context.scene.xtd_tools_proximity_min_dist
        vw_proximity.max_dist = self.max_dist if self.max_dist else bpy.context.scene.xtd_tools_proximity_max_dist
        vw_proximity.invert_falloff = self.invert_falloff if self.invert_falloff else context.scene.xtd_tools_proximity_invert_falloff
        
        vw_proximity.normalize = True
        vw_proximity.falloff_type = 'STEP'
        vw_proximity.show_in_editmode = True
        
        target = None
        if self.target_object:
            target = bpy.data.objects.get(self.target_object)
        if not target:
            target = bpy.context.scene.xtd_tools_proximity_target_object
        
        if target:
            vw_proximity.target = target

        return {'FINISHED'}

bpy.types.Scene.xtd_tools_proximity_target_object = bpy.props.PointerProperty(
    name="Target Object",
    description="Target object for proximity modifier",
    type=bpy.types.Object
)

bpy.types.Scene.xtd_tools_proximity_min_dist = bpy.props.FloatProperty(
    name="Min Distance",
    description="Minimum distance for proximity",
    default=0.4,
    subtype='DISTANCE',
    min=0.0,
    max=50.0,
    step=0.001,
    precision=3
)

bpy.types.Scene.xtd_tools_proximity_max_dist = bpy.props.FloatProperty(
    name="Max Distance",
    description="Maximum distance for proximity",
    default=0.5,
    subtype='DISTANCE',
    min=0.0,
    max=50.0,
    step=0.001,
    precision=3
)

bpy.types.Scene.xtd_tools_proximity_invert_falloff = bpy.props.BoolProperty(
    name="Invert Falloff",
    description="Invert the falloff",
    default=True
)