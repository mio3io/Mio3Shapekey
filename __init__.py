import bpy
from bpy.types import Panel, PropertyGroup, PointerProperty, UIList, Collection, Object
from bpy.props import PointerProperty
from bpy.app.handlers import persistent

bl_info = {
    "name": "Mio3 ShapeKeySync",
    "author": "mio3io",
    "version": (2, 0, 0),
    "blender": (3, 0, 0),
    "warning": "",
    "location": "View3D > Sidebar",
    "description": "Synchronize shape keys with the same name in the certain collection.",
    "category": "Object",
}


class MESH_UL_Mio3sksync(UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):

        obj = active_data
        key_block = item

        split = layout.split(factor=0.66, align=False)
        split.prop(key_block, "name", text="", emboss=False, icon_value=icon)
        row = split.row(align=True)
        row.emboss = "NONE"

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


class VIEW3D_PT_Mio3sksync(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    # bl_context = "objectmode"
    bl_label = "Mio3 ShapeKey Sync"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in {
            "MESH",
            "CURVE",
            "SURFACE",
            "LATTICE",
            "SURFACE",
        }

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Sync Collection")

        if context.object.data.shape_keys:

            row.prop(context.object.mio3sksync, "syncs", text="")

            collection_keys = []

            # コレクション設定済み
            if context.object.mio3sksync.syncs:
                dat = context.object.data
                layout.template_list(
                    "MESH_UL_Mio3sksync",
                    "",
                    context.object.data.shape_keys,
                    "key_blocks",
                    context.object,
                    "active_shape_key_index",
                    rows=3,
                )

                for cobj in context.object.mio3sksync.syncs.objects:
                    if (
                        hasattr(cobj.data, "shape_keys")
                        and cobj.active_shape_key is not None
                    ):
                        for ckey in cobj.data.shape_keys.key_blocks:
                            collection_keys.append(ckey.name)

            row = layout.row()
            row.label(
                text="Local:" + str(len(context.object.data.shape_keys.key_blocks))
            )
            row.label(text="Collection:" + str(len(list(set(collection_keys)))))


def callback_update_shapekey():
    context = bpy.context
    if context.object.data.shape_keys:
        if context.object.mio3sksync.syncs:
            dat = context.object.data
            for cobj in context.object.mio3sksync.syncs.objects:
                if (
                    hasattr(cobj.data, "shape_keys")
                    and cobj.active_shape_key is not None
                ):
                    for ckey in cobj.data.shape_keys.key_blocks:
                        if cobj != context.object:
                            if (
                                ckey.name in dat.shape_keys.key_blocks
                                and ckey.value
                                != dat.shape_keys.key_blocks[ckey.name].value
                            ):
                                ckey.value = dat.shape_keys.key_blocks[ckey.name].value


class MIO3SKSYNC_Props(PropertyGroup):
    syncs: PointerProperty(
        name=bpy.app.translations.pgettext("shapekey sync collection"), type=Collection
    )


classes = [MIO3SKSYNC_Props, MESH_UL_Mio3sksync, VIEW3D_PT_Mio3sksync]


def register_subscribe_rna():
    bpy.types.Scene.msgbus_owner = object()
    subscribe_to = (bpy.types.ShapeKey, "value")
    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        owner=bpy.types.Scene.msgbus_owner,
        args=(),
        notify=callback_update_shapekey,
    )


@persistent
def handler_subscribe(scene):
    register_subscribe_rna()


def register():
    for c in classes:
        bpy.utils.register_class(c)
    Object.mio3sksync = PointerProperty(type=MIO3SKSYNC_Props)
    bpy.app.handlers.load_post.append(handler_subscribe)
    if hasattr(bpy.types.Scene, "msgbus_owner") == False:
        register_subscribe_rna()


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.app.handlers.load_post.remove(handler_subscribe)
    if hasattr(bpy.types.Scene, "msgbus_owner") == True:
        bpy.msgbus.clear_by_owner(bpy.types.Scene.msgbus_owner)
        del bpy.types.Scene.msgbus_owner
    del Object.mio3sksync


if __name__ == "__main__":
    register()
