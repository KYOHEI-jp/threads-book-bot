# threads-book-bot

## 商品JSONの追加

`generate_product.py` を使うと、`books.json` または `toys.json` に新しい商品を対話形式で追加できます。

```bash
python generate_product.py
```

### 書籍を追加する場合

```
カテゴリを選択してください:
  1. 書籍 → books.json
  2. おもちゃ・ガジェット → toys.json
選択 [1/2]: 1

--- 書籍情報を入力してください ---
  タイトル: 嫌われる勇気
  テーマ: 人間関係
  対象読者の悩み: 人にどう思われるかで疲れてる
  本の核心メッセージ: 他人の評価を生きる軸にしない
```

### おもちゃ・ガジェットを追加する場合

```
選択 [1/2]: 2

--- おもちゃ・ガジェット情報を入力してください ---
  タイトル: フィジェットキューブ
  特徴・説明: 触るだけなのに妙に落ち着く
  対象ユーザー: 手が暇でついスマホ触る人
```

入力後にテキストのプレビューが表示され、`y` を入力すると該当のJSONファイルに追記されます。

## note 記事の自動生成

`generate_note_article.py` を実行すると、`books.json` / `toys.json` / `fidgets.json` から1件ずつピックアップし、note 投稿用の Markdown 記事を `articles/YYYY-MM-DD.md` に保存します。

```bash
python generate_note_article.py
# → articles/2026-03-28.md を生成
```

同日に複数回実行しても同じ商品の組み合わせが選ばれます（日付を乱数シードに使用）。

### GitHub Actions による自動生成

`.github/workflows/generate_article.yml` により、毎日 **JST 7:00** に自動実行され、生成された記事がリポジトリに自動コミット・プッシュされます。

| ワークフロー | スケジュール | 処理 |
|---|---|---|
| `generate_article.yml` | 毎日 JST 7:00 | 記事生成 → `articles/` にコミット |
| `post.yml` | 毎日 JST 9:00 | メール送信 |

手動実行は GitHub の Actions タブ → `Generate Note Article` → `Run workflow` から行えます。
