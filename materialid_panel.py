from .global_settings import *
disable_cache()
# ================== PANEL =================
class XTD_PT_MaterialID(bpy.types.Panel):
    bl_label = "Material ID Generator"
    bl_idname = "XTD_PT_materialid"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XTD Tools"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return VisibilityController.check_visibility(
            context, 
            panel_name="materialid_panel", 
            require_selected=True, 
            require_prefix=True
        )
        
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        row = layout.row()
        row.label(text="Material ID Assignment", icon="MATERIAL")
        row.separator()
        row.prop(scene, "xtd_materialid_fill_unfilled", expand=True)
        row = layout.row()
        row.prop(scene, "xtd_materialid_base_color", text="Base Color")
        row = layout.row(align=True)
        row.prop(scene, "xtd_materialid_to_add", text="")
        row.operator("xtd_tools.materialid_controller", text="Add", icon="ADD").action = "ADD"
        mat_ids = ["grass", "road", "dirtroad", "sidewalk", "duna", "building", "other"]
        for mat_id in mat_ids:
            visible_prop = f"xtd_materialid_{mat_id}_visible"
            if not getattr(scene, visible_prop):
                continue 
            color_prop = f"xtd_materialid_{mat_id}_color"
            filepath_prop = f"xtd_materialid_{mat_id}_filepath"
            strength_prop = f"xtd_materialid_{mat_id}_strength"
            box = layout.box()
            row = box.row(align=True)
            row.scale_x = 1
            preview_id = self.get_texture_preview(getattr(scene, filepath_prop))
            if preview_id:
                row.template_icon(icon_value=preview_id, scale=1.2)
            else:
                row.label(text="", icon='TEXTURE')
            row.enabled = False
            row.scale_x = 0.1
            row.scale_y = 1
            row.prop(scene, color_prop, text="")
            
            row.enabled = False
            row.scale_x = 0.15
            row.scale_y = 1.1
            row.label(text=f"{mat_id}")
            
            row.enabled = False
            row.scale_x = 0.3
            row.scale_y = 1.1
            row.prop(scene, strength_prop, text="", slider=True)
            
            row.enabled = True
            row.scale_x = 0.3
            row.scale_y = 1.1
            row.alignment = "EXPAND"
            row.prop(scene, filepath_prop, text="")

            row.scale_x = 1
            row.operator("xtd_tools.materialid_controller", text="", icon="TRASH").action = f"REMOVE_{mat_id}"
        layout = self.layout
        row = layout.row()
        row.operator("xtd_tools.materialid_controller", text="Run Generator", icon="PLAY").action = "RUN"
    def get_texture_preview(self, filepath):
        abspath = bpy.path.abspath(filepath)

        if not os.path.exists(abspath):
            return None

        try:
            img = bpy.data.images.load(abspath, check_existing=True)
            if img.preview is None:
                img.preview_ensure()
            return img.preview.icon_id if img.preview else None
        except RuntimeError:
            return None

# ================== PROPERTY CLASSES =================

bpy.types.Scene.xtd_materialid_base_color = bpy.props.FloatVectorProperty(
    name="Base Color",
    description="Fallback color for undefined areas",
    subtype='COLOR',
    default=(0.0, 0.0, 0.0),
    min=0.0,
    max=1.0
)

# Grass
bpy.types.Scene.xtd_materialid_grass_color = bpy.props.FloatVectorProperty(subtype='COLOR',default=(0.0, 1.0, 0.0),min=0.0,max=1.0)
bpy.types.Scene.xtd_materialid_grass_filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
bpy.types.Scene.xtd_materialid_grass_visible = bpy.props.BoolProperty(default=False)
bpy.types.Scene.xtd_materialid_grass_strength = bpy.props.IntProperty(name="Grass Dominance", default=50, min=0, max=100)

# Road
bpy.types.Scene.xtd_materialid_road_color = bpy.props.FloatVectorProperty(subtype='COLOR',default=(0.5, 0.5, 0.5),min=0.0,max=1.0)
bpy.types.Scene.xtd_materialid_road_filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
bpy.types.Scene.xtd_materialid_road_visible = bpy.props.BoolProperty(default=False)
bpy.types.Scene.xtd_materialid_road_strength = bpy.props.IntProperty(name="road Dominance", default=50, min=0, max=100)

