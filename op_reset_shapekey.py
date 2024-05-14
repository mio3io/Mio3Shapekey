import bpy
from bpy.types import Operator
from .define import *


class MIO3SK_OT_reset(Operator):
    bl_idname = "mio3sk.reset"
    bl_label = "Reset ShapeKey"
    bl_description = "Reset ShapeKey"
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
        return (
            context.object is not None
            and context.object.data.shape_keys is not None
        )

    def execute(self, context):
        mesh = context.object.data
        shapekey = context.object.active_shape_key
        current_mode = context.object.mode

        if self.type == "select":
            bpy.ops.object.mode_set(mode="EDIT")
            basis = mesh.shape_keys.key_blocks[0]
            try:
                bpy.ops.mesh.blend_from_shape(shape=basis.name, blend=1.0, add=False)
            except Exception as e:
                self.report({'ERROR'}, str(e))
            
        else:
            bpy.ops.object.mode_set(mode="OBJECT")
            for i, el in enumerate(mesh.vertices):
                shapekey.data[i].co = el.co

        if context.object.mode != current_mode:
            bpy.ops.object.mode_set(mode=current_mode)

        return {"FINISHED"}

    def invoke(self, context, event):
        if self.type == "all":
            wm = context.window_manager
            return wm.invoke_confirm(self, event)
        else:
            return self.execute(context)


classes = [
    MIO3SK_OT_reset,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
