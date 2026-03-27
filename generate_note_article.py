"""
books.json / toys.json / fidgets.json を読み込み、
note 売れ筋構成（悩み→共感→解決）で Markdown 記事を articles/ に生成する。

各商品セクション構成:
  - こんな人に向いている
  - いいところ
  - 使ってみた感覚
  + 末尾に全体まとめ

同日に複数回実行しても同じ商品の組み合わせが選ばれる（日付シード）。
"""

import json
import os
import random
import urllib.parse
from datetime import datetime, timezone, timedelta
from typing import Optional

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
    "読んでよかった。『{book}』と、最近手放せないもの",
    "少しだけ変えたら、楽になった話——本・おもちゃ・手遊び",
    "なんとなくうまくいってない人へ。今日のピック",
    "手に取ってよかったもの、まとめて紹介します",
    "今日届けたい3つ。『{book}』ほか",
    "『{book}』を読んで気づいたこと——今日のおすすめ",
]

INTRO_PAINS = [
    "なんとなくうまくいってない感覚、ありませんか。",
    "毎日ちゃんとやってるつもりなのに、どこかがずっと噛み合わない。そういう時期があります。",
    "頑張ってるのに前に進んでる気がしない。焦るわけじゃないけど、何かが違う。",
    "やる気がないわけじゃない。でも、なぜかうまく回らない。",
    "最近ちょっと息切れしてる。そんな感覚、ないですか。",
]

INTRO_EMPATHIES = [
    "そういう時って、大きなことを変えようとするより、手元の小さなことを変えた方が早かったりする。大げさな決意じゃなくて、今日の一冊、机の上の一個。それくらいのことが、意外と続く。",
    "気合いで乗り越えようとしても長続きしない。仕組みや環境を少し変える方が、結果的に効く。自分がそれに気づいたのも、何かに手を伸ばしたことがきっかけだった。",
    "自分もそういう時期があって、本や道具に助けられることが多かった。特別なものじゃなくて、「これ試してみよう」と思えるものが一個あるだけで、気持ちの向きが少し変わる。",
    "何かを変えたい時って、きっかけはわりと小さいことだったりする。大きな決断じゃなくて、今日の気分に合う一冊を手に取るとか、机に何か置いてみるとか、それくらいのことが入り口になる。",
]

INTRO_BRIDGES = [
    "今日は、そういう時期に自分が頼った本と、毎日手元に置いているものを紹介します。気になるものがあれば、参考にしてみてください。",
    "今日ピックアップしたのは、そういう時期に特に効いたものです。全部じゃなくていい、一つでも引っかかるものがあれば。",
    "今日紹介するのは、本・おもちゃ・フィジェットの3ジャンルです。どれも売り込みたいわけじゃなくて、自分がよかったと思ったものを正直に書きます。",
    "そんな時に頼りにした本と、毎日使っているものをまとめてみました。読み物として流してもらえれば。",
]

# ---- 書籍：サブセクション ----

BOOK_FOR_WHO_EXPANSIONS = [
    "「自分のことかも」と思ったら、たぶん読むタイミングです。",
    "刺さる人は最初の数ページで分かります。そういうタイプの本です。",
    "ピンときたら手に取ってみてください。合う人にはかなり合います。",
    "引っかかりを感じたなら、読むサインだと思ってください。",
]

BOOK_GOOD_POINTS = [
    "この本のいいところは、背中を強く押してくるわけじゃないのに、読み終えると言い訳がしにくくなるところです。正論で詰めてくるタイプじゃなくて、気づいたら自分の考えが動いている感じ。そういう本はあとから効いてきます。",
    "派手な主張はないのに、核心だけはきっちり外さない。読んでいて気持ちいいというより、図星を静かに突かれる感覚に近い。それが読後にじわじわ残ります。",
    "テクニックを教えてくれる本じゃなくて、考え方の前提を整えてくれる本です。表面的なノウハウより先に、こういう本を読んでおくと後がラクになる。",
    "難しいことは言っていないのに、読んだあとに自分の扱い方が少し変わる。そういう本は多くないので、手元に置いておく価値があります。",
]

BOOK_FEELINGS = [
    "読み終えたあと、すぐに何かが変わるわけじゃないけど、視点が少しだけズレる感じがあります。それが数日後に効いてくる。焦らず読めるのもいいところです。",
    "読んでいる途中から「あ、これ自分のことだ」という感覚がきます。きれいごとじゃなく、ちゃんと痛い。でも読んだあと、少しだけ身軽になる。",
    "読後感は人によって違うと思いますが、少なくとも「読んでよかった」という感覚は残ります。それだけで十分な本もあります。",
    "最初は「知ってることだな」と思いながら読むかもしれない。でも知ってるのにやってない、というのがこの本の核心で、読むほどに言い訳が消えていきます。",
]

