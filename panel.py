import bpy
from bpy.types import Panel, UIList
from bpy.app.translations import pgettext
from .define import *
from .op_add_shapekey import *
from .op_util import *


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
            for cobj in prop_o.syncs.objects:
                if cobj.type not in OBJECT_TYPES or cobj.active_shape_key is None:
                    continue
                for ckey in cobj.data.shape_keys.key_blocks:
                    collection_keys.append(ckey.name)

        # シェイプキー数
        row = layout.row()
        row.label(text="Local:" + str(len(shape_keys.key_blocks)))
        row.label(text="Collection:" + str(len(list(set(collection_keys)))))
        # コンテキストメニュー
        row.menu("MIO3SK_MT_context", icon="DOWNARROW_HLT", text="")


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
        object = context.object
        layout = self.layout
        row = layout.row()
        row.prop(prop_s, "sync_active_shapekey_enabled", text="アクティブキーと名前を同期")
        row = layout.row()
        row.prop(prop_s, "xmirror_auto_enabled", text="Xミラー編集の自動切り替え")
        row = layout.row()
        row.label(text="L/R接尾辞タイプ")
        row.prop(prop_s, "xmirror_auto_suffix_type", text="")


class MIO3SK_UL_shape_keys(UIList):
    def draw_item(self, _context, layout, _data, item, icon, active_data, _active_propname, index):
        obj = active_data
        key_block = item
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            split = layout.split(factor=0.66, align=False)
            split.prop(key_block, "name", text="", emboss=False, icon_value=icon)
            row = split.row(align=True)
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
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class MIO3SK_MT_context(bpy.types.Menu):
    bl_idname = "MIO3SK_MT_context"
    bl_label = "Context Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator(
            MIO3SK_OT_some_file.bl_idname,
            text=pgettext("Add: Import CSV"),
        )
        layout.operator(
            MIO3SK_OT_add_preset.bl_idname,
            text=pgettext("Add: VRChat Viseme"),
        ).mode = "vrc_viseme"
        layout.operator(
            MIO3SK_OT_add_preset.bl_idname,
            text=pgettext("Add: MMD Lite"),
        ).mode = "mmd_light"
        layout.operator(
            MIO3SK_OT_add_preset.bl_idname,
            text=pgettext("Add: Perfect Sync"),
        ).mode = "perfect_sync"
        layout.operator(
            MIO3SK_OT_fill_keys.bl_idname,
            text=pgettext("Fill Shapekeys"),
        )