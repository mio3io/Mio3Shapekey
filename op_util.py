import bpy
from .define import *


class StashProp:
    def __init__(self, prop, name, value=None):
        self.prop = prop
        self.name = name
        self.tmp = getattr(prop, name, value)
        setattr(self.prop, name, value)

    def revert(self):
        setattr(self.prop, self.name, self.tmp)


def is_sync_collection(obj):
    return obj.type in OBJECT_TYPES and obj.mio3sksync.syncs is not None


def has_shapekey(obj):
    return obj.type in OBJECT_TYPES and obj.active_shape_key is not None
