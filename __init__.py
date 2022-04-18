import bpy
from bpy.types import PropertyGroup
from bpy.app.handlers import persistent

from .dictionary import *
from .icons import *
from .panel import *
from .op_add_shapekey import *
from .op_move_shapekey import *

bl_info = {
    "name": "Mio3 ShapeKeySync",
    "author": "mio3io",
    "version": (2, 3, 0),
    "blender": (3, 0, 0),
    "warning": "",
    "location": "View3D > Sidebar",
    "description": "Synchronize shape keys with the same name in the certain collection.",
    "category": "Object",
}


def callback_sync_active_shapekey_enabled(self, context):
    if self.sync_active_shapekey_enabled:
        register_active_shape_key()
        sync_active_shape_key()
    else:
        unregister_active_shape_key()


def callback_xmirror_auto_enabled(self, context):
    if self.xmirror_auto_enabled:
        register_auto_active_mirror_edit()
    else:
        unregister_auto_active_mirror_edit()


def callback_move_active(self, context):
    bpy.ops.mio3sk.move_set_primary(mode="set" if self.move_active else "remove")

class MIO3SK_scene_props(PropertyGroup):
    sync_active_shapekey_enabled: bpy.props.BoolProperty(
        default=False, update=callback_sync_active_shapekey_enabled
    )
    xmirror_auto_enabled: bpy.props.BoolProperty(default=False, update=callback_xmirror_auto_enabled)
    xmirror_auto_suffix_type: bpy.props.EnumProperty(
        default="_head",
        items=[(k, f"{l} / {r}", "") for (k, l, r) in lr_suffix_types_source],
    )

    move_active: bpy.props.BoolProperty(update=callback_move_active)
    move_primary: bpy.props.StringProperty()
    move_primary_auto: bpy.props.BoolProperty()

class MIO3SK_props(bpy.types.PropertyGroup):
    syncs: bpy.props.PointerProperty(
        name=bpy.app.translations.pgettext("Sync Collection"), type=bpy.types.Collection
    )


def callback_update_shapekey():
    sync_shapekey_value()


def callback_rename_shapekey():
    pass


def callback_active_shapekey():
    pass


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

    if hasattr(bpy.context, "scene"):
        prop_s = bpy.context.scene.mio3sk
        if prop_s.xmirror_auto_enabled:
            register_auto_active_mirror_edit()
        if prop_s.sync_active_shapekey_enabled:
            register_active_shape_key()
    else:
        # Default=True
        # register_auto_active_mirror_edit()
        # register_active_shape_key()
        pass


@persistent
def load_handler(scene):
    register_msgbus()


classes = [
    MIO3SK_scene_props,
    MIO3SK_props,
    MIO3SK_PT_main,
    MIO3SK_PT_sub_move,
    MIO3SK_PT_sub_options,
    MIO3SK_MT_context,
    MIO3SK_UL_shape_keys,
    MIO3SK_OT_some_file,
    MIO3SK_OT_add_preset,
    MIO3SK_OT_fill_keys,
    MIO3SK_OT_move_set_primary,
    MIO3SK_OT_move,
]


def register():
    register_translations(__name__)
    register_icons()
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.mio3sk = bpy.props.PointerProperty(type=MIO3SK_scene_props)
    bpy.types.Object.mio3sksync = bpy.props.PointerProperty(type=MIO3SK_props)
    register_msgbus()


def unregister():
    bpy.app.handlers.load_post.remove(load_handler)
    unregister_active_shape_key()
    unregister_auto_active_mirror_edit()
    bpy.msgbus.clear_by_owner(msgbus_owner)
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.mio3sk
    del bpy.types.Object.mio3sksync
    remove_translations(__name__)
    remove_icons()

if __name__ == "__main__":
    register()
