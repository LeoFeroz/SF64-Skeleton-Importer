import bpy
import os
import time

def import_mesh_via_fast64(file_path, mesh_name, base_path, draw_layer="0"):
    try:
        scene = bpy.context.scene
        
        scene.DLImportPath = file_path
        scene.DLImportBasePath = base_path
        scene.DLImportName = mesh_name
        scene.blenderF3DScale = 100.0
        
        if hasattr(scene, "DLRemoveDoubles"):
            scene.DLRemoveDoubles = True
        if hasattr(scene, "DLImportNormals"):
            scene.DLImportNormals = True
        
        if hasattr(scene, "DLImportDrawLayer"):
            try:
                scene.DLImportDrawLayer = draw_layer
            except TypeError:
                try:
                    prop = scene.bl_rna.properties.get("DLImportDrawLayer")
                    if prop and prop.type == 'ENUM' and prop.enum_items:
                        scene.DLImportDrawLayer = prop.enum_items[0].identifier
                except:
                    pass
        
        time.sleep(0.05)
        
        result = bpy.ops.object.f3d_import_dl('INVOKE_DEFAULT')
        
        return result == {'FINISHED'}
        
    except Exception as e:
        return False

def find_imported_mesh(mesh_name):
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH' and mesh_name in obj.name:
            return obj
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name.startswith(mesh_name):
            return obj
    
    return None

def duplicate_mesh_for_limb(mesh_obj, limb_name, original_mesh_name):
    new_mesh = mesh_obj.copy()
    new_mesh.data = mesh_obj.data.copy()
    new_mesh.name = f"{original_mesh_name}_Limb_{limb_name}"
    
    bpy.context.collection.objects.link(new_mesh)
    
    return new_mesh

def import_meshes_with_duplication(file_path, mesh_to_limbs, operator=None):
    base_path = os.path.dirname(file_path)
    total_meshes = len(mesh_to_limbs)
    
    limb_mesh_map = {}
    
    wm = bpy.context.window_manager
    wm.progress_begin(0, total_meshes)
    
    for i, (mesh_name, limb_list) in enumerate(mesh_to_limbs.items(), 1):
        wm.progress_update(i)
        
        if operator:
            operator.report({'INFO'}, f"Processing [{i}/{total_meshes}]: {mesh_name}")
        
        success = import_mesh_via_fast64(file_path, mesh_name, base_path)
        
        if not success:
            if operator:
                operator.report({'WARNING'}, f"Failed to import {mesh_name}")
            continue
        
        mesh_obj = find_imported_mesh(mesh_name)
        
        if not mesh_obj:
            continue
        
        if len(limb_list) == 1:
            limb_name = limb_list[0]
            limb_mesh_map[limb_name] = mesh_obj
        else:
            for idx, limb_name in enumerate(limb_list):
                if idx == 0:
                    limb_mesh_map[limb_name] = mesh_obj
                    mesh_obj.name = f"{mesh_name}_Limb_{limb_name}"
                else:
                    dup_obj = duplicate_mesh_for_limb(mesh_obj, limb_name, mesh_name)
                    limb_mesh_map[limb_name] = dup_obj
        
        time.sleep(0.1)
    
    wm.progress_end()
    
    return limb_mesh_map