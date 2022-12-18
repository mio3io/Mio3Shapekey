import bpy
from bpy.types import Operator
from .define import *
from .op_util import *


class MIO3SK_OT_remove_shapekey(Operator):
    bl_idname = "mio3sk.remove_shapekey"
    bl_label = "Remove"
    bl_description = "Remove"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return (
            context.object is not None
            and context.object.type in OBJECT_TYPES
            and context.object.mode == "OBJECT"
            and context.object.active_shape_key is not None
        )

    def execute(self, context):
        object = context.object
        key_blocks = object.data.shape_keys.key_blocks

        for key in [el.name for el in key_blocks[1:] if not el.mute]:
            index = key_blocks.find(key)
            object.active_shape_key_index = index
            bpy.ops.object.shape_key_remove(all=False)

        return {"FINISHED"}
