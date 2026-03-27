# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Threads向け日本語アフィリエイト投稿の自動生成・メール送信ボット。GitHub Actionsで毎日JST 9:00に実行される。

Amazon アソシエイトID: `aoga101903-22`

## Commands

```bash
# 動作確認（メール送信なし、標準出力のみ）
python main.py

# 商品JSONを対話形式で生成・追加
python generate_product.py

# note 用 Markdown 記事を articles/YYYY-MM-DD.md に生成
python generate_note_article.py

# 300件の投稿バリエーションを posts.json に生成
python generate_posts.py
```

環境変数（GitHub Secrets）:
- `EMAIL_USER` / `EMAIL_PASS` / `EMAIL_TO` — Gmail送信用
- `BITLY_TOKEN` — ワークフローで定義されているが現在未使用

## Architecture

```
main.py                  # エントリーポイント：books/toys/fidgets から1件ずつ選択 → メール送信
generate_note_article.py # books/toys/fidgets から1件ずつ選択 → articles/YYYY-MM-DD.md を生成
generate_product.py      # 商品メタデータを対話入力 → books.json / toys.json / fidgets.json に追記
generate_posts.py        # 書籍30冊 × テンプレートで300件の posts.json を生成（main.py では未使用）

books.json         # 書籍アフィリエイト投稿データ（title + text）
toys.json          # おもちゃ・ガジェット投稿データ（title + text）
fidgets.json       # フィジェット専用投稿データ（title + text）※初期状態は空配列
articles/          # 自動生成された note 用 Markdown 記事（YYYY-MM-DD.md）

.github/workflows/post.yml             # JST 9:00 メール送信
.github/workflows/generate_article.yml # JST 7:00 記事生成・自動コミット
```

### JSON フォーマット

全JSONファイル共通構造:

```json
[
  {
    "title": "商品名（Amazon検索キーワードとして使用）",
    "text": "日本語投稿本文（末尾に ※リンクはアフィリエイトを含みます）"
  }
]
```

`main.py` の `build_amazon_url()` が `title` をURLエンコードして Amazon 検索URLを生成する。

### 文体スタイル

- 冒頭: 対象読者への呼びかけ（「〇〇な人、これ読んでほしい」）
- 中盤: 問題提起 → 商品タイトル → 核心メッセージ
- 末尾: `※本リンクはアフィリエイトを含みます`（書籍）or `※リンクはアフィリエイトを含みます`（おもちゃ・フィジェット）

### fidgets 運用ルール

- `fidgets.json` はフィジェット特化カテゴリ。`toys.json` との重複登録は避ける（既存の toys.json にあるフィジェット商品は移行不要）
- `generate_product.py` でカテゴリ `3` を選択すると追記される
- `main.py` は `fidgets.json` が存在しデータがある場合のみ `【今日のフィジェット】` セクションをメールに追加する（空または不在の場合はスキップ）
- 入力項目: タイトル・触り心地/動作（sensation）・対象ユーザー・置き場所/携帯性（省略可）
