#-------------------------------------------------
#-VERTEXGROUPTOOLS_PANEL.py
#-------------------------------------------------

from .global_settings import *

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
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.scale_x = 0.5
        
        for i in range(0,2,2):
            row = box.row(align=True)
            row.label(text="ADD NEW VERTEX GROUP TO SELECTED:")
            row = box.row(align=True)
            row.scale_x = 0.30
            row.label(text="Group name:")
            row.scale_x = 0.30
            row.prop(bpy.context.scene, "vertexgroupname")
            row.scale_x = 0.40
            row.operator("xtd_tools.create_vertex_groups", text="CREATE")
            
        for i in range(0,2,2):
            row = box.row(align=True)
            row.operator("xtd_tools.addgeometrynodesvertexgroup", text="Assign to Geometry Nodes")
        for i in range(0,2,2):
            row = box.row(align=True)
            row.operator("xtd_tools.addselected_vertex_groups", text="Add selected verts to group")
        for i in range(0,2,2):
            row = box.row(align=True)
            row.separator()
            row = box.row(align=True)
            row.scale_x = 0.40
            row.operator("xtd_tools.removevertexgroups", text="REMOVE All", icon="TRASH")
            row.separator()
            row.scale_x = 0.60
            row.prop(bpy.context.scene, "remove_hiddenattributes", text="Hidden attributes too?")
            
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

        vertexgroup=obj.vertex_groups.get(vertexgroupname) or obj.vertex_groups.new(name=vertexgroupname)

        vertexgroup.name = vertexgroupname
        

        return {'FINISHED'}

class XTD_OT_AddSelectedVertexGroups(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.addselected_vertex_groups"
    bl_label = "Vertex Group Assign Selected"
    bl_description = "Létrehoz egy vertex group-ot az aktív objektumokon"
    bl_options = {'REGISTER', 'UNDO'}
    

    def process_object(self, context):
        
        vertexgroupname = bpy.context.scene.vertexgroupname
        global_deselect(context, all_objects=False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        vg = obj.vertex_groups.get(vertexgroupname)
        if vg is not None:
            obj.vertex_groups.remove(vg)
            attr = [attr for attr in obj.data.attributes]
            attributes_names = [attr.name for attr in obj.data.attributes]
            print(f"Check attributes...")
            if not attr.is_internal:
                print(f"Clear not internals")
                for aname in attributes_names:
                    attr = obj.data.attributes[aname]
                    try:
                        obj.data.attributes.remove(vg)
                    except Exception as error:
                        print("oops, an exception occurred:", error)
                        
        bpy.ops.object.vertex_group_add()
        vertex_group = obj.vertex_groups[-1]
        vertex_group.name = vertexgroupname
        
        mesh = obj.data
        print(f"Add to {len(mesh.vertices)} verticles only selected")
        workvert = len(mesh.vertices)
        reported_percentages = set()
        wv = 0
        for wv, v in enumerate(mesh.vertices, start=1):
            percent = int((wv / workvert) * 100)
            if percent % 10 == 0 and percent not in reported_percentages:
                sys.stdout.write(f"\r{percent}% completed")  # Sor elejére ugrik és felülírja
                sys.stdout.flush()
                reported_percentages.add(percent)
            if v.select:
                vertex_group.add([v.index], 1.0, 'ADD')
        return {'FINISHED'}
        
class XTD_OT_addgeometrynodesvertexgroup(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.addgeometrynodesvertexgroup"
    bl_label = "Vertex Group hozzáadása Geometry nodeshoz. "
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        
        vertexgroupname = bpy.context.scene.vertexgroupname
        vg = obj.vertex_groups.get(vertexgroupname)
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

