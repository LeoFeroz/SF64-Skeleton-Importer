bl_info = {
    "name": "SF64 Skeleton Importer",
    "author": "LeoFeroz",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > SF64",
    "description": "Import SF64 skeleton and automatically import all meshes using Fast64",
    "category": "Import",
}

import bpy
from . properties import scene_properties
from . operators import import_skeleton
from . panels import main_panel

modules = [
    scene_properties,
    import_skeleton,
    main_panel,
]

def register():
    for module in modules:
        module.register()

def unregister():
    for module in reversed(modules):
        module.unregister()

if __name__ == "__main__":
    register()