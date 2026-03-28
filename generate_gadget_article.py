"""
gadgets.json を読み込み、
note 向けガジェット紹介記事（悩み→共感→解決）を articles/gadget-YYYY-MM-DD.md に生成する。

同日に複数回実行しても同じ商品が選ばれる（日付シード）。
"""

import json
import os
import random
import urllib.parse
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))


def today_jst():
    return datetime.now(tz=JST).date()


STORE_ID = "aoga101903-22"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(SCRIPT_DIR, "articles")

DISCLAIMER_PATTERNS = [
    "※本リンクはアフィリエイトを含みます",
    "※リンクはアフィリエイトを含みます",
]

# ======================================================
# テンプレート定義
# ======================================================

TITLES = [
    "これ買ってよかった。今日のガジェット紹介",
    "地味に変わった。おすすめガジェット1選",
    "使ってみたら手放せなくなったガジェット",
    "毎日使ってる。今日のガジェット紹介",
    "ガジェット好きに届けたい、今日の1個",
    "生活が少し変わるガジェットを1つ紹介します",
]

INTRO_PAINS = [
    "地味に不便なこと、ずっと我慢してませんか。",
    "「まあこれでいいか」で使い続けてるもの、ありませんか。",
    "毎日使うものなのに、なんかいつもストレスを感じている。そういうことあります。",
    "ちょっとだけ快適になるだけで、毎日の気分がかなり変わることがあります。",
    "大きな買い物じゃなくていい。毎日使うものをちょっとよくするだけで、生活の質が変わります。",
]

INTRO_EMPATHIES = [
    "ガジェットって、買うまで「本当に必要かな」と思うものほど、使い始めたら「なんで今まで持ってなかったんだろう」ってなる。そういうものを今日は紹介します。",
    "高価なものじゃなくていい。ちゃんと使えるものを選んで、毎日の小さなストレスを一個減らす。それだけで十分価値があります。",
    "ガジェットで生活が劇的に変わるとは言いません。でも、地味に毎日の快適さが上がるものはあって、そういうものほど長く使い続けられます。",
    "便利なものって、慣れると当たり前になってしまうんですが、その「当たり前」が増えると毎日が少し楽になる。そういう話です。",
]

INTRO_BRIDGES = [
    "今日紹介するのは、そういう地味に快適なガジェットです。使ってみて良かったものを正直に書きます。",
    "今日ピックアップしたのは、実際に使ってよかったと感じたものです。参考になれば。",
    "難しい説明はしません。使ってみてどうだったか、正直に書きます。",
    "今日紹介するものは、特別派手じゃないけど、あると地味に助かるやつです。",
]

# ---- ガジェット：サブセクション ----

GADGET_FOR_WHO_EXPANSIONS = [
    "ピンときたら試してみる価値はあります。",
    "「自分に使えるかな」と思ったら、たぶん使えます。",
    "刺さる人には刺さるタイプのガジェットです。",
    "地味に困ってた人ほど、使い始めたら手放せなくなります。",
]

GADGET_GOOD_POINTS = [
    "このガジェットのいいところは、使い方を覚えなくていいところです。手に取ってすぐ使える。そういうシンプルさが毎日使い続けられる理由です。",
    "値段以上の満足感があります。安いからといって妥協感があるわけじゃなくて、これで十分と思えるクオリティがある。そういうものが一番コスパいいです。",
    "毎日使うものだから、細かい使い勝手が積み重なって大きな差になります。買うまで気にしてなかった部分が、使い始めると気になってたんだと分かる。",
    "シンプルな機能に絞ってあるものほど、長く使えます。あれもこれも詰め込んだものより、一つのことをちゃんとやってくれるものの方が信頼できる。",
]

