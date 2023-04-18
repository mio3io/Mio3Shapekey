import bpy
from bpy.types import Operator
from .define import *


def callback_move_active_shapekey():
    bpy.ops.mio3sk.move()


move_msgbus_owner = object()


class MIO3SK_OT_move_set_primary(Operator):
    bl_idname = "mio3sk.move_set_primary"
    bl_label = "Set Move"
    bl_description = "Set Move"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in OBJECT_TYPES

    def execute(self, context):
        object = context.object
        prop_s = context.scene.mio3sk
        prop_s.move_primary = object.active_shape_key.name
        bpy.msgbus.clear_by_owner(move_msgbus_owner)
        bpy.msgbus.subscribe_rna(
            key=(bpy.types.Object, "active_shape_key_index"),
            owner=move_msgbus_owner,
            args=(),
            notify=callback_move_active_shapekey,
        )
        return {"FINISHED"}


class MIO3SK_OT_move_remove_primary(Operator):
    bl_idname = "mio3sk.move_remove_primary"
    bl_label = "Set Move"
    bl_description = "Set Move"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in OBJECT_TYPES

    def execute(self, context):
        object = context.object
        prop_s = context.scene.mio3sk
        prop_s.move_primary = ""
        bpy.msgbus.clear_by_owner(move_msgbus_owner)
        return {"FINISHED"}



class MIO3SK_OT_move(Operator):
    bl_idname = "mio3sk.move"
    bl_label = "Move ShapeKeys"
    bl_description = "Move ShapeKeys"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in OBJECT_TYPES

    def execute(self, context):
        object = context.object
        prop_s = context.scene.mio3sk
        key_blocks = object.data.shape_keys.key_blocks
        primary_key = prop_s.move_primary
        secondary_key = object.active_shape_key.name

        if prop_s.move_active_type == "multi":
            base_idx = key_blocks.find(primary_key)
            move_idx = object.active_shape_key_index
        else:
            base_idx = object.active_shape_key_index
            move_idx = key_blocks.find(primary_key)

        object.active_shape_key_index = move_idx

        if base_idx > move_idx:
            [bpy.ops.object.shape_key_move(type="DOWN") for i in range(base_idx - move_idx)]
        elif base_idx < move_idx:
            [bpy.ops.object.shape_key_move(type="UP") for i in range(move_idx - base_idx - 1)]

        if prop_s.move_active_type == "multi":
            prop_s.move_primary = secondary_key
            if (len(key_blocks) > move_idx + 1):
                object.active_shape_key_index = move_idx + 1
        else:
            prop_s.move_active_single = False

        return {"FINISHED"}
