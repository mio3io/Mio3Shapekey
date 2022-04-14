import bpy
from .define import *

def sync_shapekey_value():
    object = bpy.context.object
    if object.type not in OBJECT_TYPES or object.mio3sksync.syncs is None:
        return None
    shape_keys = object.data.shape_keys
    for item in object.mio3sksync.syncs.objects:
        # コレクションアイテム
        if item.type not in OBJECT_TYPES or item.active_shape_key is None or item == object:
            continue
        for item_key in item.data.shape_keys.key_blocks:
            if item_key.name in shape_keys.key_blocks:
                item_key.mute = shape_keys.key_blocks[item_key.name].mute
                if item_key.value != shape_keys.key_blocks[item_key.name].value:
                    item_key.value = shape_keys.key_blocks[item_key.name].value
