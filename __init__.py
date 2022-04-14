import bpy
from bpy.types import PropertyGroup
from bpy.app.handlers import persistent

from .dictionary import *
from .panel import *
from .op_add_shapekey import *

bl_info = {
    "name": "Mio3 ShapeKeySync",
    "author": "mio3io",
    "version": (2, 2, 0),
    "blender": (3, 0, 0),
    "warning": "",
    "location": "View3D > Sidebar",
    "description": "Synchronize shape keys with the same name in the certain collection.",
    "category": "Object",
}


class MIO3SK_props(bpy.types.PropertyGroup):
    syncs: bpy.props.PointerProperty(
        name=bpy.app.translations.pgettext("Sync Collection"), type=bpy.types.Collection
    )


def callback_update_shapekey():
    sync_shapekey_value()


msgbus_owner = object()


def register_msgbus():
    bpy.msgbus.clear_by_owner(msgbus_owner)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.ShapeKey, "value"),
        owner=msgbus_owner,
        args=(),
        notify=callback_update_shapekey,
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.ShapeKey, "mute"),
        owner=msgbus_owner,
        args=(),
        notify=callback_update_shapekey,
    )
    if load_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_handler)


@persistent
def load_handler(scene):
    register_msgbus()


classes = [
    MIO3SK_props,
    MIO3SK_PT_main,
    MIO3SK_MT_context,
    MIO3SK_UL_shape_keys,
    MIO3SK_OT_some_file,
    MIO3SK_OT_add_preset,
    MIO3SK_OT_fill_keys,
]


def register():
    register_translations(__name__)
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Object.mio3sksync = bpy.props.PointerProperty(type=MIO3SK_props)
    register_msgbus()


def unregister():
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.msgbus.clear_by_owner(msgbus_owner)
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.Object.mio3sksync
    remove_translations(__name__)


if __name__ == "__main__":
    register()
