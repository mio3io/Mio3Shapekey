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
        return context.object is not None and context.object.type in OBJECT_TYPES

    def execute(self, context):
        object = bpy.context.object
        prop_s = context.scene.mio3sk

        key_blocks = object.data.shape_keys.key_blocks
        target_keys = [k.name for k in key_blocks[1:]]

        if prop_s.sort_priority:
            target_keys = [key for key in target_keys if key[:3] != "vrc"]

        sorted_keys = (
            sorted(target_keys, key=str.lower)
            if self.type == "asc"
            else sorted(target_keys, key=str.lower, reverse=True)
        )

        current_key_name = object.active_shape_key.name

        for key in sorted_keys:
            idx = key_blocks.find(key)
            object.active_shape_key_index = idx
            bpy.ops.object.shape_key_move(type="BOTTOM")

        object.active_shape_key_index = key_blocks.find(current_key_name)

        return {"FINISHED"}
