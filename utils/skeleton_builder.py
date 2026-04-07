import bpy
from mathutils import Matrix, Euler
from math import pi

def n64_to_rad(v):
    return (v / 32768.0) * pi

def build_empties(limbs, limb_names, skeleton_name, scale_value, operator=None):
    collection = bpy.context.collection
    scale_factor = scale_value * 0.0001

    root = bpy.data.objects.new(skeleton_name + "_ROOT", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.scale = (scale_factor, scale_factor, scale_factor)
    collection.objects.link(root)

    empty_size_cube = 0.05 * scale_value
    empty_size_sphere = 3.0

    global_matrix = {}
    parent_map = {}

    conversion_matrix = Matrix((
        (1, 0, 0, 0),
        (0, 0, -1, 0),
        (0, 1, 0, 0),
        (0, 0, 0, 1)
    ))
    
    def compute_global(name, parent=None):
        if name not in limbs:
            return Matrix.Identity(4)

        if name in global_matrix:
            return global_matrix[name]

        limb = limbs[name]

        T = Matrix.Translation(limb.trans)

        R = Euler((
            n64_to_rad(limb.rot[0]),
            n64_to_rad(limb.rot[1]),
            n64_to_rad(limb.rot[2])
        )).to_matrix().to_4x4()

        local = T @ R
        
        local = conversion_matrix @ local @ conversion_matrix.inverted()

        if parent and parent in limbs:
            global_matrix[name] = compute_global(parent) @ local
        else:
            global_matrix[name] = local

        return global_matrix[name]

    referenced = set()
    for n in limb_names:
        l = limbs.get(n)
        if l and l.child:
            referenced.add(l.child)

    roots = [n for n in limb_names if n not in referenced and n in limbs]

    def walk(name, parent=None):
        if name not in limbs:
            return

        compute_global(name, parent)
        parent_map[name] = parent

        limb = limbs[name]

        if limb.child:
            walk(limb.child, name)

        if limb.sibling:
            walk(limb.sibling, parent)

    for r in roots:
        walk(r, None)

    objects = {}
    limb_to_gfx_map = {}

    for name in limb_names:
        if name not in global_matrix:
            continue

        limb = limbs[name]
        
        if limb.gfx_ptr == "NULL":
            empty_type = 'CUBE'
            empty_size = empty_size_cube
        else:
            empty_type = 'SPHERE'
            empty_size = empty_size_sphere
            limb_to_gfx_map[name] = limb.gfx_ptr

        obj = bpy.data.objects.new(name, None)
        obj.empty_display_type = empty_type
        obj.empty_display_size = empty_size
        
        obj.show_in_front = True

        obj.matrix_world = global_matrix[name]
        collection.objects.link(obj)

        obj.parent = root
        obj.matrix_parent_inverse = root.matrix_world.inverted()

        objects[name] = obj

    for name, parent in parent_map.items():
        if parent and parent in objects:
            objects[name].parent = objects[parent]
            objects[name].matrix_parent_inverse = objects[parent].matrix_world.inverted()
    
    if operator:
        operator.report({'INFO'}, f"Skeleton created with {len(limb_names)} bones")
    
    return root, objects, limb_to_gfx_map