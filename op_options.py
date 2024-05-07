import bpy
from bpy.types import Panel

class MIO3SK_PT_sub_options(Panel):
    bl_label = "Options"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_parent_id = "MIO3SK_PT_main"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        prop_s = context.scene.mio3sk
        layout = self.layout
        row = layout.row()
        row.prop(prop_s, "sync_active_shapekey_enabled", text="Sync Active ShapeKey")
