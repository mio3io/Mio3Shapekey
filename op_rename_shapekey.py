import re
import bpy
from bpy.types import Operator, Panel
from bpy.app.translations import pgettext
from .define import *
from .op_util import *
from .op_sync_shapekey import *


class MIO3SK_OT_rename(Operator):
    bl_idname = "mio3sk.rename"
    bl_label = "Rename"
    bl_description = "Rename (sync)"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in OBJECT_TYPES

    def execute(self, context):
        object = context.object
        prop_s = context.scene.mio3sk
        prop_o = object.mio3sksync

        name = object.active_shape_key.name

        stash = StashProp(prop_s, "sync_active_shapekey_enabled", False)

        targets = (
            [o for o in prop_o.syncs.objects if has_shapekey(o)]
            if prop_s.rename_sync_collections and is_sync_collection(object)
            else [object]
        )
        for obj in targets:
            index = obj.data.shape_keys.key_blocks.find(name)
            if index > 0:
                obj.data.shape_keys.key_blocks[index].name = prop_s.rename_inputname

        stash.revert()

        return {"FINISHED"}


class MIO3SK_OT_replace(Operator):
    bl_idname = "mio3sk.replace"
    bl_label = "Replace"
    bl_description = "Replace Names (sync)"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in OBJECT_TYPES

    def execute(self, context):
        object = context.object
        prop_s = context.scene.mio3sk
        prop_o = object.mio3sksync

        if prop_s.rename_search:

            stash = StashProp(prop_s, "sync_active_shapekey_enabled", False)

            rep_func = rep_func_regex if prop_s.rename_regex else rep_func_replace
            targets = (
                [o for o in prop_o.syncs.objects if has_shapekey(o)]
                if prop_s.rename_replace_sync_collections and is_sync_collection(object)
                else [object]
            )
            for obj in targets:
                for key in obj.data.shape_keys.key_blocks[1:]:
                    try:
                        key.name = rep_func(key.name, prop_s.rename_search, prop_s.rename_replace)
                    except re.error:
                        self.report({"WARNING"}, "Regular expression syntax is incorrect")
                        break

            stash.revert()

        return {"FINISHED"}


def rep_func_replace(str, search, replace):
    return str.replace(search, replace)


def rep_func_regex(str, search, replace):
    return re.sub(search, replace, str)


class MIO3SK_PT_sub_rename(Panel):
    bl_label = "Rename (sync)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_parent_id = "MIO3SK_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.object.active_shape_key is not None

    def draw(self, context):
        prop_s = context.scene.mio3sk
        layout = self.layout

        layout.prop(context.object.active_shape_key, "name", text="Current Name", emboss=False)
        layout.prop(prop_s, "rename_inputname", text="New Name")
        layout.prop(prop_s, "rename_sync_collections", text="Change other sync objects")
        layout.operator(MIO3SK_OT_rename.bl_idname, text="Rename")


class MIO3SK_PT_sub_replace(Panel):
    bl_label = "Replace Names (sync)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_parent_id = "MIO3SK_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.object.active_shape_key is not None

    def draw(self, context):
        prop_s = context.scene.mio3sk
        layout = self.layout

        layout.separator()
        layout.prop(prop_s, "rename_search", text="Search")
        layout.prop(prop_s, "rename_replace", text="Replace")
        row = layout.row()
        row.prop(prop_s, "rename_regex", text="Use Regex")
        row.scale_x=0.5
        op = row.operator('wm.url_open', text=pgettext("Syntax"), icon="URL")
        op.url = "https://docs.python.org/3/library/re.html"
        layout.prop(prop_s, "rename_replace_sync_collections", text="Change other sync objects")
        layout.operator(MIO3SK_OT_replace.bl_idname, text="Replace")
