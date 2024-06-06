import re
import bpy
from bpy.types import Context, Event, Operator, Panel
from bpy.props import StringProperty
from bpy.app.translations import pgettext
from .define import *
from .op_util import *


class MIO3SK_OT_rename(Operator):
    bl_idname = "mio3sk.rename"
    bl_label = "Rename Sync ShapeKeys"
    bl_description = "Rename (sync)"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    old_name: StringProperty(options={"HIDDEN"})
    new_name: StringProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in OBJECT_TYPES

    def execute(self, context):
        obj = context.active_object
        prop_o = obj.mio3sksync

        members = prop_o.syncs.objects
        for member in members:
            if member == obj or not has_shapekey(member):
                continue
            member_key_blocks = member.data.shape_keys.key_blocks
            index = member_key_blocks.find(self.old_name)
            if index > 0:
                member_key_blocks[index].name = self.new_name
                member.mio3sksync.update_stored([sk.name for sk in member_key_blocks])  # 検知用データ

        return {"FINISHED"}


class MIO3SK_OT_replace(Operator):
    bl_idname = "mio3sk.replace"
    bl_label = "Replace"
    bl_description = "Replace Names (sync)"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type in OBJECT_TYPES

    def execute(self, context):
        obj = context.active_object
        prop_s = context.scene.mio3sk
        prop_o = obj.mio3sksync

        if prop_s.rename_search:
            stash = StashProp(prop_s, "sync_active_shapekey_enabled", False)
            rep_func = lambda str, search, replace: (
                re.sub(search, replace, str) if prop_s.rename_regex else str.replace(search, replace)
            )
            targets = (
                [o for o in prop_o.syncs.objects if has_shapekey(o)]
                if prop_s.rename_replace_sync_collections and is_sync_collection(obj)
                else [obj]
            )
            for member in targets:
                for key in member.data.shape_keys.key_blocks[1:]:
                    try:
                        key.name = rep_func(key.name, prop_s.rename_search, prop_s.rename_replace)
                    except re.error:
                        self.report({"WARNING"}, "Regular expression syntax is incorrect")
                        break
            stash.revert()

        return {"FINISHED"}


class MIO3SK_PT_sub_replace(Panel):
    bl_label = "Replace Names (sync)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_parent_id = "MIO3SK_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.active_object.data.shape_keys is not None

    def draw(self, context):
        prop_s = context.scene.mio3sk
        layout = self.layout

        layout.separator()
        layout.prop(prop_s, "rename_search", text="Search")
        layout.prop(prop_s, "rename_replace", text="Replace")
        row = layout.row()
        row.prop(prop_s, "rename_regex", text="Use Regex")
        row.scale_x = 0.5
        op = row.operator("wm.url_open", text=pgettext("Syntax"), icon="URL")
        op.url = "https://docs.python.org/3/library/re.html"
        layout.prop(prop_s, "rename_replace_sync_collections", text="Change other sync objects")
        layout.operator(MIO3SK_OT_replace.bl_idname, text="Replace")


classes = [
    MIO3SK_PT_sub_replace,
    MIO3SK_OT_rename,
    MIO3SK_OT_replace,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
