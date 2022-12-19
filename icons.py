import os
import bpy
import bpy.utils.previews

ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")
icons = bpy.utils.previews.new()


def register_icons():
    if "DEFAULT" not in icons:
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

def remove_icons():
    for pcoll in icons.values():
        if pcoll in icons:
            bpy.utils.previews.remove(pcoll)
    icons.clear()
    pass
