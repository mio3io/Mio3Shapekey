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
        obj = context.active_object
        return (
            obj is not None
            and obj.type in OBJECT_TYPES
            and obj.data.shape_keys is not None
            and obj.mode == "OBJECT"

        )

    def execute(self, context):
        obj = context.active_object
        key_blocks = obj.data.shape_keys.key_blocks

        for key in [el for el in key_blocks[1:] if not el.mute]:
            index = key_blocks.find(key.name)
            obj.active_shape_key_index = index
            bpy.ops.object.shape_key_remove(all=False)

        return {"FINISHED"}


classes = [
    MIO3SK_OT_remove_shapekey,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
