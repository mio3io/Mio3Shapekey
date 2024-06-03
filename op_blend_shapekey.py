import bpy
import bmesh
import mathutils
import numpy as np
from bpy.types import Operator, Panel
from .define import *

# import time

def update_props(self, context):
    prop_s = context.scene.mio3sk
    prop_s.blend = self.blend


class MIO3SK_OT_blend(Operator):
    bl_idname = "mesh.mio3sk_blend"
    bl_label = "シェイプキーをブレンド"
    bl_description = "シェプキーをブレンド"
    bl_options = {"REGISTER", "UNDO"}

    blend: bpy.props.FloatProperty(name="ブレンド", default=1, min=-2, max=2, step=10, update=update_props)
    smooth: bpy.props.BoolProperty(name="スムーズブレンド", default=True)
    add: bpy.props.BoolProperty(name="加算", default=False)
    blend_mode: bpy.props.EnumProperty(
        name="方向",
        default="RADIAL",
        items=[
            ("RADIAL", "Radial", ""),
            ("LEFT", "Left", ""),
            ("RIGHT", "Right", ""),
            ("TOP", "Top", ""),
            ("BOTTOM", "Bottom", ""),
        ],
    )
    falloff: bpy.props.EnumProperty(
        name="減衰",
        default="gaussian",
        items=[
            ("gaussian", "ガウス", ""),
            ("linear", "リニア", ""),
        ],
    )
    blend_width: bpy.props.FloatProperty(name="中心幅", default=1.0, soft_min=0.1, soft_max=1, step=10)
    normalize: bpy.props.BoolProperty(name="正規化", default=True)

    blend_source_name: None
    blend_source: None

    @classmethod
    def poll(cls, context):
        return (
            context.object is not None
            and context.object.mode == "EDIT"
            and context.object.data.shape_keys is not None
        )

    def execute(self, context):
        # start_time = time.time()

        obj = context.active_object
        mesh = obj.data

        if not self.smooth:
            bpy.ops.mesh.blend_from_shape(shape=self.blend_source_name, blend=self.blend, add=self.add)
            return {"FINISHED"}

        basis = mesh.shape_keys.key_blocks[0]

        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        selected_verts = [v for v in bm.verts if v.select]
        if context.object.use_mesh_mirror_x:
            selected_verts.extend(self.get_symmetry(bm, selected_verts))

        selected_verts_indices = [v.index for v in selected_verts]
        basis_coords = np.array([basis.data[i].co for i in selected_verts_indices])
        target_coords = np.array([self.blend_source.data[i].co for i in selected_verts_indices])
        current_coords = np.array([v.co for v in selected_verts])

        move_vectors = target_coords - basis_coords

        weights = self.calculate_weights(current_coords)
        weights = weights * self.blend
        if self.add:
            movement_vectors = move_vectors * weights[:, np.newaxis]
            new_coords = current_coords + movement_vectors
        else:
            new_coords = (1 - weights[:, np.newaxis]) * current_coords + weights[
                :, np.newaxis
            ] * target_coords
        for v, new_co in zip(selected_verts, new_coords):
            v.co = new_co

        bmesh.update_edit_mesh(obj.data)

        # print(f"実行時間: {time.time() - start_time} 秒")
        return {"FINISHED"}

    # Xミラーのみ
    def get_symmetry(self, bm, selected_verts):
        symm_verts = []
        kd = mathutils.kdtree.KDTree(len(bm.verts))
        for i, v in enumerate(bm.verts):
            kd.insert(v.co, i)
        kd.balance()
        for v in selected_verts:
            co = v.co
            symm_co = mathutils.Vector((-co.x, co.y, co.z))
            co_find = kd.find(symm_co)
            if co_find is not None and co_find[2] < 0.0001:
                symm_vert = bm.verts[co_find[1]]
                if symm_vert not in selected_verts:
                    symm_verts.append(symm_vert)
        return symm_verts

    # ウェイト計算
    def calculate_weights(self, coords):
        if self.blend_mode in ["LEFT", "RIGHT", "TOP", "BOTTOM"]:
            axis_index = 0 if self.blend_mode in ["LEFT", "RIGHT"] else 2
            min_val = np.min(coords[:, axis_index])
            max_val = np.max(coords[:, axis_index])
            center_val = (min_val + max_val) / 2
            grad_width = (max_val - min_val) * self.blend_width  # 幅％

            if max_val == min_val:  # 差がゼロの場合の対処
                weights = np.full(coords.shape[0], 0.5)
            else:
                if self.blend_mode in ["LEFT", "BOTTOM"]:
                    weights = ((center_val + grad_width / 2) - coords[:, axis_index]) / grad_width
                else:  # RIGHT or TOP
                    weights = (coords[:, axis_index] - (center_val - grad_width / 2)) / grad_width

                weights = np.clip(weights, 0, 1)
        else:
            center = np.mean(coords, axis=0)
            distances = np.linalg.norm(coords - center, axis=1)
            max_distance = np.max(distances)
            sigma = max_distance / 3

            # 減衰タイプ
            if self.falloff == "gaussian":
                gaussian_weights = self.gaussian(distances, 0, sigma)
                weights = gaussian_weights
            else:
                linear_weights = 1 - (distances / max_distance)
                weights = linear_weights

            if self.normalize:
                weights /= np.max(weights)  # 正規化

        return weights
    
    def gaussian(self, x, mu, sigma):
        return np.exp(-((x - mu) ** 2) / (2 * sigma**2))
    
    def invoke(self, context, event):
        obj = context.active_object
        mesh = obj.data
        prop_s = context.scene.mio3sk
        prop_o = obj.mio3sksync

        self.blend = prop_s.blend
        self.smooth = prop_s.blend_smooth

        self.blend_source_name = prop_o.blend_source_name
        self.blend_source = mesh.shape_keys.key_blocks.get(prop_o.blend_source_name)

        if not self.blend_source:
            self.report({"ERROR"}, "ソースになるシェイプキーがありません")
            return {"CANCELLED"}

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")

        count = mesh.count_selected_items()[0]
        if count < 1:
            self.report({"ERROR"}, "頂点が選択されていません")
            return {"CANCELLED"}

        if count < 2:
            self.smooth = False

        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "blend")
        layout.prop(self, "add")
        layout.prop(self, "smooth")

        box = layout.box()
        box.enabled = True if self.smooth else False
        box.prop(self, "blend_mode")
        if self.blend_mode == "RADIAL":
            box.prop(self, "falloff")
            box.prop(self, "normalize")
        else:
            box.prop(self, "blend_width")


