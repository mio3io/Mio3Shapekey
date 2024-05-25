import os
import bpy


ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")

preview_collections = {}


def register():
    import bpy.utils.previews

    icons = bpy.utils.previews.new()
    icons.load("DEFAULT", os.path.join(ICON_DIR, "default.png"), "IMAGE")
    icons.load("PRIMARY", os.path.join(ICON_DIR, "primary.png"), "IMAGE")
    icons.load("PRIMARY_HISTORY", os.path.join(ICON_DIR, "primary_history.png"), "IMAGE")
    icons.load("MOVE", os.path.join(ICON_DIR, "move.png"), "IMAGE")

    icons.load("FACE_ALL", os.path.join(ICON_DIR, "face_all.png"), "IMAGE")
    icons.load("FACE_MIRRIR", os.path.join(ICON_DIR, "face_mirror.png"), "IMAGE")
    icons.load("FACE_L", os.path.join(ICON_DIR, "face_left.png"), "IMAGE")
    icons.load("FACE_R", os.path.join(ICON_DIR, "face_right.png"), "IMAGE")

    icons.load("PARENT", os.path.join(ICON_DIR, "parent.png"), "IMAGE")
    icons.load("LINKED", os.path.join(ICON_DIR, "linked.png"), "IMAGE")

    icons.load("UP_EX", os.path.join(ICON_DIR, "arrow_up_ex.png"), "IMAGE")
    icons.load("DOWN_EX", os.path.join(ICON_DIR, "arrow_down_ex.png"), "IMAGE")
    preview_collections["icons"] = icons


def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
