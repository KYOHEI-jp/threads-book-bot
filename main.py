import json
import urllib.parse

# 読み込み
with open("posts.json", "r") as f:
    posts = json.load(f)

# 1個選ぶ（順番でもOK）
post = posts[0]

title = post["title"]
text = post["text"]

# Amazonリンク追加
encoded = urllib.parse.quote(title)
url = f"https://www.amazon.co.jp/s?k={encoded}&tag=aoga101903-22"

final_text = text + "\n" + url

print(final_text)
