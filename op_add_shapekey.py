import bpy
import csv
import os
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty, EnumProperty

OBJECT_TYPES = {"MESH", "CURVE", "SURFACE", "LATTICE"}

ADDON_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = ADDON_DIR + os.sep + "_templates" + os.sep

# ファイルの読み込み
class MIO3SS_OT_some_file(Operator, ImportHelper):
    bl_idname = "mio3ss.add_file"
    bl_label = "Import"
    bl_description = bpy.app.translations.pgettext("Add Import CSV")
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".csv"

    filter_glob: StringProperty(
        default="*.csv",
        options={"HIDDEN"},
        maxlen=255,
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # context, self.filepath, self.use_setting
        with open(self.filepath) as f:
            reader = csv.reader(f)
            for row in reader:
                addNewKey(row[0], context)

        return {"FINISHED"}


# プリセットの読み込み
class MIO3SS_OT_add_preset(Operator):
    bl_idname = "mio3ss.add_preset"
    bl_label = "Import"
    bl_description = bpy.app.translations.pgettext("Add from presets")
    bl_options = {"REGISTER", "UNDO"}

    mode: EnumProperty(
        default="vrc_viseme",
        items=[
            ("vrc_viseme", "VRChat Viseme", ""),
            ("mmd_light", "MMD Light", ""),
            ("perfect_sync", "Perfect Sync", ""),
        ],
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        with open(TEMPLATE_DIR + self.mode + ".csv") as f:
            reader = csv.reader(f)
            for row in reader:
                addNewKey(row[0], context)
        return {"FINISHED"}


# コレクション内で使用されているキーをすべて作成
class MIO3SS_OT_fill_keys(Operator):
    bl_idname = "mio3ss.fill_keys"
    bl_label = "Fill shapekeys from collection"
    bl_description = bpy.app.translations.pgettext("Fill shapekeys from collection")
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            context.object is not None
            and context.object.type in OBJECT_TYPES
            and context.object.mio3sksync.syncs is not None
        )

    def execute(self, context):
        object = context.object

        collection_keys = []
        for cobj in object.mio3sksync.syncs.objects:
            if cobj.type not in OBJECT_TYPES or cobj.active_shape_key is None:
                continue
            for ckey in cobj.data.shape_keys.key_blocks:
                if (ckey.name not in collection_keys):
                    collection_keys.append(ckey.name)

        for name in collection_keys:
            addNewKey(name, context)

        return {"FINISHED"}


def addNewKey(keyname, context):
    if keyname in context.object.data.shape_keys.key_blocks:
        return
    context.object.shape_key_add(name=keyname)


def callback_update_shapekey():

    object = bpy.context.object
    if object.type not in OBJECT_TYPES or object.mio3sksync.syncs is None:
        return None

    # アクティブオブジェクトのシェイプキーのあるオブジェクト＆同期コレクションが設定されている

    shape_keys = object.data.shape_keys

    for item in object.mio3sksync.syncs.objects:

        # コレクションアイテム
        if item.type not in OBJECT_TYPES  or item.active_shape_key is None:
            continue

        for item_key in item.data.shape_keys.key_blocks:
            if item != object and item_key.name in shape_keys.key_blocks:
                item_key.mute = shape_keys.key_blocks[item_key.name].mute
                if item_key.value != shape_keys.key_blocks[item_key.name].value:
                    item_key.value = shape_keys.key_blocks[item_key.name].value
