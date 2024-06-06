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
        obj = context.active_object
        return (
            obj is not None
            and obj.type in OBJECT_TYPES
            and obj.mode == "EDIT"
            and obj.data.shape_keys is not None
        )

    def execute(self, context):
        obj = context.active_object
        original_index = obj.active_shape_key_index
        shapekey_from = obj.active_shape_key.name

        obj.active_shape_key_index = 0
        try:
            bpy.ops.mesh.blend_from_shape(shape=shapekey_from, add=False)
        except Exception as e:
            self.report({"ERROR"}, str(e))
        obj.active_shape_key_index = original_index

        return {"FINISHED"}


classes = [MIO3SK_OT_apply_to_basis]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
