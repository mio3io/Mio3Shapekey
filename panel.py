from cgitb import enable
import bpy
from bpy.types import Panel, UIList
from bpy.app.translations import pgettext
from .define import *
from .icons import *
from .op_util import *
from .op_sync_shapekey import *
from .op_add_shapekey import *
from .op_move_shapekey import *
from .op_sort_shapekey import *
from .op_reset_shapekey import *
from .op_remove_shapekey import *


class MIO3SK_PT_main(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_label = "Mio3 ShapeKey"

    @classmethod
    def poll(cls, context):
        return (
            context.object is not None
            and context.object.type in OBJECT_TYPES
            and context.object.active_shape_key is not None
        )

    def draw(self, context):
        prop_o = context.object.mio3sksync
        object = context.object
        shape_keys = object.data.shape_keys

        layout = self.layout

        row = layout.row(align=True)
        row.label(text="Sync Collection")
        row.prop(prop_o, "syncs", text="")

        collection_keys = []

        layout.template_list(
            "MIO3SK_UL_shape_keys",
            "",
            shape_keys,
            "key_blocks",
            object,
            "active_shape_key_index",
            rows=3,
        )

        if prop_o.syncs is not None:
            for cobj in [o for o in prop_o.syncs.objects if has_shapekey(o)]:
                for ckey in cobj.data.shape_keys.key_blocks:
                    collection_keys.append(ckey.name)

        # シェイプキー数
        row = layout.row()
        row.label(text="Local:" + str(len(shape_keys.key_blocks)))
        row.label(text="Collection:" + str(len(list(set(collection_keys)))))
        # コンテキストメニュー
        row.menu("MIO3SK_MT_context", icon="DOWNARROW_HLT", text="")

        row = layout.row(align=True)
        row.scale_x = 1.8
        row.label(text="形状をリセット")
        row.scale_x = 1
        row.operator(MIO3SK_OT_reset.bl_idname, text="全て").type = "all"
        row.operator(MIO3SK_OT_reset.bl_idname, text="選択").type = "select"


class MIO3SK_PT_sub_move(Panel):
    bl_label = "移動"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_parent_id = "MIO3SK_PT_main"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        prop_s = context.scene.mio3sk
        layout = self.layout

        layout.row().prop(
            prop_s,
            "move_active_single",
            text="選択中のキーを移動" if not prop_s.move_active_single else "クリックしたキーの下に移動",
            icon_value=icons["MOVE"].icon_id,
        )

        layout.row().prop(
            prop_s,
            "move_active_multi",
            text=" 選択中のキーの下に複数移動" if not prop_s.move_active_multi else "移動するキーを順番にクリック",
            icon_value=icons["MOVE"].icon_id,
        )


class MIO3SK_PT_sub_sort(Panel):
    bl_label = "ソート"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_parent_id = "MIO3SK_PT_main"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        prop_s = context.scene.mio3sk
        layout = self.layout

        row = layout.row()
        row.label(text="名前でソート")

        row = layout.row(align=True)
        row.operator(
            MIO3SK_OT_sort.bl_idname,
            text=pgettext("昇順"),
        ).type = "asc"
        row.operator(
            MIO3SK_OT_sort.bl_idname,
            text=pgettext("降順"),
        ).type = "desc"

        layout.row().prop(prop_s, "sort_priority", text="vrc* をトップに維持する")
        layout.row().prop(prop_s, "sort_priority_mute", text="無効化中のキーをトップに維持する")


class MIO3SK_PT_sub_options(Panel):
    bl_label = "Options"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_parent_id = "MIO3SK_PT_main"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        prop_s = context.scene.mio3sk
        layout = self.layout
        row = layout.row()
        row.prop(prop_s, "sync_active_shapekey_enabled", text="選択を同期")
        row = layout.row()
        row.prop(prop_s, "xmirror_auto_enabled", text="Xミラー編集の自動切り替え")
        row = layout.row()
        row.label(text="L/R接尾辞タイプ")
        row.prop(prop_s, "xmirror_auto_suffix_type", text="")


class MIO3SK_UL_shape_keys(UIList):
    def draw_item(self, context, layout, _data, item, icon, active_data, _active_propname, index):
        obj = active_data
        key_block = item
        prop_s = context.scene.mio3sk
        prop_o = context.object.mio3sksync

        micon = icons["DEFAULT"].icon_id
        if prop_s.move_primary:
            if prop_s.move_active_type == "multi":
                if prop_s.move_primary == key_block.name:
                    micon = icons["PRIMARY"].icon_id
            else:
                if prop_s.move_primary == key_block.name:
                    micon = icons["MOVE"].icon_id

        split = layout.split(factor=0.68, align=False)
        split.prop(key_block, "name", text="", emboss=False, icon_value=micon)
        row = split.row(align=False)
        row.emboss = "NONE_OR_STATUS"
        if key_block.mute or (
            obj.mode == "EDIT" and not (obj.use_shape_key_edit_mode and obj.type == "MESH")
        ):
            row.active = False
        if not item.id_data.use_relative:
            row.prop(key_block, "frame", text="")
        elif index > 0:
            row.prop(key_block, "value", text="")
        else:
            row.label(text="")
        row.prop(key_block, "mute", text="", emboss=False)


class MIO3SK_MT_context(bpy.types.Menu):
    bl_idname = "MIO3SK_MT_context"
    bl_label = "Context Menu"

    def draw(self, context):
        layout = self.layout

        layout.operator(
            MIO3SK_OT_sort.bl_idname,
            text=pgettext("名前でソート（昇順）"),
        ).type = "asc"
        layout.operator(
            MIO3SK_OT_sort.bl_idname,
            text=pgettext("名前でソート（降順）"),
        ).type = "desc"

        layout.separator()
        layout.operator(
            MIO3SK_OT_remove_shapekey.bl_idname,
            text=pgettext("無効化を除くシェイプキーを削除"),
        )

        layout.separator()
        layout.operator(
            MIO3SK_OT_add_preset.bl_idname,
            text=pgettext("Add: VRChat Viseme"),
        ).type = "vrc_viseme"
        layout.operator(
            MIO3SK_OT_add_preset.bl_idname,
            text=pgettext("Add: MMD Lite"),
        ).type = "mmd_light"
        layout.operator(
            MIO3SK_OT_add_preset.bl_idname,
            text=pgettext("Add: Perfect Sync"),
        ).type = "perfect_sync"
        layout.operator(
            MIO3SK_OT_some_file.bl_idname,
            text=pgettext("Add: Import CSV"),
        )

        layout.separator()
        layout.operator(
            MIO3SK_OT_fill_keys.bl_idname,
            text=pgettext("Fill Shapekeys"),
        )
