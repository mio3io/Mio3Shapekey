import bpy
from bpy.app.handlers import persistent

from . import properties
from . import dictionary
from . import icons
from . import panel
from . import op_sync_shapekey
from . import op_add_shapekey
from . import op_remove_shapekey
from . import op_move_shapekey
from . import op_sort_shapekey
from . import op_reset_shapekey
from . import op_rename_shapekey
from . import op_propagate_shapekey
from . import op_options

bl_info = {
    "name": "Mio3 ShapeKey",
    "author": "mio3io",
    "version": (2, 5, 5),
    "blender": (3, 0, 0),
    "warning": "",
    "location": "View3D > Sidebar",
    "description": "Synchronize shape keys with the same name in the certain collection.",
    "category": "Object",
}


def register():
    dictionary.register(__name__)
    icons.register()

    properties.register()
    panel.register()
    op_sync_shapekey.register()
    op_add_shapekey.register()
    op_remove_shapekey.register()
    op_move_shapekey.register()
    op_sort_shapekey.register()
    op_rename_shapekey.register()
    op_reset_shapekey.register()
    op_propagate_shapekey.register()
    op_options.register()


def unregister():
    dictionary.unregister(__name__)
    icons.unregister()

    properties.unregister()
    panel.unregister()
    op_sync_shapekey.unregister()
    op_add_shapekey.unregister()
    op_remove_shapekey.unregister()
    op_move_shapekey.unregister()
    op_sort_shapekey.unregister()
    op_rename_shapekey.unregister()
    op_reset_shapekey.unregister()
    op_propagate_shapekey.unregister()
    op_options.unregister()


if __name__ == "__main__":
    register()
