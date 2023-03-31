import bpy
from bpy.types import Panel, UIList
from bpy.app.translations import pgettext
from .define import *
from .icons import *
from .op_util import *
from .op_sync_shapekey import *
from .op_add_shapekey import *
from .op_remove_shapekey import *
from .op_move_shapekey import *
from .op_sort_shapekey import *
from .op_reset_shapekey import *
from .op_rename_shapekey import *
from .op_propagate_shapekey import *


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

        row = layout.row()
        row.row().prop(
            prop_s,
            "move_active_single",
            text="Move active ShapeKey" if not prop_s.move_active_single else "Move below the key you clicked",
            icon_value=icons["MOVE"].icon_id,
        )
        row.enabled = context.object.mode == "OBJECT"

        row = layout.row()
        row.enabled = context.object.mode == "OBJECT"
        row.row().prop(
            prop_s,
            "move_active_multi",
            text="Move below active ShapeKey (Multiple)" if not prop_s.move_active_multi else "Click the keys in order to move",
            icon_value=icons["MOVE"].icon_id,
        )


class MIO3SK_PT_sub_sort(Panel):
    bl_label = "Sort"
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


class MIO3SK_PT_sub_rename(Panel):
    bl_label = "Rename (sync)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_parent_id = "MIO3SK_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.object.active_shape_key is not None

    def draw(self, context):
        prop_s = context.scene.mio3sk
        layout = self.layout

        layout.prop(context.object.active_shape_key, "name", text="Current Name", emboss=False)
        layout.prop(prop_s, "rename_inputname", text="New Name")
        layout.prop(prop_s, "rename_sync_collections", text="Change other sync objects")
        layout.operator(MIO3SK_OT_rename.bl_idname, text="Rename")


class MIO3SK_PT_sub_replace(Panel):
    bl_label = "Replace Names (sync)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_parent_id = "MIO3SK_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.object.active_shape_key is not None

    def draw(self, context):
        prop_s = context.scene.mio3sk
        layout = self.layout

        layout.separator()
        layout.prop(prop_s, "rename_search", text="Search")
        layout.prop(prop_s, "rename_replace", text="Replace")
        row = layout.row()
        row.prop(prop_s, "rename_regex", text="Use Regex")
        row.scale_x=0.5
        op = row.operator('wm.url_open', text=pgettext("Syntax"), icon="URL")
        op.url = "https://docs.python.org/3/library/re.html"
        layout.prop(prop_s, "rename_replace_sync_collections", text="Change other sync objects")
        layout.operator(MIO3SK_OT_replace.bl_idname, text="Replace")


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
        row.prop(prop_s, "sync_active_shapekey_enabled", text="Sync Active ShapeKey")
        row = layout.row()
        row.prop(prop_s, "xmirror_auto_enabled", text="Auto X Mirror Switching")


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

        layout.separator()
        layout.operator(
            MIO3SK_OT_propagate_to_basis.bl_idname,
            text=pgettext("Propagate to Basis(Selected Vertices)"),
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
