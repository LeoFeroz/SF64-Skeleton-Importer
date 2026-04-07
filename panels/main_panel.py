import bpy
import os
from .. utils import limb_parser

class SF64_PT_panel(bpy.types.Panel):
    bl_label = "SF64 Skeleton Importer"
    bl_idname = "SF64_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SF64"

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="Star Fox 64 Tools", icon='ARMATURE_DATA')
        
        layout.prop(context.scene, "sf64_file")
        layout.prop(context.scene, "sf64_skeleton_name")
        layout.prop(context.scene, "sf64_scale")
        
        row = layout.row()
        row.scale_y = 1.5
        op = row.operator("sf64.import_skeleton", text="Import Skeleton Only")
        op.auto_import_meshes = False
        op.add_constraints = False
        
        row = layout.row()
        row.scale_y = 1.5
        op_full = row.operator("sf64.import_skeleton", text="Import ALL (Fast64)")
        op_full.auto_import_meshes = True
        op_full.add_constraints = True
        
        if context.scene.sf64_file and context.scene.sf64_skeleton_name:
            try:
                with open(context.scene.sf64_file, "r", encoding="utf-8") as f:
                    text = f.read()
                all_limbs = limb_parser.parse_all_limbs(text)
                limb_names = limb_parser.parse_skeleton_array(text, context.scene.sf64_skeleton_name)
                if limb_names:
                    mesh_to_limbs = limb_parser.extract_mesh_names(all_limbs, limb_names)
                    if mesh_to_limbs:
                        total_unique = len(mesh_to_limbs)
                        total_assignments = sum(len(limbs) for limbs in mesh_to_limbs.values())
                        box = layout.box()
                        box.label(text=f"Unique meshes: {total_unique}", icon='OBJECT_DATA')
                        box.label(text=f"Total assignments: {total_assignments}", icon='CONSTRAINT')
                        
                        shared = [(m, l) for m, l in mesh_to_limbs.items() if len(l) > 1]
                        if shared:
                            box.label(text=f"Shared meshes: {len(shared)}", icon='COPY_ID')
            except:
                pass
        
        layout.separator()
        box = layout.box()
        box.label(text="Tip:", icon='INFO')
        box.label(text="Use 'Import ALL' to import")
        box.label(text="skeleton + all meshes + constraints")
        box.label(text="Shared meshes are automatically duplicated")

def register():
    bpy.utils.register_class(SF64_PT_panel)

def unregister():
    bpy.utils.unregister_class(SF64_PT_panel)