# Dirt Road
bpy.types.Scene.xtd_materialid_dirtroad_color = bpy.props.FloatVectorProperty(subtype='COLOR',default=(0.82, 0.73, 0.67), min=0.0, max=1.0)
bpy.types.Scene.xtd_materialid_dirtroad_filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
bpy.types.Scene.xtd_materialid_dirtroad_visible = bpy.props.BoolProperty(default=False)
bpy.types.Scene.xtd_materialid_dirtroad_strength = bpy.props.IntProperty(name="dirtroad Dominance", default=50, min=0, max=100)

# Sidewalk
bpy.types.Scene.xtd_materialid_sidewalk_color = bpy.props.FloatVectorProperty(subtype='COLOR',default=(0.75, 0.75, 0.75), max=1.0)
bpy.types.Scene.xtd_materialid_sidewalk_filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
bpy.types.Scene.xtd_materialid_sidewalk_visible = bpy.props.BoolProperty(default=False)
bpy.types.Scene.xtd_materialid_sidewalk_strength = bpy.props.IntProperty(name="sidewalk Dominance", default=50, min=0, max=100)

# Building
bpy.types.Scene.xtd_materialid_building_color = bpy.props.FloatVectorProperty(subtype='COLOR', default=(1.0, 0.0, 0.0), min=0.0, max=1.0)
bpy.types.Scene.xtd_materialid_building_filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
bpy.types.Scene.xtd_materialid_building_visible = bpy.props.BoolProperty(default=False)
bpy.types.Scene.xtd_materialid_building_strength = bpy.props.IntProperty(name="building Dominance", default=50, min=0, max=100)

# Duna
bpy.types.Scene.xtd_materialid_duna_color = bpy.props.FloatVectorProperty(subtype='COLOR', default=(0.0, 0.5, 1.0), min=0.0, max=1.0)
bpy.types.Scene.xtd_materialid_duna_filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
bpy.types.Scene.xtd_materialid_duna_visible = bpy.props.BoolProperty(default=False)
bpy.types.Scene.xtd_materialid_duna_strength = bpy.props.IntProperty(name="duna Dominance", default=50, min=0, max=100)

# Other
bpy.types.Scene.xtd_materialid_other_color = bpy.props.FloatVectorProperty(subtype='COLOR', default=(1.0, 1.0, 1.0), min=0.0, max=1.0)
bpy.types.Scene.xtd_materialid_other_filepath = bpy.props.StringProperty(subtype='FILE_PATH', default="")
bpy.types.Scene.xtd_materialid_other_visible = bpy.props.BoolProperty(default=False)
bpy.types.Scene.xtd_materialid_other_strength = bpy.props.IntProperty(name="other Dominance", default=50, min=0, max=100)

bpy.types.Scene.xtd_materialid_fill_unfilled = bpy.props.EnumProperty(
    name="Fill Unfilled Areas",
    description="If enabled, unfilled black areas will be blended with surrounding colors",
    items=[('NO', "No", "Do not blend unfilled areas"),
           ('YES', "Yes", "Fill unfilled areas with surrounding colors")],
    default='NO'
)
def available_material_ids(self, context):
    scene = context.scene
    out = []
    all_ids = ["GRASS", "ROAD", "DIRTROAD", "SIDEWALK", "DUNA", "BUILDING", "OTHER"]
    for mat_id in all_ids:
        if not getattr(scene, f"xtd_materialid_{mat_id.lower()}_visible"):
            out.append((mat_id, mat_id.capitalize(), ""))
    return out


bpy.types.Scene.xtd_materialid_to_add = bpy.props.EnumProperty(
    name="Material ID Type",
    description="Choose a material ID to add",
    items=available_material_ids
)

