import bpy
from .define import *


def is_sync_collection(obj):
    return obj.type in OBJECT_TYPES and obj.mio3sksync.syncs is not None

def has_shapekey(obj):
    return obj.type in OBJECT_TYPES and obj.active_shape_key is not None