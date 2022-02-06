# Mio3 ShapeKeySync

複数のオブエジェクトのシェイプキーを同期する Blender Addon です。
選択したコレクションに含まれるオブジェクトのシェイプキーの数値をすべて同期します。

![](https://github.com/mio3io/resources/raw/Mio3ShapekeySync/Mio3ShapekeySync2022-02-07%20020022.png)

オブジェクト自身のシェイプキーの数、同期しているコレクションのすべてのシェイプキーの数（名前の重複は 1 カウント）を表示する機能も付いています。統合後のシェイプキーの数を調整するのに役立ちます。

## 導入方法

[Code > Download ZIP](https://github.com/mio3io/Mio3ShapekeySync/archive/master.zip) から ZIP ファイルをダウンロードします。

Blender の `Edit > Preferences > Addons > Install` を開き、ダウンロードしたアドオンの ZIP ファイルを選択してインストールボタンを押します。
インストール後、該当するアドオンの左側についているチェックボックスを ON にします。

## 使い方

シェイプキーを使用できるオブジェクトを選択するとサイドバーの Tool に「Mio3 ShapeKey Sync」とい項目が表示されます。
選択中のオブジェクトのシェイプキーと同期させたいコレクションを設定してください。
コレクションに含まれるオブジェクトのシェイプキーが同期します。
コレクションに自分自身が含まれてても問題ありません。
