import re
from mathutils import Vector

class Limb:
    def __init__(self, name, gfx_ptr, trans, rot, sibling, child):
        self.name = name
        self.gfx_ptr = gfx_ptr
        self.trans = Vector(trans)
        self.rot = rot
        self.sibling = sibling
        self.child = child

def parse_all_limbs(text):
    limbs = {}

    pattern = re.compile(
        r"Limb\s+(\w+)\s*=\s*\{\s*"
        r"([^,]+),\s*"
        r"\{([^}]*)\},\s*"
        r"\{([^}]*)\},\s*"
        r"([^,]*),\s*"
        r"([^}]*)\}"
    )

    for m in pattern.finditer(text):
        name = m.group(1)
        gfx_ptr = m.group(2).strip()
        
        trans = [float(v.strip()) for v in m.group(3).split(",")]
        rot = [int(v.strip()) for v in m.group(4).split(",")]

        sibling = m.group(5).strip()
        child = m.group(6).strip()

        sibling = None if sibling == "NULL" else sibling.replace("&", "").rstrip(",")
        child = None if child == "NULL" else child.replace("&", "").rstrip(",")
        
        limbs[name] = Limb(name, gfx_ptr, trans, rot, sibling, child)

    return limbs

def parse_skeleton_array(text, skeleton_name):
    pattern = re.compile(
        r"Limb\s*\*\s*" + re.escape(skeleton_name) +
        r"\s*\[\s*\]\s*=\s*\{([^}]*)\}",
        re.S
    )

    m = pattern.search(text)
    if not m:
        return None

    content = m.group(1)
    raw = re.findall(r"&([^\s,}]+)", content)
    return [n.strip().rstrip(",") for n in raw]

def extract_mesh_names(limbs, limb_names):
    mesh_to_limbs = {}
    
    for name in limb_names:
        if name in limbs:
            limb = limbs[name]
            if limb.gfx_ptr != "NULL":
                if limb.gfx_ptr not in mesh_to_limbs:
                    mesh_to_limbs[limb.gfx_ptr] = []
                mesh_to_limbs[limb.gfx_ptr].append(name)
    
    return mesh_to_limbs