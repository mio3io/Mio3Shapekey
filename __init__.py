import bpy
from bpy.types import PropertyGroup
from bpy.app.handlers import persistent

from .dictionary import *
from .icons import *
from .panel import *
from .op_sync_shapekey import *
from .op_add_shapekey import *
from .op_remove_shapekey import *
from .op_move_shapekey import *
from .op_sort_shapekey import *
from .op_reset_shapekey import *
from .op_rename_shapekey import *
from .op_propagate_shapekey import *


bl_info = {
    "name": "Mio3 ShapeKey",
    "author": "mio3io",
    "version": (2, 5, 3),
    "blender": (3, 0, 0),
    "warning": "",
    "location": "View3D > Sidebar",
    "description": "Synchronize shape keys with the same name in the certain collection.",
    "category": "Object",
}


def callback_xmirror_auto_enabled(self, context):
    if self.xmirror_auto_enabled:
        register_auto_active_mirror_edit()
    else:
        unregister_auto_active_mirror_edit()


def callback_move_active_single(self, context):
    if self.move_active_single:
        self.move_active_type = "single"
        self.move_active_multi = False
        bpy.ops.mio3sk.move_set_primary()
    else:
        bpy.ops.mio3sk.move_remove_primary()


def callback_move_active_multi(self, context):
    if self.move_active_multi:
        self.move_active_type = "multi"
        self.move_active_single = False
        bpy.ops.mio3sk.move_set_primary()
    else:
        bpy.ops.mio3sk.move_remove_primary()


class MIO3SK_scene_props(PropertyGroup):

    sync_active_shapekey_enabled: bpy.props.BoolProperty(default=True)
    xmirror_auto_enabled: bpy.props.BoolProperty(default=False, update=callback_xmirror_auto_enabled)
    # xmirror_auto_suffix_type: bpy.props.EnumProperty(
    #     default="_head",
    #     items=[(k, f"{l} / {r}", "") for (k, l, r) in lr_suffix_types_source],
    # )

    move_active_single: bpy.props.BoolProperty(update=callback_move_active_single)
    move_active_multi: bpy.props.BoolProperty(update=callback_move_active_multi)
    move_active_type: bpy.props.EnumProperty(
        default="single",
        items=[("single", "single", ""), ("multi", "multi", "")],
    )
    move_primary: bpy.props.StringProperty()
    move_primary_auto: bpy.props.BoolProperty()

    sort_priority: bpy.props.BoolProperty()
    sort_priority_mute: bpy.props.BoolProperty()

    rename_inputname: bpy.props.StringProperty()
    rename_sync_collections: bpy.props.BoolProperty(default=True)
    rename_search: bpy.props.StringProperty()
    rename_replace: bpy.props.StringProperty()
    rename_regex: bpy.props.BoolProperty()
    rename_replace_sync_collections: bpy.props.BoolProperty(default=True)


class MIO3SK_props(bpy.types.PropertyGroup):
    syncs: bpy.props.PointerProperty(
        name=bpy.app.translations.pgettext("Sync Collection"), type=bpy.types.Collection
    )

def callback_update_mode():
    auto_active_mirror_edit()

def callback_update_shapekey():
    sync_shapekey_value()


def callback_show_only_shape_key():
    sync_show_only_shape_key()


def callback_rename_shapekey():
    pass


def callback_active_shapekey():
    prop_s = bpy.context.scene.mio3sk
    if prop_s.sync_active_shapekey_enabled:
        sync_active_shape_key()
    prop_s.rename_inputname = str(bpy.context.object.active_shape_key.name)

msgbus_owner = object()


def register_msgbus():

    bpy.msgbus.clear_by_owner(msgbus_owner)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "mode"),
        owner=msgbus_owner,
        args=(),
        notify=callback_update_mode,
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "active_shape_key_index"),
        owner=msgbus_owner,
        args=(),
        notify=callback_active_shapekey,
    )
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.ShapeKey, "name"),
        owner=msgbus_owner,
        args=(),
        notify=callback_rename_shapekey,
    )
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
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "show_only_shape_key"),
        owner=msgbus_owner,
        args=(),
        notify=callback_show_only_shape_key,
    )

    if load_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_handler)

    if hasattr(bpy.context, "scene"):
        prop_s = bpy.context.scene.mio3sk
        if prop_s.xmirror_auto_enabled:
            register_auto_active_mirror_edit()
    else:
        # Default=True
        # register_auto_active_mirror_edit()
        pass


@persistent
def load_handler(scene):
    register_msgbus()


classes = [
    MIO3SK_scene_props,
    MIO3SK_props,
    MIO3SK_PT_main,
    MIO3SK_PT_sub_move,
    MIO3SK_PT_sub_sort,
    MIO3SK_PT_sub_rename,
    MIO3SK_PT_sub_replace,
    MIO3SK_PT_sub_options,
    MIO3SK_MT_context,
    MIO3SK_UL_shape_keys,
    MIO3SK_OT_some_file,
    MIO3SK_OT_add_preset,
    MIO3SK_OT_fill_keys,
    MIO3SK_OT_move_set_primary,
    MIO3SK_OT_move_remove_primary,
    MIO3SK_OT_move,
    MIO3SK_OT_sort,
    MIO3SK_OT_reset,
    MIO3SK_OT_rename,
    MIO3SK_OT_replace,
    MIO3SK_OT_remove_shapekey,
    MIO3SK_OT_propagate_to_basis,
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
