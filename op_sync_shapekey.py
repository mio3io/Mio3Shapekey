import bpy
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
    prop_o = object.mio3sksync
    if is_sync_collection(object):
        for elem in [o for o in prop_o.syncs.objects if has_shapekey(o) and o != object]:
            index = elem.data.shape_keys.key_blocks.find(object.active_shape_key.name)
            elem.active_shape_key_index = index if index >= 0 else 0


msgbus_owner_auto_active_mirror_edit = object()


def register_auto_active_mirror_edit():
    bpy.msgbus.clear_by_owner(msgbus_owner_auto_active_mirror_edit)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "active_shape_key_index"),
        owner=msgbus_owner_auto_active_mirror_edit,
        args=(),
        notify=auto_active_mirror_edit,
    )


def unregister_auto_active_mirror_edit():
    bpy.msgbus.clear_by_owner(msgbus_owner_auto_active_mirror_edit)


def auto_active_mirror_edit():
    object = bpy.context.object
    prop_s = bpy.context.scene.mio3sk
    if prop_s.xmirror_auto_enabled and bpy.context.active_object.mode == "EDIT":

        object.data.use_mirror_x = True
        for lr_suffix in lr_suffix_types.values():
            trim_l = object.active_shape_key.name[-lr_suffix[1] :]
            trim_r = object.active_shape_key.name[-lr_suffix[3] :]
            if trim_l == lr_suffix[0] or trim_r == lr_suffix[2]:
                object.data.use_mirror_x = False
                break

        for win in bpy.context.window_manager.windows:
            [area.tag_redraw() for area in win.screen.areas if area.type in {"VIEW_3D"}]