GADGET_FEELINGS = [
    "使い始めると「なんで今まで持ってなかったんだろう」ってなるタイプのやつです。あって当たり前になるのが早い。",
    "毎日使ってると、地味にストレスが減ります。一個一個は小さいことですが、積み重なると違いが出てきます。",
    "思ったより使い続けてます。最初は「本当に使うかな」と思ってたのに、気づいたら毎日触ってる。そういうものです。",
    "使い心地がよくて、他のものに戻れなくなりました。同じカテゴリのものを見ても、これでいいやってなる。それが一番の評価だと思います。",
]

GADGET_SUMMARIES = [
    "毎日使うものを少しだけよくする。それだけで生活の快適さはちゃんと上がります。\n\n大げさな変化じゃなくていい。今日の1個が、毎日の地味なストレスを減らしてくれたら十分です。\n\n気になったら試してみてください。",
    "ガジェットは使ってみないと分からないことが多いですが、今日紹介したものは買って後悔しにくいタイプだと思います。\n\n毎日使うものだから、合うものを選ぶのは大事。少しでも参考になれば。",
    "小さな快適さの積み重ねが、毎日の気分を作ります。\n\nこれじゃないといけないわけじゃないけど、こういうものに手を伸ばしてみる、という習慣が生活をよくしていく気がします。\n\n合いそうなら、試してみてください。",
]


# ======================================================
# ユーティリティ
# ======================================================

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


def clean_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if any(stripped == p for p in DISCLAIMER_PATTERNS):
            continue
        if stripped.startswith("『") and stripped.endswith("』"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def first_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def rest_lines(text: str) -> str:
    lines = text.splitlines()
    found = False
    rest = []
    for line in lines:
        if not found and line.strip():
            found = True
            continue
        rest.append(line)
    return "\n".join(rest).strip()


def pick(templates: list) -> str:
    return random.choice(templates)


# ======================================================
# セクション構築
# ======================================================

def build_intro() -> str:
    return "\n\n".join([
        pick(INTRO_PAINS),
        pick(INTRO_EMPATHIES),
        pick(INTRO_BRIDGES),
    ])


def build_gadget_section(post: dict) -> str:
    title = post.get("title") or post.get("asin", "")
    raw_text = clean_text(post.get("text", ""))
    url = build_amazon_url(post)

    who_line = first_line(raw_text)
    body = rest_lines(raw_text)

    lines = [
        f"## 今日のガジェット｜{title}",
        "",
        "### こんな人に向いている",
        "",
        who_line,
        "",
        pick(GADGET_FOR_WHO_EXPANSIONS),
        "",
        "### ここがいい",
        "",
    ]
    if body:
        lines += [body, ""]
    lines += [
        pick(GADGET_GOOD_POINTS),
        "",
        "### 使ってみた感覚",
        "",
        pick(GADGET_FEELINGS),
        "",
        f"[Amazonで見る]({url})",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def build_summary() -> str:
    return "\n".join([
        "## まとめ",
        "",
        pick(GADGET_SUMMARIES),
    ])


# ======================================================
# 記事全体
# ======================================================

def build_article(gadget: dict) -> str:
    title = pick(TITLES)

    parts = [
        f"# {title}",
        "",
        build_intro(),
        "",
        "---",
        "",
        build_gadget_section(gadget),
        build_summary(),
        "",
        "---",
        "",
        "※ 本記事のリンクにはアフィリエイトが含まれます。",
    ]
    return "\n".join(parts)


# ======================================================
# エントリーポイント
# ======================================================

def main() -> None:
    gadgets = load_json(os.path.join(SCRIPT_DIR, "gadgets.json"))

    if not gadgets:
        raise ValueError("gadgets.json が空です。")

    today = today_jst()
    random.seed(today.toordinal())

    gadget = random.choice(gadgets)

    article = build_article(gadget)

    os.makedirs(ARTICLES_DIR, exist_ok=True)
    output_path = os.path.join(ARTICLES_DIR, f"gadget-{today.isoformat()}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(article)

    print(f"生成しました → {output_path}")
    print(f"タイトル: {article.splitlines()[0].lstrip('# ')}")


if __name__ == "__main__":
    main()
