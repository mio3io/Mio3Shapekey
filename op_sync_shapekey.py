import bpy
from bpy.app.handlers import persistent
from .define import *
from .op_util import *


def sync_shapekey_value():
    if bpy.context.active_object is None:
        return
    object = bpy.context.object
    prop_o = object.mio3sksync
    if is_sync_collection(object):
        key_blocks = object.data.shape_keys.key_blocks
        for item in [v for v in prop_o.syncs.objects if has_shapekey(v) and v != object]:
            for item_key in item.data.shape_keys.key_blocks:
                if item_key.name in key_blocks:
                    if item_key.mute != key_blocks[item_key.name].mute:
                        item_key.mute = key_blocks[item_key.name].mute
                    if item_key.value != key_blocks[item_key.name].value:
                        item_key.value = key_blocks[item_key.name].value


def sync_show_only_shape_key():
    object = bpy.context.object
    prop_o = object.mio3sksync
    if is_sync_collection(object):
        for item in [v for v in prop_o.syncs.objects if has_shapekey(v) and v != object]:
            if item.show_only_shape_key != object.show_only_shape_key:
                item.show_only_shape_key = object.show_only_shape_key


def sync_active_shape_key():
    object = bpy.context.object
    prop_s = bpy.context.scene.mio3sk
    prop_o = object.mio3sksync
    if prop_s.sync_active_shapekey_enabled:
        if is_sync_collection(object):
            for elem in [o for o in prop_o.syncs.objects if has_shapekey(o) and o != object]:
                index = elem.data.shape_keys.key_blocks.find(object.active_shape_key.name)
                elem.active_shape_key_index = index if index >= 0 else 0
        prop_s.rename_inputname = str(bpy.context.object.active_shape_key.name)


@persistent
def load_handler(scene):
    register()


msgbus_owner = object()


def register():

    bpy.msgbus.clear_by_owner(msgbus_owner)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "active_shape_key_index"),
        owner=msgbus_owner,
        args=(),
        notify=sync_active_shape_key,
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.ShapeKey, "value"),
        owner=msgbus_owner,
        args=(),
        notify=sync_shapekey_value,
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.ShapeKey, "mute"),
        owner=msgbus_owner,
        args=(),
        notify=sync_shapekey_value,
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "show_only_shape_key"),
        owner=msgbus_owner,
        args=(),
        notify=sync_show_only_shape_key,
    )

    if load_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_handler)


def unregister():
    bpy.msgbus.clear_by_owner(msgbus_owner)
    bpy.app.handlers.load_post.remove(load_handler)
