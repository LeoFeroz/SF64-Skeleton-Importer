import bpy
import os
from .. utils import limb_parser, mesh_importer, skeleton_builder, constraints

class SF64_OT_import(bpy.types.Operator):
    bl_idname = "sf64.import_skeleton"
    bl_label = "Import Skeleton"
    bl_options = {'REGISTER', 'UNDO'}
    
    auto_import_meshes: bpy.props.BoolProperty(
        name="Auto Import Meshes",
        description="Automatically import all meshes using Fast64",
        default=True
    )
    
    add_constraints: bpy.props.BoolProperty(
        name="Add Constraints",
        description="Add Copy Location and Copy Rotation constraints to meshes",
        default=True
    )

    def execute(self, context):
        path = context.scene.sf64_file
        skel_name = context.scene.sf64_skeleton_name
        scale_val = context.scene.sf64_scale

        if not path:
            self.report({'ERROR'}, "Choose a .c file")
            return {'CANCELLED'}

        if not skel_name:
            self.report({'ERROR'}, "Enter skeleton name")
            return {'CANCELLED'}

        self.report({'INFO'}, "Loading file...")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            self.report({'ERROR'}, f"Error reading file: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, "Parsing limbs...")
        all_limbs = limb_parser.parse_all_limbs(text)
        
        self.report({'INFO'}, "Parsing skeleton...")
        limb_names = limb_parser.parse_skeleton_array(text, skel_name)

        if not limb_names:
            self.report({'ERROR'}, "Skeleton not found")
            return {'CANCELLED'}

        mesh_to_limbs = limb_parser.extract_mesh_names(all_limbs, limb_names)
        
        self.report({'INFO'}, f"Creating skeleton with {len(limb_names)} bones...")
        root, limb_objects, limb_to_gfx_map = skeleton_builder.build_empties(
            all_limbs, limb_names, skel_name, scale_val, self
        )
        
        if self.auto_import_meshes and mesh_to_limbs:
            total_unique = len(mesh_to_limbs)
            total_assignments = sum(len(limbs) for limbs in mesh_to_limbs.values())
            
            self.report({'INFO'}, f"Starting import of {total_unique} unique meshes ({total_assignments} total assignments)...")
            
            limb_mesh_map = mesh_importer.import_meshes_with_duplication(path, mesh_to_limbs, self)
            
            if limb_mesh_map:
                self.report({'INFO'}, f"COMPLETE! {len(limb_mesh_map)} mesh assignments created")
                
                if self.add_constraints:
                    self.report({'INFO'}, "Adding constraints to meshes...")
                    constraints_added = constraints.add_constraints_to_meshes(limb_mesh_map)
                    self.report({'INFO'}, f"Added constraints to {constraints_added} meshes")
            else:
                self.report({'ERROR'}, "No meshes were imported. Check the console.")
        else:
            if mesh_to_limbs:
                total_unique = len(mesh_to_limbs)
                total_assignments = sum(len(limbs) for limbs in mesh_to_limbs.values())
                self.report({'INFO'}, f"Skeleton OK. {total_unique} unique meshes ({total_assignments} assignments) available")
            else:
                self.report({'INFO'}, f"Skeleton created with {len(limb_names)} bones")

        return {'FINISHED'}

def register():
    bpy.utils.register_class(SF64_OT_import)

def unregister():
    bpy.utils.unregister_class(SF64_OT_import)