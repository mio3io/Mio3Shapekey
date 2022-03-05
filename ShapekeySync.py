import bpy

OBJECT_TYPES = {"MESH", "CURVE", "SURFACE", "LATTICE"}


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
