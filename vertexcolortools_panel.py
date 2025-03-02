#-------------------------------------------------
#-VERTEXCOLORTOOLS_PANEL.py
#-------------------------------------------------
from .global_settings import *
disable_cache()
# ================== PANEL =================
class XTD_PT_VertexColorTools(bpy.types.Panel):
    bl_label = "VERTEX COLOR TOOLS"
    bl_idname = "XTD_PT_vertexcolortools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"

    @classmethod
    def poll(cls, context):
        return VisibilityController.check_visibility(context, panel_name="vertexcolortools_panel", require_selected=True, require_prefix=True)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="BAKE SETTINGS:")
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        grid = box.grid_flow(columns=2, align=True)
        grid.prop(bpy.context.scene, "xtd_custom_bake_extrusion")
        grid.prop(bpy.context.scene, "xtd_custom_bake_raydistance")
        
        layout = self.layout
        row = layout.row()
        layout.label(text="VERTEX COLOR TOOLS:")
        
        box = layout.box()
        row.prop(context.scene, "xtd_tools_vertex_color_name", text="")
        
        row = box.row(align=True)
        row.operator("xtd_tools.activate_vertex_color", text="Activate")
        row.operator("xtd_tools.remove_vertex_color", text="Remove")
        
        row = box.row(align=True)
        row.operator("xtd_tools.create_vertex_color", text="Create")
        row.operator("xtd_tools.bake_vertex_color", text="Bake to selected")
        
        row = box.row(align=True)
        row.operator("xtd_tools.create_and_bake_vertex_color", text="Create and Bake")
        row.operator("xtd_tools.remove_all_vertex_colors", text="Remove All")

# ================ SCENES ================
bpy.types.Scene.xtd_tools_vertex_color_name = bpy.props.StringProperty(name="Vertex Color Name", default="VertexColor")

# ================ OPERATORS ================
class XTD_OT_ActivateVertexColor(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.activate_vertex_color"
    bl_label = "Activate Vertex Color"

    def process_object(self, obj):
        color_name = bpy.context.scene.xtd_tools_vertex_color_name
        if color_name in obj.data.color_attributes:
            obj.data.color_attributes.active = obj.data.color_attributes[color_name]
        return {'FINISHED'}

class XTD_OT_RemoveVertexColor(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.remove_vertex_color"
    bl_label = "Remove Vertex Color"

    def process_object(self, obj):
        color_name = bpy.context.scene.xtd_tools_vertex_color_name
        if color_name in obj.data.color_attributes:
            obj.data.color_attributes.remove(obj.data.color_attributes[color_name])
        return {'FINISHED'}

class XTD_OT_CreateVertexColor(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.create_vertex_color"
    bl_label = "Create Vertex Color"

    def process_object(self, obj):
        color_name = bpy.context.scene.xtd_tools_vertex_color_name
        bpy.context.view_layer.objects.active = obj
        if color_name not in obj.data.color_attributes:
            obj.data.color_attributes.new(name=color_name, type='FLOAT_COLOR', domain='POINT')
        else:
            obj.data.color_attributes.remove(obj.data.color_attributes[color_name])
            obj.data.color_attributes.new(name=color_name, type='FLOAT_COLOR', domain='POINT')
        return {'FINISHED'}

class XTD_OT_BakeVertexColor(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.bake_vertex_color"
    bl_label = "Bake to Vertex Color"

    def process_object(self, obj):
        bake_render_settings()
        color_name = bpy.context.scene.xtd_tools_vertex_color_name
        print('Bake...')
        obj.data.color_attributes.active = obj.data.color_attributes[color_name]
        bpy.context.scene.render.bake.use_selected_to_active = False
        bpy.context.scene.render.bake.target = 'VERTEX_COLORS'
        bpy.ops.object.bake(type='DIFFUSE')
        return {'FINISHED'}

class XTD_OT_CreateAndBakeVertexColor(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.create_and_bake_vertex_color"
    bl_label = "Create and Bake Vertex Color"

    def pre_process_object(self, context):
        bake_render_settings()
        bpy.context.scene.cycles.time_limit = 30
        bpy.context.scene.render.bake.use_selected_to_active = False
        bpy.context.scene.render.bake.target = 'VERTEX_COLORS'
        
    def pre_process_batch_objs(self, obj):
        color_name = bpy.context.scene.xtd_tools_vertex_color_name
        if color_name not in obj.data.color_attributes:
            obj.data.color_attributes.new(name=color_name, type='FLOAT_COLOR', domain='POINT')
        else:
            obj.data.color_attributes.remove(obj.data.color_attributes[color_name])
            obj.data.color_attributes.new(name=color_name, type='FLOAT_COLOR', domain='POINT')
        obj.data.color_attributes.active = obj.data.color_attributes[color_name]
    
    def process_object(self, obj):
        return
        
    def post_process_batch_objs(self, context):
        bpy.ops.object.bake(type='DIFFUSE')
        return {'FINISHED'}

class XTD_OT_RemoveAllVertexColors(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.remove_all_vertex_colors"
    bl_label = "Remove All Vertex Colors"

    def process_object(self, obj):
        attributes_names = [attr.name for attr in obj.data.color_attributes]
        for aname in attributes_names:
            attr = obj.data.color_attributes[aname]
            try:
                obj.data.color_attributes.remove(attr)
            except Exception as error:
                print("", error)
        
        return {'FINISHED'}


