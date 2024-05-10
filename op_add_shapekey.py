import csv
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from .define import *
from .op_util import *


# 選択しているキーの下に新しいキーを追加
class MIO3SK_OT_add_key_current(Operator):
    bl_idname = "mio3sk.add_key_current"
    bl_label = "Add Shape Key"
    bl_description = "Add: Shape Key at current position"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            context.object is not None
            and context.object.type in OBJECT_TYPES
            and context.object.data.shape_keys is not None
            and context.active_object.mode == "OBJECT"
        )

    def execute(self, context):
        object = context.object

        base_idx = object.active_shape_key_index
        move_idx = len(object.data.shape_keys.key_blocks)
        object.active_shape_key_index = move_idx

        bpy.ops.object.shape_key_add(from_mix=False)

        [bpy.ops.object.shape_key_move(type="UP") for i in range(move_idx - base_idx - 1)]

        return {"FINISHED"}


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
        initShapeKey(context)
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
        initShapeKey(context)
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


def initShapeKey(context):
    if context.object.data.shape_keys is None:
        bpy.ops.object.shape_key_add(from_mix=False)


classes = [
    MIO3SK_OT_some_file,
    MIO3SK_OT_add_key_current,
    MIO3SK_OT_add_preset,
    MIO3SK_OT_fill_keys,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