class MIO3SK_OT_reset(Operator):
    bl_idname = "mesh.mio3sk_reset"
    bl_label = "Reset ShapeKey"
    bl_description = "Reset ShapeKey"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return (
            context.object is not None
            and context.object.mode == "EDIT"
            and context.object.data.shape_keys is not None
        )

    def execute(self, context):
        mesh = context.object.data
        basis = mesh.shape_keys.key_blocks[0]
        try:
            bpy.ops.mesh.blend_from_shape(shape=basis.name, blend=1, add=False)
        except Exception as e:
            self.report({"ERROR"}, str(e))

        return {"FINISHED"}


class MIO3SK_PT_sub_blend(Panel):
    bl_label = "Blend"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_parent_id = "MIO3SK_PT_main"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.active_shape_key is not None

    def draw(self, context):
        prop_s = context.scene.mio3sk
        prop_o = context.object.mio3sksync
        shape_keys = context.object.data.shape_keys

        layout = self.layout
        row = layout.row(align=True)
        row.scale_x = 2
        row.operator(MIO3SK_OT_blend.bl_idname, text="ブレンド")
        row.scale_x = 1
        row.prop(prop_s, "blend", text="")

        row = layout.row(align=True)
        # シェイプキーリスト
        row.separator()
        row.label(text="ソース")
        row.prop_search(
            prop_o,
            "blend_source_name",
            shape_keys,
            "key_blocks",
            text="",
        )

        row = layout.row()
        row.scale_x = 2
        row.prop(prop_s, "blend_smooth")


classes = [MIO3SK_OT_blend, MIO3SK_OT_reset, MIO3SK_PT_sub_blend]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
