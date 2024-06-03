import bpy
from bpy.types import Panel, UIList
from bpy.app.translations import pgettext
from .define import *
from .op_util import *
from .icons import preview_collections
from .op_add_shapekey import MIO3SK_OT_add_key_current, MIO3SK_OT_add_preset, MIO3SK_OT_some_file, MIO3SK_OT_fill_keys
from .op_remove_shapekey import MIO3SK_OT_remove_shapekey
from .op_sort_shapekey import MIO3SK_OT_sort
from .op_reset_shapekey import MIO3SK_OT_reset
from .op_apply_shapekey import MIO3SK_OT_apply_to_basis

class MIO3SK_PT_main(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_label = "Mio3 ShapeKey"

    @classmethod
    def poll(cls, context):
        return (
            context.object is not None
            and context.object.type in OBJECT_TYPES
        )

    def draw(self, context):
        prop_o = context.object.mio3sksync
        object = context.object
        shape_keys = object.data.shape_keys

        layout = self.layout

        # 同期コレクション
        row = layout.row()
        row.label(text="Sync Collection")
        row.prop(prop_o, "syncs", text="")

        # コンテキストメニュー
        row.menu("MIO3SK_MT_context", icon="DOWNARROW_HLT", text="")


        row = layout.row()

        # シェイプキーリスト
        row.template_list(
            "MIO3SK_UL_shape_keys",
            "",
            shape_keys,
            "key_blocks",
            object,
            "active_shape_key_index",
            rows=5,
        )
        col = row.column(align=True)

        col.operator("object.shape_key_add", icon='ADD', text="").from_mix = False
        col.operator(MIO3SK_OT_add_key_current.bl_idname, icon='PLUS', text="")
        col.operator("object.shape_key_remove", icon='REMOVE', text="").all = False

        col.separator()

        col.menu("MESH_MT_shape_key_context_menu", icon='DOWNARROW_HLT', text="")

        if context.object.active_shape_key:
            col.separator()

            sub = col.column(align=True)
            sub.operator("object.shape_key_move", icon='TRIA_UP', text="").type = 'UP'
            sub.operator("object.shape_key_move", icon='TRIA_DOWN', text="").type = 'DOWN'

            row = layout.row()

            # シェイプキー数表示
            collection_keys = []
            if prop_o.syncs is not None:
                for cobj in [o for o in prop_o.syncs.objects if has_shapekey(o)]:
                    for ckey in cobj.data.shape_keys.key_blocks:
                        collection_keys.append(ckey.name)
            # シェイプキー数
            row.label(text="Local:" + str(len(shape_keys.key_blocks)))
            row.label(text="Collection:" + str(len(list(set(collection_keys)))))

            row.alignment = 'RIGHT'
            sub = row.row(align=True)
            sub.prop(object, "show_only_shape_key", text="")
            sub.prop(object, "use_shape_key_edit_mode", text="")

            sub = row.row()
            if shape_keys.use_relative:
                sub.operator("object.shape_key_clear", icon='X', text="")
            else:
                sub.operator("object.shape_key_retime", icon='RECOVER_LAST', text="")

            layout.separator()

            row = layout.row(align=True)
            row.scale_x = 1.2
            row.label(text="Reset Shape")
            row.scale_x = 1
            row.operator(MIO3SK_OT_reset.bl_idname, text=pgettext("All Vertices")).type = "all"
            row.operator(MIO3SK_OT_reset.bl_idname, text=pgettext("Active Vertices")).type = "select"


class MIO3SK_UL_shape_keys(UIList):
    def draw_item(self, context, layout, _data, item, icon, active_data, _active_propname, index):
        icons = preview_collections["icons"]
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

        layout.separator()
        layout.operator(
            MIO3SK_OT_apply_to_basis.bl_idname,
            text=pgettext("Apply to Basis(Selected Vertices)"),
        )
        layout.separator()

        layout.operator(
            MIO3SK_OT_sort.bl_idname,
            text=pgettext("Sort ASC"),
        ).type = "asc"
        layout.operator(
            MIO3SK_OT_sort.bl_idname,
            text=pgettext("Sort DESC"),
        ).type = "desc"

        layout.separator()
        layout.operator(
            MIO3SK_OT_remove_shapekey.bl_idname,
            text=pgettext("Delete shape key except disable"),
        )

        layout.separator()
        layout.operator(
            MIO3SK_OT_add_key_current.bl_idname,
            text=pgettext("Add: Shape Key at current position"),
        )
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


classes = [
    MIO3SK_PT_main,
    MIO3SK_MT_context,
    MIO3SK_UL_shape_keys,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
