import bpy
from bpy.types import PropertyGroup
from bpy.app.handlers import persistent


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

    rename_inputname: bpy.props.StringProperty()
    rename_sync_collections: bpy.props.BoolProperty(default=True)
    rename_search: bpy.props.StringProperty()
    rename_replace: bpy.props.StringProperty()
    rename_regex: bpy.props.BoolProperty()
    rename_replace_sync_collections: bpy.props.BoolProperty(default=True)


class MIO3SK_object_state(bpy.types.PropertyGroup):
    syncs: bpy.props.PointerProperty(
        name=bpy.app.translations.pgettext("Sync Collection"), type=bpy.types.Collection
    )
    blend_source_name: bpy.props.StringProperty()


def callback_rename():
    obj = bpy.context.object
    if obj and obj.type in {"MESH", "CURVE", "SURFACE", "LATTICE"} and obj.data.shape_keys:
        current_shape_key_names = [sk.name for sk in obj.data.shape_keys.key_blocks]
        if "stored_shape_key_names" not in obj:
            obj["stored_shape_key_names"] = current_shape_key_names
        else:
            stored_shape_key_names = obj["stored_shape_key_names"]
            # added_keys = set(current_shape_key_names) - set(stored_shape_key_names)
            removed_keys = set(stored_shape_key_names) - set(current_shape_key_names)
            if removed_keys:
                for old_name, new_name in zip(stored_shape_key_names, current_shape_key_names):
                    prop_o = obj.mio3sksync
                    if old_name != new_name:
                        if hasattr(prop_o, "blend_source_name") and prop_o.blend_source_name == old_name:
                            prop_o.blend_source_name = new_name
                        break
            obj["stored_shape_key_names"] = current_shape_key_names


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


classes = [
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
