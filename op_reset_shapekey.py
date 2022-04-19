import bpy
from bpy.types import Operator
from .define import *


class MIO3SK_OT_reset(Operator):
    bl_idname = "mio3sk.reset"
    bl_label = "シェイプキーの形状をリセット"
    bl_description = "シェイプキーの形状をリセット"
    bl_options = {"REGISTER", "UNDO"}

    type: bpy.props.EnumProperty(
        default="all",
        items=[
            ("all", "All", ""),
            ("select", "Select", ""),
        ],
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in OBJECT_TYPES

    def execute(self, context):
        mesh = context.object.data
        shapekey = context.object.active_shape_key

        current_mode = bpy.context.active_object.mode

        bpy.ops.object.mode_set(mode="OBJECT")
        if self.type == "select":
          for i, el in enumerate(mesh.vertices):
            if el.select:
              shapekey.data[i].co = el.co
        else:
          for i, el in enumerate(mesh.vertices):
            shapekey.data[i].co = el.co

        mesh.update()

        bpy.ops.object.mode_set(mode=current_mode)

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)