import bpy
from bpy.types import Operator, Panel
from bpy.app.translations import pgettext
from .define import *


class MIO3SK_OT_sort(Operator):
    bl_idname = "mio3sk.sort"
    bl_label = "Sort"
    bl_description = "Sort by ShapeKey Name"
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
        obj = context.active_object
        return (
            obj is not None
            and obj.type in OBJECT_TYPES
            and obj.data.shape_keys is not None
            and obj.mode == "OBJECT"
        )

    def execute(self, context):
        obj = context.active_object
        prop_s = context.scene.mio3sk

        key_blocks = obj.data.shape_keys.key_blocks
        target_blocks = key_blocks[1:]

        # ToDo 除外方法をリスト方式に変更する
        if prop_s.sort_priority:
            target_blocks = [key for key in target_blocks if key.name[:3] != "vrc"]
        if prop_s.sort_priority_mute:
            target_blocks = [key for key in target_blocks if key.mute == False]

        target_blocks = [k.name for k in target_blocks]

        sorted_keys = (
            sorted(target_blocks, key=str.lower)
            if self.type == "asc"
            else sorted(target_blocks, key=str.lower, reverse=True)
        )

        current_key_name = obj.active_shape_key.name

        for key in sorted_keys:
            idx = key_blocks.find(key)
            obj.active_shape_key_index = idx
            bpy.ops.object.shape_key_move(type="BOTTOM")

        obj.active_shape_key_index = key_blocks.find(current_key_name)

        return {"FINISHED"}


class MIO3SK_PT_sub_sort(Panel):
    bl_label = "Sort"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_parent_id = "MIO3SK_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.active_object.data.shape_keys is not None

    def draw(self, context):
        prop_s = context.scene.mio3sk
        layout = self.layout

        row = layout.row()
        row.label(text="Sort by ShapeKey Name")

        row = layout.row(align=True)
        row.operator(
            MIO3SK_OT_sort.bl_idname,
            text=pgettext("ASC"),
        ).type = "asc"
        row.operator(
            MIO3SK_OT_sort.bl_idname,
            text=pgettext("DESC"),
        ).type = "desc"

        layout.row().prop(prop_s, "sort_priority", text="Pinned vrc.* keys")
        layout.row().prop(prop_s, "sort_priority_mute", text="Pinned Mute keys")


classes = [
    MIO3SK_PT_sub_sort,
    MIO3SK_OT_sort,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