# ---- おもちゃ：サブセクション ----

TOY_FOR_WHO_EXPANSIONS = [
    "遊び心があるものを探してるなら、これは外しにくいです。",
    "理屈じゃなくて、触ってみると分かるタイプ。そういうものが長続きします。",
    "難しく考えなくていい。直感で「いいな」と思ったら、たぶん合います。",
    "子ども向けに見えて、大人が一番ハマるやつです。",
]

TOY_GOOD_POINTS = [
    "このジャンルのいいところは、頭を使わなくていいところです。本を読んだり考えたりする時間が長い人ほど、こういうシンプルに楽しいものが必要だったりする。気分転換の道具として、手元にあると助かります。",
    "単純だからこそ飽きにくい。複雑なものって最初だけ面白くて、だんだん使わなくなる。これくらいシンプルな方が、気がついたら触ってる、という状態が長続きします。",
    "デスク周りに一個あるだけで、仕事の密度が少し変わります。大げさじゃなくて、手の行き場ができるだけで集中が途切れにくくなる。そういう効果があります。",
    "値段の割に満足度が高い系のやつです。届いた瞬間は「こんなもんか」と思っても、気づいたら毎日触ってる。そういうものの方が長く使えます。",
]

TOY_FEELINGS = [
    "触り始めると止めどきが分からなくなります。それは欠点でもあるんですが、それくらい没入できるのは正直です。",
    "使ってみると、余計なことを考えなくなります。頭が静かになる感覚があって、それが意外と心地いい。",
    "遊んでいる、というより、手が動いてる、という感覚です。仕事の合間に使うと、次のタスクに入りやすくなる。",
    "気分転換のつもりで触り始めて、気づいたら5分経ってた。それくらい自然に使えます。",
]

# ---- フィジェット：サブセクション ----

FIDGET_FOR_WHO_EXPANSIONS = [
    "無意識に何かを触ってしまう人、スマホをだらだら開いてしまう人に特に合います。",
    "手持ち無沙汰が集中を妨げてると感じてる人向けです。",
    "考え事をしながら手を動かしたい人には、かなりフィットします。",
    "デスクで長時間作業する人の、地味に助かるやつです。",
]

FIDGET_GOOD_POINTS = [
    "フィジェットのいいところは、意識しなくても使えるところです。本を読んだり動画を見たりしながら触れる。何かをしながらできる、というのが大事で、それがスマホを無駄に触る代わりになってくれます。",
    "シンプルな動きに繰り返しがあるので、妙に落ち着きます。手が忙しいと、頭が静かになる。そういう感覚があって、作業の集中が続きやすくなります。",
    "触り心地がちゃんとしているものは、それだけで価値があります。安いものとの差は、使い続けるかどうかに出てくる。飽きずに机に置いておけるかどうかが基準です。",
    "小さいので場所を取らないし、音が気になるものでなければ職場でも使えます。持ち歩きもできるサイズ感のものが多くて、使う場面を選ばないのが強いです。",
]

FIDGET_FEELINGS = [
    "使い始めると、スマホを触る回数が自然と減ります。意識してやめようとするより、代わりになるものがあった方が早い。それがフィジェットの実質的な効果です。",
    "触ってる間、頭の中が少し静かになります。何かを考えながら触る、というより、触ってる間だけ余計なことを考えなくなる、そういう感じです。",
    "気づいたら触ってる、という状態が長続きします。それが良いフィジェットの条件で、使わなくなったら意味がない。飽きにくいものを選ぶのが大事です。",
    "最初は「こんなもので変わるのか」と思うかもしれません。でも1週間使ってみると、なんとなく手元にないと落ち着かなくなる。そういうものです。",
]

# ---- まとめ ----

