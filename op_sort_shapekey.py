import bpy
from bpy.types import Operator
from .define import *


class MIO3SK_OT_sort(Operator):
    bl_idname = "mio3sk.sort"
    bl_label = "Sort"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    type: bpy.props.EnumProperty(
        default="asc",
        items=[
            ("asc", "昇順", ""),
            ("desc", "降順", ""),
        ],
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in OBJECT_TYPES and context.object.mode == "OBJECT"

    def execute(self, context):
        object = context.object
        prop_s = context.scene.mio3sk

        key_blocks = object.data.shape_keys.key_blocks
        target_blocks = key_blocks[1:]

        # ToDo 除外方法をリスト方式に変更する
        if prop_s.sort_priority:
            target_blocks = [key for key in target_blocks if key.name[:1] != "_" and key.name[:4] != "vrc." and key.name[:5] != "body_"]
        if prop_s.sort_priority_mute:
            target_blocks = [key for key in target_blocks if key.mute == False]

        target_blocks = [k.name for k in target_blocks]

        sorted_keys = (
            sorted(target_blocks, key=str.lower)
            if self.type == "asc"
            else sorted(target_blocks, key=str.lower, reverse=True)
        )

        current_key_name = object.active_shape_key.name

        for key in sorted_keys:
            idx = key_blocks.find(key)
            object.active_shape_key_index = idx
            bpy.ops.object.shape_key_move(type="BOTTOM")

        object.active_shape_key_index = key_blocks.find(current_key_name)

        return {"FINISHED"}
