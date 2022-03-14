import bpy
from bpy.types import PropertyGroup, PointerProperty, Collection, Object
from bpy.props import PointerProperty
from bpy.app.handlers import persistent

from .dictionary import *
from .panel import *
from .fn_sync_shapekey import *
from .op_add_shapekey import MIO3SS_OT_some_file, MIO3SS_OT_add_preset, MIO3SS_OT_fill_keys

bl_info = {
    "name": "Mio3 ShapeKeySync",
    "author": "mio3io",
    "version": (2, 1, 2),
    "blender": (3, 0, 0),
    "warning": "",
    "location": "View3D > Sidebar",
    "description": "Synchronize shape keys with the same name in the certain collection.",
    "category": "Object",
}


class MIO3SS_props(PropertyGroup):
    syncs: PointerProperty(
        name=bpy.app.translations.pgettext("Sync Collection"), type=Collection
    )


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
    MIO3SS_props,
    MIO3SS_MT_context,
    MIO3SS_UL_shape_keys,
    MIO3SS_PT_main,
    MIO3SS_OT_some_file,
    MIO3SS_OT_add_preset,
    MIO3SS_OT_fill_keys,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    Object.mio3sksync = PointerProperty(type=MIO3SS_props)
    bpy.app.translations.register(__name__, translation_dict)
    register_msgbus()


def unregister():
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.msgbus.clear_by_owner(msgbus_owner)
    bpy.app.translations.unregister(__name__)
    for c in classes:
        bpy.utils.unregister_class(c)
    del Object.mio3sksync


if __name__ == "__main__":
    register()
