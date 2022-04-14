import bpy

translation_dict = {
    "ja_JP": {
        ("*", "Sync Collection"):
            "同期コレクション",
        ("*", "Add: from presets"):
            "プリセットから追加",
        ("*", "Add: Import CSV"):
            "Add: CSVファイルから追加",
        ("*", "Add: VRChat Viseme"):
            "Add: VRChat Viseme",
        ("*", "Add: MMD Lite"):
            "Add: MMDモーフ簡易",
        ("*", "Add: Perfect Sync"):
            "Add: パーフェクトシンク",
        ("*", "Fill Shapekeys"):
            "足りないシェイプキーを埋める",
        ("*", "Fill shapekeys from collection"):
            "コレクションから不足しているシェイプキーを埋める",
    }
}


def register_translations(name):
    if bpy.app.translations.pgettext("Sync Collection"):
        bpy.app.translations.unregister(name)
    bpy.app.translations.register(name, translation_dict)


def remove_translations(name):
    bpy.app.translations.unregister(name)
