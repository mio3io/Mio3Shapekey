import os

OBJECT_TYPES = {"MESH", "CURVE", "SURFACE", "LATTICE"}
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "_templates")

lr_suffix_types_source = [
    ("_head", "_L", "_R"),
    ("upper", "Left", "Right"),
    ("lower", "left", "Right"),
    ("ja", "左", "右"),
]
lr_suffix_types = {k: (l, len(l), r, len(r)) for (k, l, r) in lr_suffix_types_source}
