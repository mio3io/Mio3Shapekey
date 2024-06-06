import bpy

translation_dict = {
    "ja_JP": {
        ("*", "Sync Collection"):
            "同期コレクション",

        ("*", "ASC"):
            "昇順",
        ("*", "DESC"):
            "降順",
        ("*", "Sort by ShapeKey Name"):
            "名前でソート", 
        ("*", "Sort ASC"):
            "名前でソート（昇順）",
        ("*", "Sort DESC"):
            "名前でソート（降順）",
 
        ("*", "Syntax"):
            "構文",

        ("*", "Add: Shape Key at current position"):
            "現在の位置に新しいキーを追加",
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

        ("*", "Delete shape key except disable"):
            "無効化を除くシェイプキーを削除",

        ("*", "Reset Shape"):
            "形状をリセット",
        ("*", "Reset ShapeKey"):
            "シェイプキーの形状をリセット",
        ("*", "All Vertices"):
            "全頂点",
        ("*", "Active Vertices"):
            "選択中の頂点",

        ("*", "Rename (sync)"):
            "シェイプキー名の変更",
        ("*", "Current Name"):
            "現在の名前",
        ("*", "New Name"):
            "新しい名前",
        ("*", "Rename Sync ShapeKeys"):
            "同期シェイプキー名の変更",
        ("*", "Replace Names (sync)"):
            "シェイプキー名の置換",
        ("*", "Use Regex"):
            "正規表現を使用",
        ("*", "Regular expression syntax is incorrect"):
            "正規表現が正しくありません",
        ("*", "Change other sync objects"):
            "同期コレクションも変更",

        ("*", "Move ShapeKeys"):
            "シェイプキーを移動",
        ("*", "Pinned vrc.* keys"):
            "vrc* をトップに維持する",
        ("*", "Pinned Mute keys"):
            "無効化中のキーをトップに維持する",

        ("*", "Move active ShapeKey"):
            "選択中のキーを移動",
        ("*", "Move below the key you clicked"):
            "次にクリックしたキーの下に移動",
        ("*", "Move below active ShapeKey (Multiple)"):
            "選択中のキーの下に複数移動",
        ("*", "Click the keys in order to move"):
            "移動するキーをクリック",

        ("*", "Sync Active ShapeKey"):
            "選択を同期",
        ("*", "Sync ShapeKey Name"):
            "リネームを同期",

        ("*", "Apply to Basis(Selected Vertices)"):
            "選択した頂点をBasisに反映",
    }
}


def register(name):
    if bpy.app.translations.pgettext("Sync Collection"):
        bpy.app.translations.unregister(name)
    bpy.app.translations.register(name, translation_dict)


def unregister(name):
    bpy.app.translations.unregister(name)
