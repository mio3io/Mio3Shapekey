import os
import bpy

ICON_DIR = os.path.join(os.path.dirname(__file__), "icons") 
icons = bpy.utils.previews.new()

def register_icons():
  icons.load("DEFAULT", os.path.join(ICON_DIR, "default.png"), "IMAGE")
  icons.load("PRIMARY", os.path.join(ICON_DIR, "primary.png"), "IMAGE")
  icons.load("MOVE", os.path.join(ICON_DIR, "move.png"), "IMAGE")

  icons.load("FACE_ALL", os.path.join(ICON_DIR, "face_all.png"), "IMAGE")
  icons.load("FACE_MIRRIR", os.path.join(ICON_DIR, "face_mirror.png"), "IMAGE")
  icons.load("FACE_L", os.path.join(ICON_DIR, "face_left.png"), "IMAGE")
  icons.load("FACE_R", os.path.join(ICON_DIR, "face_right.png"), "IMAGE")

def remove_icons():
  if "FACE_ALL" in icons:
    bpy.utils.previews.remove(icons)