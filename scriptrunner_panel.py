#-------------------------------------------------
#-SCRIPTRUNNER_TOOL.py (Mode switch: LOCAL | FILE)
#-------------------------------------------------
from .global_settings import *
import re
disable_cache()
# ================== PANEL =================
class XTD_PT_ScriptRunner(bpy.types.Panel):
    bl_label = "SCRIPT RUNNER"
    bl_idname = "XTD_PT_script_runner"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"

    @classmethod
    def poll(cls, context):
        return VisibilityController.check_visibility(context, panel_name="scriptrunner_panel", require_selected=True)

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene

        box = layout.box()
        row = box.row()
        row.label(text="Python Script Executor", icon="CONSOLE")

        row = box.row()
        row.prop(scene, "script_runner_mode", expand=True)

        if scene.script_runner_mode == "LOCAL":
            row = box.row()
            row.prop(scene, "script_runner_selected", text="")
        else:
            row = box.row()
            row.prop(scene, "script_runner_filepath", text="")

        row = box.row()
        row.operator("xtd_tools.run_script", text="Run Script", icon="PLAY")

# ================ PROPERTYS ================
def update_text_list(self, context):
    """Frissíti a Blender Text Editor-ban lévő szkriptek listáját."""
    return [(text.name, text.name, "") for text in bpy.data.texts]

bpy.types.Scene.script_runner_mode = bpy.props.EnumProperty(
    name="Mód",
    description="Válaszd ki, honnan futtassuk a szkriptet",
    items=[
        ("LOCAL", "Blender Text", "Szkript a Blender belső Text Editorából"),
        ("FILE", "Külső fájl", "Szkript külső Python fájlból")
    ],
    default="LOCAL"
)

bpy.types.Scene.script_runner_selected = bpy.props.EnumProperty(
    name="Script",
    description="Select a script from the project",
    items=update_text_list
)

bpy.types.Scene.script_runner_text = bpy.props.EnumProperty(
    name="Szkript",
    description="Válaszd ki a futtatandó szkriptet",
    items=update_text_list
)

bpy.types.Scene.script_runner_filepath = bpy.props.StringProperty(
    name="Szkript Fájl",
    description="Útvonal egy külső Python szkript fájlhoz",
    default="",
    subtype='FILE_PATH'
)

# ================ OPERATOR ================
class XTD_OT_RunScript(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.run_script"
    bl_label = "Run Script"
    bl_description = "Execute the selected script on all selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def process_object(self, obj):
        scene = bpy.context.scene

        # A futtatandó szkript betöltése a kiválasztott módtól függően
        if scene.script_runner_mode == "LOCAL":
            script_name = scene.script_runner_text
            text = bpy.data.texts.get(script_name)
            if not text:
                self.report({'WARNING'}, "A kiválasztott szkript nem található!")
                return {'CANCELLED'}
            script_code = text.as_string()
        else:
            # Külső fájl
            filepath = bpy.path.abspath(scene.script_runner_filepath).strip()
            if not filepath or not os.path.exists(filepath):
                self.report({'WARNING'}, "Érvénytelen vagy nem létező fájlútvonal!")
                return {'CANCELLED'}
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    script_code = f.read()
            except Exception as e:
                self.report({'ERROR'}, f"Hiba a fájl beolvasása közben: {e}")
                return {'CANCELLED'}

        # Módosítás: cseréljük le a bpy.context.object hivatkozást az 'obj'-re
        script_code = re.sub(r'\bbpy\.context\.object\b', 'obj', script_code)

        # Ellenőrzés: vannak-e kiválasztott objektumok?
        selected_objects = bpy.context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "Nincs kiválasztott objektum!")
            return {'CANCELLED'}

        # A szkriptet minden kiválasztott objektumra lefuttatjuk
        for obj in selected_objects:
            try:
                # A futtatás lokális környezete: csak "obj" (az aktuális objektum) és "bpy" érhető el
                exec(script_code, {"obj": obj, "bpy": bpy})
            except Exception as e:
                self.report({'ERROR'}, f"Hiba a szkript futtatása közben ({obj.name}): {e}")
                return {'CANCELLED'}

        self.report({'INFO'}, "A szkript sikeresen lefutott minden kiválasztott objektumon.")
        return {'FINISHED'}
