import bpy
from bpy.types import Operator
from .define import *


class MIO3SK_OT_apply_to_basis(Operator):
    bl_idname = "mesh.mio3sk_apply_to_basis"
    bl_label = "apply to Basis(Selected Vertices)"
    bl_description = "apply to Basis(Selected Vertices)"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            context.object is not None
            and context.object.type in OBJECT_TYPES
            and context.object.mode == "EDIT"
        )

    def execute(self, context):
        mesh = context.object.data
        current_mode = context.object.mode
        current_index = bpy.context.object.active_shape_key_index
        shapekey_from = context.object.active_shape_key.name

        bpy.ops.object.mode_set(mode="EDIT")

        bpy.context.object.active_shape_key_index = 0
        bpy.ops.mesh.blend_from_shape(shape=shapekey_from, add=False)
        bpy.context.object.active_shape_key_index = current_index

        bpy.ops.object.mode_set(mode=current_mode)

        return {"FINISHED"}


classes = [MIO3SK_OT_apply_to_basis]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
