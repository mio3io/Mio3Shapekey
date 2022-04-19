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
                if item_key.mute != shape_keys.key_blocks[item_key.name].mute:
                    item_key.mute = shape_keys.key_blocks[item_key.name].mute
                if item_key.value != shape_keys.key_blocks[item_key.name].value:
                    item_key.value = shape_keys.key_blocks[item_key.name].value


msgbus_owner_sync_active_shape_key = object()


def register_active_shape_key():
    bpy.msgbus.clear_by_owner(msgbus_owner_sync_active_shape_key)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "active_shape_key_index"),
        owner=msgbus_owner_sync_active_shape_key,
        args=(),
        notify=sync_active_shape_key,
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.ShapeKey, "name"),
        owner=msgbus_owner_sync_active_shape_key,
        args=(),
        notify=sync_rename,
    )


def unregister_active_shape_key():
    bpy.msgbus.clear_by_owner(msgbus_owner_sync_active_shape_key)


def sync_active_shape_key():
    object = bpy.context.object
    if object.type not in OBJECT_TYPES or object.mio3sksync.syncs is None:
        return None
    for item in object.mio3sksync.syncs.objects:
        if item.type not in OBJECT_TYPES or item.active_shape_key is None or item == object:
            continue
        index = item.data.shape_keys.key_blocks.find(object.active_shape_key.name)
        item.active_shape_key_index = index if index >= 0 else 0


# アクティブキーが同期していること
def sync_rename():
    object = bpy.context.object
    if object.type not in OBJECT_TYPES or object.mio3sksync.syncs is None:
        return None
    for item in object.mio3sksync.syncs.objects:
        if item.type not in OBJECT_TYPES or item.active_shape_key is None or item == object:
            continue
        if item.active_shape_key_index != 0:
            item.active_shape_key.name = object.active_shape_key.name


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
    prop_s = bpy.context.scene.mio3sk
    lr_suffix = lr_suffix_types.get(bpy.context.scene.mio3sk.xmirror_auto_suffix_type)
    if prop_s.xmirror_auto_enabled and bpy.context.active_object.mode == "EDIT":
        trim_l = bpy.context.object.active_shape_key.name[-lr_suffix[1] :]
        trim_r = bpy.context.object.active_shape_key.name[-lr_suffix[3] :]
        if trim_l == lr_suffix[0] or trim_r == lr_suffix[2]:
            bpy.context.object.data.use_mirror_x = False
        else:
            bpy.context.object.data.use_mirror_x = True

        for win in bpy.context.window_manager.windows:
            [area.tag_redraw() for area in win.screen.areas if area.type in {"VIEW_3D"}]
