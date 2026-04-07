import bpy

def register():
    bpy.types.Scene.sf64_file = bpy.props.StringProperty(
        name="C File",
        description=".c file containing skeleton definitions",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.sf64_skeleton_name = bpy.props.StringProperty(
        name="Skeleton Name",
        description="Name of the skeleton array (e.g., D_ANDROSS_C01CC3C_skeleton)"
    )

    bpy.types.Scene.sf64_scale = bpy.props.FloatProperty(
        name="Scale",
        description="Scale factor for the skeleton",
        default=100.0,
        min=0.0001,
        soft_min=1.0,
        soft_max=1000.0
    )

def unregister():
    del bpy.types.Scene.sf64_file
    del bpy.types.Scene.sf64_skeleton_name
    del bpy.types.Scene.sf64_scale