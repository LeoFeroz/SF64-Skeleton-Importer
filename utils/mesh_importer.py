import bpy
import os
import time


# ---------------------------------------------------------------------------
# Fallback registration for Fast64's F3D DL importer scene properties.
#
# Some Fast64 builds/forks ship `f3d_parser_register()` as a no-op (`pass`),
# which means `bpy.types.Scene.DLImportName`, `DLImportPath`,
# `DLImportBasePath`, `DLRemoveDoubles`, `DLImportNormals` and
# `DLImportDrawLayer` are never created on the Scene type, even though the
# `F3D_ImportDL` operator (`bpy.ops.object.f3d_import_dl`) still reads them.
# That mismatch makes the operator raise AttributeError as soon as it's
# invoked. We defensively (re)create any missing property here, mirroring
# what Fast64's own f3d_parser.py normally registers, so the import keeps
# working even against a Fast64 build with this regression.
# ---------------------------------------------------------------------------
_FALLBACK_PROPS_ENSURED = False


def _get_draw_layer_enum_items():
    import sys

    for mod_name, mod in list(sys.modules.items()):
        if mod is None:
            continue
        if mod_name.endswith("f3d_material") and hasattr(mod, "ootEnumDrawLayers"):
            return mod.ootEnumDrawLayers
        if mod_name.endswith(".utility") and hasattr(mod, "ootEnumDrawLayers"):
            return mod.ootEnumDrawLayers

    return [(str(i), str(i), f"Draw Layer {i}") for i in range(8)]


def ensure_dl_import_scene_props():
    
    global _FALLBACK_PROPS_ENSURED

    Scene = bpy.types.Scene

    if not hasattr(Scene, "DLImportName"):
        Scene.DLImportName = bpy.props.StringProperty(name="Name")

    if not hasattr(Scene, "DLImportPath"):
        Scene.DLImportPath = bpy.props.StringProperty(name="File", subtype="FILE_PATH")

    if not hasattr(Scene, "DLImportBasePath"):
        Scene.DLImportBasePath = bpy.props.StringProperty(name="Directory", subtype="FILE_PATH")

    if not hasattr(Scene, "blenderF3DScale"):
        Scene.blenderF3DScale = bpy.props.FloatProperty(name="Scale", default=100.0)

    if not hasattr(Scene, "DLRemoveDoubles"):
        Scene.DLRemoveDoubles = bpy.props.BoolProperty(name="Remove Doubles", default=True)

    if not hasattr(Scene, "DLImportNormals"):
        Scene.DLImportNormals = bpy.props.BoolProperty(name="Import Normals", default=True)

    if not hasattr(Scene, "DLImportDrawLayer"):
        Scene.DLImportDrawLayer = bpy.props.EnumProperty(
            name="Draw Layer", items=_get_draw_layer_enum_items()
        )

    _FALLBACK_PROPS_ENSURED = True


def _find_loaded_f3d_parser_module():

    import sys

    for mod_name, mod in list(sys.modules.items()):
        if mod is None:
            continue
        if mod_name.endswith("f3d.f3d_parser") or mod_name.endswith(".f3d_parser"):
            if hasattr(mod, "F3D_ImportDL"):
                return mod
    return None


def _bl_idname_class_name(bl_idname):
    category, _, name = bl_idname.partition(".")
    return f"{category.upper()}_OT_{name}"


def ensure_f3d_parser_classes_registered():

    mod = _find_loaded_f3d_parser_module()
    if mod is None:
        print("[SF64 Importer] Could not locate Fast64's f3d_parser module to register fallback classes.")
        return False

    classes = getattr(mod, "f3d_parser_classes", None)
    if not classes:
        # Fall back to just the operator itself if the tuple isn't exposed.
        classes = (getattr(mod, "F3D_ImportDL", None),)
        classes = tuple(c for c in classes if c is not None)

    any_registered = False
    for cls in classes:
        existing = getattr(bpy.types, _bl_idname_class_name(getattr(cls, "bl_idname", "")), None) \
            if hasattr(cls, "bl_idname") else getattr(bpy.types, cls.__name__, None)
        if existing is not None:
            continue
        try:
            bpy.utils.register_class(cls)
            any_registered = True
        except Exception as e:
            print(f"[SF64 Importer] Failed to register fallback class {cls}: {e}")

    return any_registered


_FALLBACK_OPERATOR_ENSURED = False


def ensure_f3d_import_operator_available():
    
    global _FALLBACK_OPERATOR_ENSURED
    if hasattr(bpy.types, "OBJECT_OT_f3d_import_dl"):
        _FALLBACK_OPERATOR_ENSURED = True
        return True

    ensure_f3d_parser_classes_registered()

    available = hasattr(bpy.types, "OBJECT_OT_f3d_import_dl")
    _FALLBACK_OPERATOR_ENSURED = available
    return available


def import_mesh_via_fast64(file_path, mesh_name, base_path, draw_layer="0"):
    try:
        ensure_dl_import_scene_props()

        if not ensure_f3d_import_operator_available():
            print(
                "[SF64 Importer] bpy.ops.object.f3d_import_dl is not registered "
                "and could not be registered from Fast64's f3d_parser module. "
                "Check that Fast64 is enabled and up to date."
            )
            return False

        scene = bpy.context.scene
        
        scene.DLImportPath = file_path
        scene.DLImportBasePath = base_path
        scene.DLImportName = mesh_name
        scene.blenderF3DScale = 100.0

        print(
            f"[SF64 Importer] DEBUG: set DLImportBasePath = {scene.DLImportBasePath!r} "
            f"(requested base_path = {base_path!r}); "
            f"abspath = {bpy.path.abspath(scene.DLImportBasePath)!r}"
        )
        
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
        print(f"[SF64 Importer] import_mesh_via_fast64 failed for '{mesh_name}': {e}")
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
