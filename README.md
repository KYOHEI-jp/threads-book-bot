# threads-book-bot

## 商品JSONの追加

`generate_product.py` を使うと、各JSONファイルに新しい商品を対話形式で追加できます。

```bash
python3 generate_product.py
```

### カテゴリと対応ファイル

```
カテゴリを選択してください:
  1. 書籍 → books.json
  2. おもちゃ・ガジェット → toys.json
  3. フィジェット → fidgets.json
```

入力後にテキストのプレビューが表示され、`y` を入力すると該当のJSONファイルに追記されます。

## JSONファイル構成

| ファイル | 内容 | 件数目安 |
|---|---|---|
| `books.json` | 書籍アフィリエイト投稿 | 100件 |
| `toys.json` | おもちゃ投稿 | 任意 |
| `gadgets.json` | ガジェット投稿 | 50件 |
| `fidgets.json` | フィジェット投稿 | 100件 |

## note 記事の自動生成

`generate_note_article.py` を実行すると、`books.json` / `toys.json` / `fidgets.json` から毎回ランダムに1件ずつピックアップし、note 投稿用の Markdown 記事を `articles/YYYY-MM-DD.md` に保存します。

```bash
python3 generate_note_article.py
# → articles/2026-03-28.md を生成
```

### GitHub Actions による自動生成

`.github/workflows/generate_article.yml` により、毎日 **JST 7:00** に自動実行され、生成された記事がリポジトリに自動コミット・プッシュされます。

| ワークフロー | スケジュール | 処理 |
|---|---|---|
| `generate_article.yml` | 毎日 JST 7:00 | 記事生成 → `articles/` にコミット |
| `post.yml` | 毎日 JST 9:00 | メール送信 |

手動実行は GitHub の Actions タブ → `Generate Note Article` → `Run workflow` から行えます。

## メール送信（main.py）

`main.py` は `books.json` / `toys.json` / `gadgets.json` / `fidgets.json` からランダムに1件ずつ選び、Amazon・楽天のアフィリエイトリンク付きの投稿文をメールで送信します。

```bash
python3 main.py
```

環境変数（GitHub Secrets）に `EMAIL_USER` / `EMAIL_PASS` / `EMAIL_TO` が必要です。ローカルでは標準出力のみ確認できます。
