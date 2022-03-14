import bpy
from bpy.types import Panel, UIList

OBJECT_TYPES = {"MESH", "CURVE", "SURFACE", "LATTICE"}


class MIO3SS_PT_main(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    # bl_context = "objectmode"
    bl_label = "Mio3 ShapeKey Sync"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in OBJECT_TYPES

    def draw(self, context):
        layout = self.layout
        object = context.object
        row = layout.row()

        if object.data.shape_keys is None:
            return

        row.label(text="Sync Collection")

        row.prop(object.mio3sksync, "syncs", text="")

        collection_keys = []

        # コレクション設定済み
        if object.mio3sksync.syncs is not None:
            layout.template_list(
                "MIO3SS_UL_shape_keys",
                "",
                object.data.shape_keys,
                "key_blocks",
                object,
                "active_shape_key_index",
                rows=3,
            )

            for cobj in object.mio3sksync.syncs.objects:
                if cobj.type not in OBJECT_TYPES or cobj.active_shape_key is None:
                    continue
                for ckey in cobj.data.shape_keys.key_blocks:
                    collection_keys.append(ckey.name)

        # シェイプキー数
        row = layout.row()
        row.label(text="Local:" + str(len(object.data.shape_keys.key_blocks)))
        row.label(text="Collection:" + str(len(list(set(collection_keys)))))
        # コンテキストメニュー
        row.menu("MIO3SS_MT_context", icon="DOWNARROW_HLT", text="")


class MIO3SS_UL_shape_keys(UIList):
    def draw_item(
        self, _context, layout, _data, item, icon, active_data, _active_propname, index
    ):
        obj = active_data
        key_block = item
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            split = layout.split(factor=0.66, align=False)
            split.prop(key_block, "name", text="", emboss=False, icon_value=icon)
            row = split.row(align=True)
            row.emboss = "NONE_OR_STATUS"
            if key_block.mute or (
                obj.mode == "EDIT"
                and not (obj.use_shape_key_edit_mode and obj.type == "MESH")
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


class MIO3SS_MT_context(bpy.types.Menu):
    bl_idname = "MIO3SS_MT_context"
    bl_label = "Context Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator(
            "mio3ss.add_file", text=bpy.app.translations.pgettext("Add Import CSV")
        )
        layout.operator(
            "mio3ss.add_preset", text=bpy.app.translations.pgettext("Add VRChat Viseme")
        ).mode = "VRC_VISEME"
        layout.operator(
            "mio3ss.add_preset", text=bpy.app.translations.pgettext("Add MMD Lite")
        ).mode = "MMD_LIGHT"
        layout.operator(
            "mio3ss.add_preset", text=bpy.app.translations.pgettext("Add Perfect Sync")
        ).mode = "PERFECT_SYNC"
        layout.operator(
            "mio3ss.fill_keys", text=bpy.app.translations.pgettext("Fill Shapekeys")
        )