# ================== CONTROLLER OPERATOR =================
class XTD_OT_MaterialIDController(global_settings.XTDToolsOperator):
    bl_idname = "xtd_tools.materialid_controller"
    bl_label = "Material ID Controller"

    action: bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        act = self.action.upper()

        if act == "ADD":
            mat_id = scene.xtd_materialid_to_add.upper()
            setattr(scene, f"xtd_materialid_{mat_id.lower()}_visible", True)

            bpy.types.Scene.xtd_materialid_to_add = bpy.props.EnumProperty(items=available_material_ids)

        elif act.startswith("REMOVE_"):
            mat_id = act.split("_")[1]
            setattr(scene, f"xtd_materialid_{mat_id.lower()}_visible", False)

            bpy.types.Scene.xtd_materialid_to_add = bpy.props.EnumProperty(items=available_material_ids)

        elif act == "RUN":
            all_ids = ["grass", "road", "dirtroad", "sidewalk", "duna", "building", "other"]
            used_ids = {}
            for mid in all_ids:
                path = getattr(scene, f"xtd_materialid_{mid}_filepath")
                if path:
                    color = getattr(scene, f"xtd_materialid_{mid}_color")
                    used_ids[mid.upper()] = (color, path)

            if not used_ids:
                self.report({'ERROR'}, "No active samples!")
                return {'CANCELLED'}

            self.generate_material_id_map(used_ids)
        
        return {'FINISHED'}


    def generate_material_id_map(self, samples):
        scene = bpy.context.scene

        for obj in bpy.context.selected_objects:
            if obj.type != 'MESH':
                continue
            if not obj.active_material or not obj.active_material.node_tree:
                self.report({'ERROR'}, f"No material/node tree in {obj.name}")
                continue

            tex_node = obj.active_material.node_tree.nodes.get('Image Texture')
            if not tex_node or not tex_node.image:
                self.report({'ERROR'}, f"No 'Image Texture' node found in {obj.name}")
                continue

            image_path = bpy.path.abspath(tex_node.image.filepath)
            if not os.path.exists(image_path):
                self.report({'ERROR'}, f"Image not found: {image_path}")
                continue

            base_name, ext = os.path.splitext(image_path)
            ext = ext.lower()
            out_path = f"{base_name}_materialid{ext}"
            counter = 1
            while os.path.exists(out_path):
                out_path = f"{base_name}_materialid_{counter}{ext}"
                counter += 1

            # 🔹 Eredeti textúra betöltése
            img = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if img is None:
                self.report({'ERROR'}, f"Cannot read image: {image_path}")
                continue

            h, w, _ = img.shape
            result_img = img.copy()

            # 🔹 UVMap generálása: az UV által nem fedett területek legyenek 0
            uv_map = np.ones((h, w), dtype=np.uint8) * 255
            black_mask = np.all(img == [0, 0, 0], axis=-1)
            uv_map[black_mask] = 0

            # 🔹 Feature Matching beállítása
            orb = cv2.ORB_create(nfeatures=100)  # ORB kulcspontok keresése

            # 🔹 Minden sample textúrát feldolgozunk
            for mat_id, (color_vec, sample_path) in samples.items():
                sample_img = cv2.imread(bpy.path.abspath(sample_path), cv2.IMREAD_COLOR)
                if sample_img is None:
                    continue

                # 🔹 **1️⃣ Template Matching gyors előszűrés**
                res = cv2.matchTemplate(img, sample_img, cv2.TM_CCOEFF_NORMED)
                threshold = 0.1  # Minőségküszöb
                loc = np.where(res >= threshold)

                # 🔹 **2️⃣ ORB Feature Matching a pontosításra**
                kp1, des1 = orb.detectAndCompute(sample_img, None)
                kp2, des2 = orb.detectAndCompute(img, None)

                bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                if des1 is not None and des2 is not None:
                    matches = bf.match(des1, des2)
                    matches = sorted(matches, key=lambda x: x.distance)

                    for match in matches:
                        x, y = kp2[match.trainIdx].pt
                        x, y = int(x), int(y)

                        # Ha a találat az előszűrt Template Matching helyeken is egyezik
                        if (y, x) in zip(*loc):
                            c_bgr = [int(c * 255) for c in reversed(color_vec)]
                            cv2.circle(result_img, (x, y), 5, c_bgr, -1)

            # 🔹 Opcionális Fill a hiányzó részekhez
            if scene.xtd_materialid_fill_unfilled == 'YES':
                print("🔄 Blending unfilled areas with surrounding colors...")
                gray = cv2.cvtColor(result_img, cv2.COLOR_BGR2GRAY)
                unfilled_mask = (gray == 0).astype(np.uint8) * 255
                unfilled_mask[uv_map == 0] = 0
                result_img = cv2.inpaint(result_img, unfilled_mask, inpaintRadius=1, flags=cv2.INPAINT_TELEA)

            # 🔹 Végső mentés
            cv2.imwrite(out_path, result_img)
            self.report({'INFO'}, f"Material ID map saved: {out_path}")
            print(f"✅ Original: {image_path} → New: {out_path}")