"""
books.json / toys.json / fidgets.json を読み込み、note 用 Markdown 記事を articles/ に生成する。
同日に複数回実行しても同じ商品の組み合わせが選ばれる（日付シード）。
"""

import json
import os
import random
import urllib.parse
from datetime import date
from typing import Optional

STORE_ID = "aoga101903-22"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(SCRIPT_DIR, "articles")


def load_json(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_amazon_url(post: dict) -> str:
    if post.get("asin"):
        return f"https://www.amazon.co.jp/dp/{post['asin']}?tag={STORE_ID}"
    encoded = urllib.parse.quote(post["title"])
    return f"https://www.amazon.co.jp/s?k={encoded}&tag={STORE_ID}"


def build_section(heading: str, post: dict) -> str:
    title = post.get("title") or post.get("asin", "")
    text = post.get("text", "").strip()
    url = build_amazon_url(post)

    lines = [f"## {heading}：{title}", ""]
    if text:
        lines += [text, ""]
    lines += [f"[Amazonで見る]({url})", "", "---", ""]
    return "\n".join(lines)


def build_article(book: dict, toy: dict, fidget: Optional[dict], today: date) -> str:
    date_str = today.strftime("%Y年%m月%d日")

    lines = [
        f"# 今日のおすすめ｜{date_str}",
        "",
        "---",
        "",
        build_section("本", book),
        build_section("おもちゃ", toy),
    ]
    if fidget:
        lines.append(build_section("フィジェット", fidget))

    lines.append("※ 本記事のリンクにはアフィリエイトが含まれます。")
    return "\n".join(lines)


def main() -> None:
    books = load_json(os.path.join(SCRIPT_DIR, "books.json"))
    toys = load_json(os.path.join(SCRIPT_DIR, "toys.json"))
    fidgets = load_json(os.path.join(SCRIPT_DIR, "fidgets.json"))

    if not books:
        raise ValueError("books.json が空です。")
    if not toys:
        raise ValueError("toys.json が空です。")

    today = date.today()
    random.seed(today.toordinal())  # 同日は常に同じ組み合わせを選ぶ

    book = random.choice(books)
    toy = random.choice(toys)
    fidget = random.choice(fidgets) if fidgets else None

    article = build_article(book, toy, fidget, today)

    os.makedirs(ARTICLES_DIR, exist_ok=True)
    output_path = os.path.join(ARTICLES_DIR, f"{today.isoformat()}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(article)

    print(f"生成しました → {output_path}")


if __name__ == "__main__":
    main()
