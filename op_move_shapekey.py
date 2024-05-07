import bpy
from bpy.types import Operator, Panel
from bpy.app.translations import pgettext
from .define import *
from .icons import *


def callback_move_active_shapekey():
    bpy.ops.mio3sk.move()


move_msgbus_owner = object()


class MIO3SK_OT_move_ex(Operator):
    bl_idname = "mio3sk.move_ex"
    bl_label = "シェイプキーを移動"
    bl_description = "10個づつ移動する"
    bl_options = {"REGISTER", "UNDO"}

    type: bpy.props.EnumProperty(
        default="UP",
        items=[
            ("UP", "UP", ""),
            ("DOWN", "DOWN", ""),
        ],
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.data.shape_keys is not None

    def execute(self, context):
        object = context.object

        if self.type == "UP":
            for i in range(10):
                if object.active_shape_key_index <= 1:
                    break
                bpy.ops.object.shape_key_move(type="UP")
        else:
            count = len(object.data.shape_keys.key_blocks)
            print(count)
            for i in range(10):
                if object.active_shape_key_index + 1 >= count:
                    break
                bpy.ops.object.shape_key_move(type="DOWN")

        return {"FINISHED"}


class MIO3SK_OT_move_set_primary(Operator):
    bl_idname = "mio3sk.move_set_primary"
    bl_label = "Set Move"
    bl_description = "Set Move"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.data.shape_keys is not None

    def execute(self, context):
        object = context.object
        prop_s = context.scene.mio3sk
        prop_s.move_primary = object.active_shape_key.name
        bpy.msgbus.clear_by_owner(move_msgbus_owner)
        bpy.msgbus.subscribe_rna(
            key=(bpy.types.Object, "active_shape_key_index"),
            owner=move_msgbus_owner,
            args=(),
            notify=callback_move_active_shapekey,
        )
        return {"FINISHED"}


class MIO3SK_OT_move_remove_primary(Operator):
    bl_idname = "mio3sk.move_remove_primary"
    bl_label = "Set Move"
    bl_description = "Set Move"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.data.shape_keys is not None

    def execute(self, context):
        object = context.object
        prop_s = context.scene.mio3sk
        prop_s.move_primary = ""
        bpy.msgbus.clear_by_owner(move_msgbus_owner)
        return {"FINISHED"}


class MIO3SK_OT_move(Operator):
    bl_idname = "mio3sk.move"
    bl_label = "Move ShapeKeys"
    bl_description = "Move ShapeKeys"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.data.shape_keys is not None

    def execute(self, context):
        object = context.object
        prop_s = context.scene.mio3sk
        key_blocks = object.data.shape_keys.key_blocks
        primary_key = prop_s.move_primary
        secondary_key = object.active_shape_key.name

        if prop_s.move_active_type == "multi":
            base_idx = key_blocks.find(primary_key)
            move_idx = object.active_shape_key_index
        else:
            base_idx = object.active_shape_key_index
            move_idx = key_blocks.find(primary_key)

        object.active_shape_key_index = move_idx

        if base_idx > move_idx:
            [bpy.ops.object.shape_key_move(type="DOWN") for i in range(base_idx - move_idx)]
        elif base_idx < move_idx:
            [bpy.ops.object.shape_key_move(type="UP") for i in range(move_idx - base_idx - 1)]

        if prop_s.move_active_type == "multi":
            prop_s.move_primary = secondary_key
            if len(key_blocks) > move_idx:
                object.active_shape_key_index = move_idx
        else:
            prop_s.move_active_single = False

        return {"FINISHED"}


class MIO3SK_PT_sub_move(Panel):
    bl_label = "Move"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_parent_id = "MIO3SK_PT_main"

    @classmethod
    def poll(cls, context):
        return context.object.active_shape_key is not None

    def draw(self, context):
        prop_s = context.scene.mio3sk
        layout = self.layout

        row = layout.row(align=True)

        row.operator(MIO3SK_OT_move_ex.bl_idname, icon_value=icons["UP_EX"].icon_id, text="10").type = "UP"
        row.operator("object.shape_key_move", icon="TRIA_UP", text="").type = "UP"
        row.operator("object.shape_key_move", icon="TRIA_DOWN", text="").type = "DOWN"
        row.operator(MIO3SK_OT_move_ex.bl_idname, icon_value=icons["DOWN_EX"].icon_id, text="10").type = "DOWN"

        row = layout.row()
        row.row().prop(
            prop_s,
            "move_active_single",
            text=(
                "Move active ShapeKey" if not prop_s.move_active_single else "Move below the key you clicked"
            ),
            icon_value=icons["MOVE"].icon_id,
        )
        row.enabled = context.object.mode == "OBJECT"

        row = layout.row()
        row.enabled = context.object.mode == "OBJECT"
        row.row().prop(
            prop_s,
            "move_active_multi",
            text=(
                "Move below active ShapeKey (Multiple)"
                if not prop_s.move_active_multi
                else "Click the keys in order to move"
            ),
            icon_value=icons["MOVE"].icon_id,
        )
