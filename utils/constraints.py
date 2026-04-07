import bpy

def add_constraints_to_meshes(limb_mesh_map):
    success_count = 0
    for limb_name, mesh_obj in limb_mesh_map.items():
        if limb_name in bpy.data.objects:
            bone_obj = bpy.data.objects[limb_name]
            
            bpy.context.view_layer.objects.active = mesh_obj
            
            mesh_obj.constraints.clear()
            
            loc_constraint = mesh_obj.constraints.new(type='COPY_LOCATION')
            loc_constraint.target = bone_obj
            loc_constraint.use_offset = False
            loc_constraint.target_space = 'WORLD'
            loc_constraint.owner_space = 'WORLD'
            
            rot_constraint = mesh_obj.constraints.new(type='COPY_ROTATION')
            rot_constraint.target = bone_obj
            rot_constraint.use_offset = False
            rot_constraint.target_space = 'WORLD'
            rot_constraint.owner_space = 'WORLD'
            rot_constraint.mix_mode = 'REPLACE'
            
            success_count += 1
    
    return success_count