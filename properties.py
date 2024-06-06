import bpy
from bpy.types import PropertyGroup
from bpy.app.handlers import persistent
from .op_rename_shapekey import MIO3SK_OT_rename
from .define import *


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


class MIO3SK_scene_state(PropertyGroup):
    sync_active_shapekey_enabled: bpy.props.BoolProperty(default=True)
    sync_name_enabled: bpy.props.BoolProperty(default=True)

    blend: bpy.props.FloatProperty(name="ブレンド", default=1, soft_min=-1, soft_max=2, step=10)
    blend_smooth: bpy.props.BoolProperty(name="スムーズブレンド", default=False)

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

    rename_search: bpy.props.StringProperty()
    rename_replace: bpy.props.StringProperty()
    rename_regex: bpy.props.BoolProperty()
    rename_replace_sync_collections: bpy.props.BoolProperty(default=True)


class MIO3SK_stored_shape_key_name(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()


class MIO3SK_object_state(bpy.types.PropertyGroup):
    syncs: bpy.props.PointerProperty(
        name=bpy.app.translations.pgettext("Sync Collection"), type=bpy.types.Collection
    )
    blend_source_name: bpy.props.StringProperty()
    stored_shape_key_names: bpy.props.CollectionProperty(
        type=MIO3SK_stored_shape_key_name,
    )

    def update_stored(self, current_shape_key_names):
        if not self.stored_shape_key_names:
            for name in current_shape_key_names:
                item = self.stored_shape_key_names.add()
                item.name = name
        else:
            stored_shape_key_names = [item.name for item in self.stored_shape_key_names]
            self.stored_shape_key_names.clear()
            for name in current_shape_key_names:
                item = self.stored_shape_key_names.add()
                item.name = name
            return stored_shape_key_names


# 変更した名前の検知
def callback_rename():
    obj = bpy.context.object
    if obj and obj.type in OBJECT_TYPES and obj.data.shape_keys:
        prop_o = obj.mio3sksync
        key_blocks = obj.data.shape_keys.key_blocks
        current_shape_key_names = [sk.name for sk in key_blocks]

        stored_names = prop_o.update_stored(current_shape_key_names)
        if stored_names:
            removed_keys = set(stored_names) - set(current_shape_key_names)
            if removed_keys:
                prop_s = bpy.context.scene.mio3sk
                for old_name, new_name in zip(stored_names, current_shape_key_names):
                    if old_name != new_name:
                        if prop_s.sync_name_enabled:
                            bpy.ops.mio3sk.rename(old_name=old_name, new_name=new_name)
                        if prop_o.blend_source_name == old_name:
                            prop_o.blend_source_name = new_name
                        break


msgbus_owner = object()


def register_msgbus():
    bpy.msgbus.clear_by_owner(msgbus_owner)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.ShapeKey, "name"),
        owner=msgbus_owner,
        args=(),
        notify=callback_rename,
    )
    if load_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_handler)


@persistent
def load_handler(scene):
    register_msgbus()
    for obj in bpy.data.objects:
        if obj.type in OBJECT_TYPES and obj.data.shape_keys:
            prop_o = obj.mio3sksync
            key_blocks = obj.data.shape_keys.key_blocks
            prop_o.update_stored([sk.name for sk in key_blocks])


classes = [
    MIO3SK_stored_shape_key_name,
    MIO3SK_scene_state,
    MIO3SK_object_state,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.Scene.mio3sk = bpy.props.PointerProperty(type=MIO3SK_scene_state)
    bpy.types.Object.mio3sksync = bpy.props.PointerProperty(type=MIO3SK_object_state)

    register_msgbus()


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.mio3sk
    del bpy.types.Object.mio3sksync

    bpy.msgbus.clear_by_owner(msgbus_owner)
    bpy.app.handlers.load_post.remove(load_handler)
