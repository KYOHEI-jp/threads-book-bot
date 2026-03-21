import json
import random
import urllib.parse
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header

STORE_ID = "aoga101903-22"


def load_posts(file_path: str = "posts.json") -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_amazon_url(title: str) -> str:
    encoded_title = urllib.parse.quote(title)
    return f"https://www.amazon.co.jp/s?k={encoded_title}&tag={STORE_ID}"


def build_final_text(post: dict) -> str:
    title = post["title"]
    text = post["text"].strip()
    amazon_url = build_amazon_url(title)
    return f"{text}\n\n{amazon_url}"


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


def main() -> None:
    posts = load_posts()
    if not posts:
        raise ValueError("posts.json が空です。")

    post = random.choice(posts)
    final_text = build_final_text(post)

    print(final_text)

    subject = f"今日のThreads投稿 | {post['title']}"
    send_email(subject, final_text)


if __name__ == "__main__":
    main()
