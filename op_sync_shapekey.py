import bpy
from bpy.app.handlers import persistent
from .define import *
from .op_util import *


def sync_shapekey_value():
    context = bpy.context
    obj = context.active_object

    if not (obj and obj.data.shape_keys and is_sync_collection(obj)):
        return

    prop_o = obj.mio3sksync
    source_key_blocks = obj.data.shape_keys.key_blocks

    for m_obj in prop_o.syncs.objects:
        if m_obj == obj or not has_shapekey(m_obj):
            continue

        target_key_blocks = m_obj.data.shape_keys.key_blocks
        for target_key in target_key_blocks:
            if target_key.name in source_key_blocks:
                if target_key.value != source_key_blocks[target_key.name].value:
                    target_key.value = source_key_blocks[target_key.name].value


def sync_shapekey_mute():
    context = bpy.context
    obj = context.active_object

    if not (obj and obj.data.shape_keys and is_sync_collection(obj)):
        return

    prop_o = obj.mio3sksync
    source_key_blocks = obj.data.shape_keys.key_blocks

    for m_obj in prop_o.syncs.objects:
        if m_obj == obj or not has_shapekey(m_obj):
            continue

        target_key_blocks = m_obj.data.shape_keys.key_blocks
        for target_key in target_key_blocks:
            if target_key.name in source_key_blocks:
                if target_key.mute != source_key_blocks[target_key.name].mute:
                    target_key.mute = source_key_blocks[target_key.name].mute


def sync_show_only_shape_key():
    context = bpy.context
    obj = context.active_object

    if not (obj and obj.data.shape_keys and is_sync_collection(obj)):
        return

    prop_o = obj.mio3sksync

    for m_obj in prop_o.syncs.objects:
        if m_obj == obj or not has_shapekey(m_obj):
            continue
        if m_obj.show_only_shape_key != obj.show_only_shape_key:
            m_obj.show_only_shape_key = obj.show_only_shape_key


def sync_active_shape_key():
    context = bpy.context
    obj = context.active_object

    if not (obj and obj.data.shape_keys and is_sync_collection(obj)):
        return

    prop_s = context.scene.mio3sk
    if not prop_s.sync_active_shapekey_enabled:
        return

    prop_o = obj.mio3sksync

    for m_obj in prop_o.syncs.objects:
        if m_obj == obj or not has_shapekey(m_obj):
            continue
        index = m_obj.data.shape_keys.key_blocks.find(obj.active_shape_key.name)
        m_obj.active_shape_key_index = index if index >= 0 else 0


msgbus_owner = object()


def register_msgbus():
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
        notify=sync_shapekey_mute,
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "show_only_shape_key"),
        owner=msgbus_owner,
        args=(),
        notify=sync_show_only_shape_key,
    )

    if load_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_handler)


@persistent
def load_handler(scene):
    register_msgbus()


def register():
    register_msgbus()


def unregister():
    bpy.msgbus.clear_by_owner(msgbus_owner)
    bpy.app.handlers.load_post.remove(load_handler)
