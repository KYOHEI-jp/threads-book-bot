"""
アフィリエイト用の商品JSONを対話形式で生成し、books.json / toys.json / fidgets.json に追記するスクリプト。
"""

import json
import random
import os
import urllib.parse

STORE_ID = "aoga101903-22"


def build_affiliate_url(asin: str) -> str:
    return f"https://www.amazon.co.jp/dp/{asin}?tag={STORE_ID}"


def build_search_url(title: str) -> str:
    return f"https://www.amazon.co.jp/s?k={urllib.parse.quote(title)}&tag={STORE_ID}"

# ---- 書籍用テンプレート ----

BOOK_TARGET_LINES = [
    "「{hook}」人、これ読んでほしい。",
    "最近ずっと「{hook}」感覚があるなら、この本はかなり残ると思う。",
    "もし今「{hook}」状態なら、一回この本に触れてみてほしい。",
    "いま「{hook}」ところで止まってる人に向いてる一冊。",
]

BOOK_MIDDLES = [
    "正直、毎日ちゃんとやってるつもりでも、どこかで噛み合ってない感覚ってある。",
    "頑張ってるのに報われない時って、能力よりも見ている場所がズレていることが多い。",
    "気合いで押し切ろうとしても続かない時は、やり方ではなく前提が間違っていることがある。",
    "表面だけ整えても苦しさが消えないのは、根っこの考え方がそのままだからだと思う。",
]

BOOK_REACTIONS = [
    "説教くさくないのに、読んだあと言い訳しづらくなるのが厄介でいい。",
    "派手なことは言わないのに、核心だけはきっちり外さない。",
    "読んでいて気持ちいいというより、図星を静かに突かれる感覚に近い。",
    "都合よく励ましてはくれないけど、その分ちゃんと残る。",
]

BOOK_CLOSINGS = [
    "いま少しでも引っかかるなら、たぶん読むタイミングなんだと思う。",
    "すぐ人生が変わるとかは言わない。でも、見方は確実に変わる。",
    "大げさじゃなく、読後に自分の扱い方が少し変わる本。",
    "読んだあと、次の一歩の置き方が少しだけ変わる。",
]

# ---- フィジェット専用テンプレート ----

FIDGET_TARGETS = [
    "{target}、これかなりいい。",
    "{target}、これ合う。",
    "{target}、これ試してほしい。",
    "{target}、これはまる。",
]

FIDGET_SENSATIONS = [
    "{sensation}だけなのに、気づいたらずっと触ってる。",
    "{sensation}という動きが、妙にクセになる。",
    "{sensation}感覚が、思ってるより落ち着く。",
    "{sensation}だけのシンプルさが、逆にちょうどいい。",
]

FIDGET_EFFECTS = [
    "無駄なスマホ触りが自然と減る。",
    "集中のスイッチとして使う人が多い。",
    "手持ち無沙汰をそのまま解消できる。",
    "考え事との相性がいい。",
]

FIDGET_PLACEMENTS = [
    "デスクに常設しておくタイプ。",
    "持ち歩きやすいサイズ感。",
    "外でも自然に使えるのが強い。",
    "机にひとつあると地味に助かる。",
]

FIDGET_CLOSINGS = [
    "地味だけど、ないと困るやつ。",
    "使い始めると手放しにくい。",
    "シンプルなものほど長く続く。",
    "飽きにくいのがいちばんの強み。",
]


def generate_fidget_text(title: str, sensation: str, target: str, placement: str) -> str:
    seed = hash(title + sensation) & 0xFFFFFF
    random.seed(seed)
    lines = [
        random.choice(FIDGET_TARGETS).format(target=target),
        "",
        random.choice(FIDGET_SENSATIONS).format(sensation=sensation),
        "",
        f"『{title}』",
        "",
        random.choice(FIDGET_EFFECTS),
        random.choice(FIDGET_PLACEMENTS).replace("デスクに常設しておくタイプ。", placement + "。") if placement else random.choice(FIDGET_PLACEMENTS),
        random.choice(FIDGET_CLOSINGS),
        "",
        "※リンクはアフィリエイトを含みます",
    ]
    return "\n".join(lines)


# ---- おもちゃ・ガジェット用テンプレート ----

TOY_TARGETS = [
    "{target}、これかなりいい。",
    "{target}、これ合うと思う。",
    "{target}、これ試してほしい。",
    "{target}、これいい。",
]

TOY_MIDDLES = [
    "シンプルなのに気づいたらずっと触ってる。",
    "単純だからこそ、疲れてる時でも使える。",
    "見た目よりずっと遊べる。",
    "結局、直感で使えるものは飽きにくい。",
]

TOY_INSIGHTS = [
    "こういう無駄に楽しい物って意外と残る。",
    "手持ち無沙汰はかなり減る。",
    "触りながら思考できるのがいい。",
    "机にひとつ置いとくと助かる。",
]

TOY_CLOSINGS = [
    "地味だけど、ひとつ置いておくと便利。",
    "ひとつあると、なんだかんだ触ってる。",
    "デスクに置いとくとちょうどいい。",
    "気軽に使えるのもポイント。",
]


def generate_book_text(title: str, theme: str, hook: str, core: str) -> str:
    seed = hash(title + hook) & 0xFFFFFF
    random.seed(seed)
    lines = [
        random.choice(BOOK_TARGET_LINES).format(hook=hook),
        "",
        random.choice(BOOK_MIDDLES),
        "",
        f"『{title}』",
        "",
        f"この本は「{core}」という話を、自分の生活に引き寄せて考えられる形で置いてくれる。",
        random.choice(BOOK_REACTIONS),
        f"特に{theme}で迷っている時ほど、考え方の軸を整える必要があると気づかされる。",
        "",
        random.choice(BOOK_CLOSINGS),
        "",
        "※本リンクはアフィリエイトを含みます",
    ]
    return "\n".join(lines)


