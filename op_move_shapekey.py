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

    mode: bpy.props.EnumProperty(
        default="set",
        items=[
            ("set", "set", ""),
            ("remove", "remove", ""),
        ],
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in OBJECT_TYPES

    def execute(self, context):
        prop_s = context.scene.mio3sk
        if self.mode == "remove":
            prop_s.move_primary = ""
            bpy.msgbus.clear_by_owner(move_msgbus_owner)
        else:
            prop_s.move_primary = bpy.context.object.active_shape_key.name
            bpy.msgbus.clear_by_owner(move_msgbus_owner)
            bpy.msgbus.subscribe_rna(
                key=(bpy.types.Object, "active_shape_key_index"),
                owner=move_msgbus_owner,
                args=(),
                notify=callback_move_active_shapekey,
            )
        return {"FINISHED"}


class MIO3SK_OT_move(Operator):
    bl_idname = "mio3sk.move"
    bl_label = "シェイプキーを移動"
    bl_description = "シェイプキーを移動"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in OBJECT_TYPES

    def execute(self, context):
        prop_s = context.scene.mio3sk
        key_blocks = bpy.context.object.data.shape_keys.key_blocks
        
        if prop_s.move_primary_auto:
            base_idx = key_blocks.find(prop_s.move_primary)
            target_idx = key_blocks.find(bpy.context.object.active_shape_key.name)
        else:
            base_idx = key_blocks.find(bpy.context.object.active_shape_key.name)
            target_idx = key_blocks.find(prop_s.move_primary)

        bpy.context.object.active_shape_key_index = target_idx

        if base_idx == target_idx:
            move = 0
        elif base_idx > target_idx:
            move = base_idx - target_idx
            for i in range(move):
                bpy.ops.object.shape_key_move(type="DOWN")
        else:
            move = abs(base_idx - target_idx) -1
            for i in range(abs(move)):
                bpy.ops.object.shape_key_move(type="UP")

        if prop_s.move_primary_auto:
            bpy.ops.mio3sk.move_set_primary(mode="set")

        if not prop_s.move_primary_auto:
            prop_s.move_active = False

        return {"FINISHED"}

