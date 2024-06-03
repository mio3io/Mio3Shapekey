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
from . import op_apply_shapekey
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


def update_panel(self, context):
    is_exist = hasattr(bpy.types, "MIO3SK_PT_main")
    category = bpy.context.preferences.addons[__package__].preferences.category

    if is_exist:
        try:
            bpy.utils.unregister_class(panel.MIO3SK_PT_main)
        except:
            pass

    panel.MIO3SK_PT_main.bl_category = category
    bpy.utils.register_class(panel.MIO3SK_PT_main)


class MIO3SK_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    category: bpy.props.StringProperty(
        name="Tab",
        description="Tab",
        default="Tool",
        update=update_panel,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "category")


def register():
    dictionary.register(__name__)
    icons.register()

    bpy.utils.register_class(MIO3SK_Preferences)

    properties.register()
    panel.register()
    op_sync_shapekey.register()
    op_add_shapekey.register()
    op_remove_shapekey.register()
    op_move_shapekey.register()
    op_sort_shapekey.register()
    op_rename_shapekey.register()
    op_reset_shapekey.register()
    op_apply_shapekey.register()
    op_options.register()


def unregister():
    properties.unregister()
    panel.unregister()
    op_sync_shapekey.unregister()
    op_add_shapekey.unregister()
    op_remove_shapekey.unregister()
    op_move_shapekey.unregister()
    op_sort_shapekey.unregister()
    op_rename_shapekey.unregister()
    op_reset_shapekey.unregister()
    op_apply_shapekey.unregister()
    op_options.unregister()

    bpy.utils.unregister_class(MIO3SK_Preferences)

    icons.unregister()
    dictionary.unregister(__name__)


if __name__ == "__main__":
    register()
