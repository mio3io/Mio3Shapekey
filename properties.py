import bpy
from bpy.types import PropertyGroup


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


classes = [
    MIO3SK_scene_props,
    MIO3SK_props,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.mio3sk = bpy.props.PointerProperty(type=MIO3SK_scene_props)
    bpy.types.Object.mio3sksync = bpy.props.PointerProperty(type=MIO3SK_props)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.mio3sk
    del bpy.types.Object.mio3sksync
