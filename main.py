import json
import random
import urllib.parse
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header

STORE_ID = "aoga101903-22"
RAKUTEN_AFFILIATE_ID = "524c75b6.f0c681ff.524c75b7.a179a690"


def load_json(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_amazon_url(post: dict) -> str:
    if post.get("asin"):
        return f"https://www.amazon.co.jp/dp/{post['asin']}?tag={STORE_ID}"
    encoded_title = urllib.parse.quote(post["title"])
    return f"https://www.amazon.co.jp/s?k={encoded_title}&tag={STORE_ID}"


def build_rakuten_url(post: dict) -> str:
    keyword = urllib.parse.quote(post.get("title", ""))
    search_url = urllib.parse.quote(f"https://search.rakuten.co.jp/search/mall/{keyword}/", safe="")
    return f"https://hb.afl.rakuten.co.jp/ichiba/{RAKUTEN_AFFILIATE_ID}/?pc={search_url}&link_type=hybrid_url"


def build_post_text(post: dict) -> str:
    text = post.get("text", "").strip()
    amazon_url = build_amazon_url(post)
    rakuten_url = build_rakuten_url(post)
    link_block = (
        f"※リンクはアフィリエイトを含みます\n"
        f"Amazon：{amazon_url}\n"
        f"楽天：{rakuten_url}"
    )
    # textに既存の※注記が含まれる場合は除去して差し替える
    if "※" in text:
        text = text[:text.index("※")].strip()
    return f"{text}\n\n{link_block}" if text else link_block


def send_email(subject: str, body: str) -> None:
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    email_to = os.getenv("EMAIL_TO")

    if not email_user or not email_pass or not email_to:
        raise ValueError("EMAIL_USER / EMAIL_PASS / EMAIL_TO のいずれかが未設定です。")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = email_user
    msg["To"] = email_to

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_user, email_pass)
        smtp.sendmail(email_user, [email_to], msg.as_string())


def load_json_optional(file_path: str) -> list[dict]:
    if not os.path.exists(file_path):
        return []
    return load_json(file_path)


def main() -> None:
    books = load_json("books.json")
    toys = load_json("toys.json")
    fidgets = load_json_optional("fidgets.json")

    if not books:
        raise ValueError("books.json が空です。")
    if not toys:
        raise ValueError("toys.json が空です。")

    book_post = random.choice(books)
    toy_post = random.choice(toys)

    book_text = build_post_text(book_post)
    toy_text = build_post_text(toy_post)

    final_body = (
        f"【今日の本】\n"
        f"{book_text}\n\n"
        f"--------------------\n\n"
        f"【今日のおもちゃ】\n"
        f"{toy_text}"
    )

    def display_name(post: dict) -> str:
        return post.get("title") or post.get("asin", "（不明）")

    subject_parts = f"本: {display_name(book_post)} / おもちゃ: {display_name(toy_post)}"

    if fidgets:
        fidget_post = random.choice(fidgets)
        fidget_text = build_post_text(fidget_post)
        final_body += (
            f"\n\n--------------------\n\n"
            f"【今日のフィジェット】\n"
            f"{fidget_text}"
        )
        subject_parts += f" / フィジェット: {display_name(fidget_post)}"

    print(final_body)

    subject = f"今日のThreads投稿 | {subject_parts}"
    send_email(subject, final_body)


if __name__ == "__main__":
    main()
