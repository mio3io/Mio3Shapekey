import bpy
from bpy.types import PropertyGroup, PointerProperty, Collection, Object, Scene
from bpy.props import PointerProperty
from bpy.app.handlers import persistent

from .Dict import *
from .UI import *
from .ShapekeySync import *
from .AddShapekey import MIO3SS_OT_SomeFile, MIO3SS_OT_AddPresets, MIO3SS_OT_FillKeys

bl_info = {
    "name": "Mio3 ShapeKeySync",
    "author": "mio3io",
    "version": (2, 1, 1),
    "blender": (3, 0, 0),
    "warning": "",
    "location": "View3D > Sidebar",
    "description": "Synchronize shape keys with the same name in the certain collection.",
    "category": "Object",
}


class MIO3SS_Props(PropertyGroup):
    syncs: PointerProperty(
        name=bpy.app.translations.pgettext("Sync Collection"), type=Collection
    )


msgbus_owner = None


def register_msgbus():
    global msgbus_owner

    msgbus_owner = object()
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


@persistent
def msgbu_handler(scene):
    register_msgbus()


classes = [
    MIO3SS_Props,
    MIO3SS_MT_Context,
    MIO3SS_UL_Mio3sksync,
    MIO3SS_PT_Mio3sksync,
    MIO3SS_OT_SomeFile,
    MIO3SS_OT_AddPresets,
    MIO3SS_OT_FillKeys,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    Object.mio3sksync = PointerProperty(type=MIO3SS_Props)
    bpy.app.handlers.load_post.append(msgbu_handler)
    bpy.app.translations.register(__name__, translation_dict)
    if msgbus_owner is None:
        register_msgbus()


def unregister():
    global msgbus_owner

    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.app.handlers.load_post.remove(msgbu_handler)
    bpy.app.translations.unregister(__name__)
    if msgbus_owner is not None:
        bpy.msgbus.clear_by_owner(msgbus_owner)
        msgbus_owner = None
    del Object.mio3sksync


if __name__ == "__main__":
    register()
