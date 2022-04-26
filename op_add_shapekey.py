import csv
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from .define import *
from .op_util import *


# ファイルの読み込み
class MIO3SK_OT_some_file(Operator, ImportHelper):
    bl_idname = "mio3sk.add_file"
    bl_label = "Import"
    bl_description = "Add: Import CSV"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".csv"

    filter_glob: bpy.props.StringProperty(
        default="*.csv",
        options={"HIDDEN"},
        maxlen=255,
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in OBJECT_TYPES

    def execute(self, context):
        # context, self.filepath, self.use_setting
        with open(self.filepath) as f:
            reader = csv.reader(f)
            for row in reader:
                addNewKey(row[0], context)

        return {"FINISHED"}


# プリセットの読み込み
class MIO3SK_OT_add_preset(Operator):
    bl_idname = "mio3sk.add_preset"
    bl_label = "Import"
    bl_description = "Add: from presets"
    bl_options = {"REGISTER", "UNDO"}

    type: bpy.props.EnumProperty(
        default="vrc_viseme",
        items=[
            ("vrc_viseme", "VRChat Viseme", ""),
            ("mmd_light", "MMD Light", ""),
            ("perfect_sync", "Perfect Sync", ""),
        ],
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in OBJECT_TYPES

    def execute(self, context):
        file = os.path.join(TEMPLATE_DIR, self.type + ".csv")
        with open(file) as f:
            reader = csv.reader(f)
            for row in reader:
                addNewKey(row[0], context)
        return {"FINISHED"}


# コレクション内で使用されているキーをすべて作成
class MIO3SK_OT_fill_keys(Operator):
    bl_idname = "mio3sk.fill_keys"
    bl_label = "Fill shapekeys from collection"
    bl_description = "Fill shapekeys from collection"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and is_sync_collection(context.object)

    def execute(self, context):
        object = context.object
        prop_o = object.mio3sksync

        collection_keys = []
        for cobj in [o for o in prop_o.syncs.objects if has_shapekey(o)]:
            for name in cobj.data.shape_keys.key_blocks.keys():
                if name not in collection_keys:
                    collection_keys.append(name)

        for name in collection_keys:
            addNewKey(name, context)

        return {"FINISHED"}


def addNewKey(keyname, context):
    if keyname in context.object.data.shape_keys.key_blocks:
        return
    context.object.shape_key_add(name=keyname, from_mix=False)