def generate_toy_text(title: str, feature: str, target: str) -> str:
    seed = hash(title + feature) & 0xFFFFFF
    random.seed(seed)
    lines = [
        random.choice(TOY_TARGETS).format(target=target),
        "",
        random.choice(TOY_MIDDLES),
        "",
        f"『{title}』",
        "",
        f"{feature}。",
        random.choice(TOY_INSIGHTS),
        random.choice(TOY_CLOSINGS),
        "",
        "※リンクはアフィリエイトを含みます",
    ]
    return "\n".join(lines)


def load_json(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def prompt(label: str, required: bool = True) -> str:
    while True:
        value = input(f"  {label}: ").strip()
        if value or not required:
            return value
        print("  ※ 必須項目です。入力してください。")


def _preview_and_save(entry: dict, affiliate_url: str, output_path: str) -> None:
    print("\n--- プレビュー ---")
    if entry.get("text"):
        print(entry["text"])
        print()
    print(f"アフィリエイトURL: {affiliate_url}")
    print("-" * 30)

    filename = os.path.basename(output_path)
    confirm = input(f"\nこの内容で {filename} に追記しますか？ [y/N]: ").strip().lower()
    if confirm != "y":
        print("キャンセルしました。")
        return

    data = load_json(output_path)
    data.append(entry)
    save_json(output_path, data)
    print(f"追記しました → {output_path}（計 {len(data)} 件）")


def add_book(output_path: str) -> None:
    print("\n--- 書籍情報を入力してください ---")
    asin  = prompt("ASIN（例: B09XYZ1234、省略可）", required=False)
    title = prompt("タイトル（省略可）" if asin else "タイトル（例: 嫌われる勇気）", required=not asin)

    url_only = asin and not title
    text = ""

    if not url_only:
        required = not asin
        theme = prompt("テーマ（例: 人間関係、習慣、お金）" + ("、省略可" if asin else ""), required=required)
        hook  = prompt("対象読者の悩み（例: 人にどう思われるかで疲れてる）" + ("、省略可" if asin else ""), required=required)
        core  = prompt("本の核心メッセージ（例: 他人の評価を生きる軸にしない）" + ("、省略可" if asin else ""), required=required)
        if title and theme and hook and core:
            text = generate_book_text(title, theme, hook, core)

    entry = {"title": title, "text": text}
    if asin:
        entry["asin"] = asin

    affiliate_url = build_affiliate_url(asin) if asin else build_search_url(title)
    _preview_and_save(entry, affiliate_url, output_path)


def add_toy(output_path: str) -> None:
    print("\n--- おもちゃ・ガジェット情報を入力してください ---")
    asin    = prompt("ASIN（例: B09XYZ1234、省略可）", required=False)
    title   = prompt("タイトル（省略可）" if asin else "タイトル（例: フィジェットキューブ）", required=not asin)

    url_only = asin and not title
    text = ""

    if not url_only:
        required = not asin
        feature = prompt("特徴・説明（例: 触るだけなのに妙に落ち着く）" + ("、省略可" if asin else ""), required=required)
        target  = prompt("対象ユーザー（例: 手が暇でついスマホ触る人）" + ("、省略可" if asin else ""), required=required)
        if title and feature and target:
            text = generate_toy_text(title, feature, target)

    entry = {"title": title, "text": text}
    if asin:
        entry["asin"] = asin

    affiliate_url = build_affiliate_url(asin) if asin else build_search_url(title)
    _preview_and_save(entry, affiliate_url, output_path)


def add_fidget(output_path: str) -> None:
    print("\n--- フィジェット情報を入力してください ---")
    asin      = prompt("ASIN（例: B09XYZ1234、省略可）", required=False)
    title     = prompt("タイトル（省略可）" if asin else "タイトル（例: マグネットフィジェットボール）", required=not asin)

    url_only = asin and not title
    text = ""

    if not url_only:
        required = not asin
        sensation = prompt("触り心地・動作（例: 磁石でカチッと止まる）" + ("、省略可" if asin else ""), required=required)
        target    = prompt("対象ユーザー（例: 手遊びしながら考えたい人）" + ("、省略可" if asin else ""), required=required)
        placement = prompt("置き場所・携帯性（例: デスクワーク向け、省略可）", required=False)
        if title and sensation and target:
            text = generate_fidget_text(title, sensation, target, placement)

    entry = {"title": title, "text": text}
    if asin:
        entry["asin"] = asin

    affiliate_url = build_affiliate_url(asin) if asin else build_search_url(title)
    _preview_and_save(entry, affiliate_url, output_path)


def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("アフィリエイト商品JSON生成ツール")
    print("カテゴリを選択してください:")
    print("  1. 書籍 → books.json")
    print("  2. おもちゃ・ガジェット → toys.json")
    print("  3. フィジェット → fidgets.json")

    choice = input("選択 [1/2/3]: ").strip()

    if choice == "1":
        add_book(os.path.join(script_dir, "books.json"))
    elif choice == "2":
        add_toy(os.path.join(script_dir, "toys.json"))
    elif choice == "3":
        add_fidget(os.path.join(script_dir, "fidgets.json"))
    else:
        print("無効な選択です。1、2、または 3 を入力してください。")


if __name__ == "__main__":
    main()