SUMMARIES = [
    "今日紹介した3つは、どれも「ちょっとだけ変えたい」という気持ちに応えるものです。\n\n本で考え方を整えて、おもちゃやフィジェットで気分転換する。そういう小さなサイクルが、意外と長続きする日常をつくってくれます。\n\n全部買う必要はないので、気になったものだけ手に取ってみてください。",
    "一つ一つは小さなことですが、組み合わさると生活の質が少し上がる、そういうものを選びました。\n\n本は長く付き合える相棒になるし、手元に置くものは毎日の気分を変えてくれる。大げさな変化じゃなくても、積み重ねると違いが出てきます。\n\n今日の記事が、何かのきっかけになれば。",
    "今日紹介したものは、どれも「これがあれば全部解決」という大げさなものじゃありません。\n\nただ、手元に置いておくと少し気持ちが変わる。本を読むと視点が変わる。そういう地味な積み重ねが、あとから見ると大きな違いになっていたりします。\n\n合うものがあったら、試してみてください。",
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
    """JSON の投稿テキストからアフィリエイト注記と商品タイトル行（『』）を除去する。"""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if any(stripped == p for p in DISCLAIMER_PATTERNS):
            continue
        if stripped.startswith("『") and stripped.endswith("』"):
            continue
        lines.append(line)
    # 先頭・末尾の空行を取り除く
    return "\n".join(lines).strip()


def first_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def rest_lines(text: str) -> str:
    """先頭の非空行を除いた残りを返す。"""
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

def build_intro(book_title: str) -> str:
    return "\n\n".join([
        pick(INTRO_PAINS),
        pick(INTRO_EMPATHIES),
        pick(INTRO_BRIDGES),
    ])


def build_book_section(post: dict) -> str:
    title = post.get("title") or post.get("asin", "")
    raw_text = clean_text(post.get("text", ""))
    url = build_amazon_url(post)

    who_line = first_line(raw_text)        # 例：「〇〇な人、これ読んでほしい。」
    body = rest_lines(raw_text)            # 残りの本文

    lines = [
        f"## 本の紹介｜『{title}』",
        "",
        "### こんな人に向いている",
        "",
        who_line,
        "",
        pick(BOOK_FOR_WHO_EXPANSIONS),
        "",
        "### ここがいい",
        "",
    ]
    if body:
        lines += [body, ""]
    lines += [
        pick(BOOK_GOOD_POINTS),
        "",
        "### 読んだあとの感覚",
        "",
        pick(BOOK_FEELINGS),
        "",
        f"[Amazonで見る]({url})",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def build_toy_section(post: dict) -> str:
    title = post.get("title") or post.get("asin", "")
    raw_text = clean_text(post.get("text", ""))
    url = build_amazon_url(post)

    who_line = first_line(raw_text)
    body = rest_lines(raw_text)

    lines = [
        f"## おもちゃ・ガジェット｜{title}",
        "",
        "### こんな人に向いている",
        "",
        who_line,
        "",
        pick(TOY_FOR_WHO_EXPANSIONS),
        "",
        "### ここがいい",
        "",
    ]
    if body:
        lines += [body, ""]
    lines += [
        pick(TOY_GOOD_POINTS),
        "",
        "### 使ってみた感覚",
        "",
        pick(TOY_FEELINGS),
        "",
        f"[Amazonで見る]({url})",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def build_fidget_section(post: dict) -> str:
    title = post.get("title") or post.get("asin", "")
    raw_text = clean_text(post.get("text", ""))
    url = build_amazon_url(post)

    who_line = first_line(raw_text)
    body = rest_lines(raw_text)

    lines = [
        f"## フィジェット｜{title}",
        "",
        "### こんな人に向いている",
        "",
        who_line,
        "",
        pick(FIDGET_FOR_WHO_EXPANSIONS),
        "",
        "### ここがいい",
        "",
    ]
    if body:
        lines += [body, ""]
    lines += [
        pick(FIDGET_GOOD_POINTS),
        "",
        "### 使ってみた感覚",
        "",
        pick(FIDGET_FEELINGS),
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
        pick(SUMMARIES),
    ])


# ======================================================
# 記事全体
# ======================================================

def build_article(book: dict, toy: dict, fidget: Optional[dict], today) -> str:
    book_title = book.get("title") or book.get("asin", "")
    title = pick(TITLES).format(book=book_title)

    sections = [
        build_book_section(book),
        build_toy_section(toy),
    ]
    if fidget:
        sections.append(build_fidget_section(fidget))

    parts = [
        f"# {title}",
        "",
        build_intro(book_title),
        "",
        "---",
        "",
        *sections,
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
    books = load_json(os.path.join(SCRIPT_DIR, "books.json"))
    toys = load_json(os.path.join(SCRIPT_DIR, "toys.json"))
    fidgets = load_json(os.path.join(SCRIPT_DIR, "fidgets.json"))

    if not books:
        raise ValueError("books.json が空です。")
    if not toys:
        raise ValueError("toys.json が空です。")

    today = today_jst()  # GitHub Actions (UTC) でも JST 日付を使う
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
    print(f"タイトル: {article.splitlines()[0].lstrip('# ')}")


if __name__ == "__main__":
    main()
