import re
import sys
from pykakasi import kakasi

# ---------- 假名工具 ----------
kks = kakasi()
kks.setMode("J", "H")
conv = kks.getConverter()

def to_hiragana(text):
    return conv.do(text)

def contains_kanji(text):
    return any("\u4e00" <= c <= "\u9fff" for c in text)

def is_pure_katakana(text):
    return all("ァ" <= c <= "ヶ" or c in "ー・" for c in text if c.strip())


# ---------- 解析词头 ----------
def parse_headword(raw):
    manual_kana = None
    disable_kana = False

    # {no_kana}
    if "{no_kana}" in raw:
        raw = raw.replace("{no_kana}", "").strip()
        disable_kana = True

    # 提取 {}（只影响假名）
    m = re.search(r"\{(.+?)\}", raw)
    if m:
        manual_kana = m.group(1).strip()
        raw = re.sub(r"\{.+?\}", "", raw).strip()

    # 处理多个 |
    parts = [p.strip() for p in raw.split("|") if p.strip()]
    headword = parts[0]
    aliases = parts[1:]

    return headword, manual_kana, aliases, disable_kana


# ---------- 释义处理 ----------
def process_meaning(text):
    # [note](内容)
    def note_repl(m):
        return f'<p class="note">{m.group(1)}</p>'

    # [example](句子)(解释)
    def example_repl(m):
        return (
            '<p class="example">'
            f'<span class="example-sentence">{m.group(1)}</span>\t'
            f'<span class="example-explain">{m.group(2)}</span>'
            '</p>'
        )

    # 先处理自定义标签
    text = re.sub(r'\[note\]\((.+?)\)', note_repl, text)
    text = re.sub(r'\[example\]\((.+?)\)\((.+?)\)', example_repl, text)

    # 再处理加粗（保留 <br> 与自定义块）
    parts = re.split(
        r'(<br>|<p class="note">.*?</p>|<p class="example">.*?</p>|'
        r'，|；|、|\.|（|）|\[|\]|\+|「|」)',
        text
    )

    out = []
    for p in parts:
        if not p:
            continue
        if p == "<br>" or p.startswith("<p "):
            out.append(p)
        elif re.match(r"[，；、\.（）\[\]\+「」]", p):
            out.append(p)
        else:
            out.append(f"<b>{p.strip()}</b>")
    return "".join(out)


# ---------- 主转换 ----------
def convert(lines):
    output = []
    redirects = []
    i = 0

    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue

        headword_raw = lines[i].strip()
        meaning = lines[i + 1].strip() if i + 1 < len(lines) else ""
        i += 2

        headword, manual_kana, aliases, disable_kana = parse_headword(headword_raw)

        # ===== 显示假名 =====
        display_sub = None
        if not disable_kana:
            if manual_kana:
                display_sub = manual_kana
            elif contains_kanji(headword):
                display_sub = to_hiragana(headword)

        # ===== 重定向 =====
        redirect_keys = set()

        # | 指定的（永远生效）
        for a in aliases:
            redirect_keys.add(a)

        # {} 指定的（除非 no_kana）
        if manual_kana and not disable_kana:
            redirect_keys.add(manual_kana)

        # 自动假名（除非 no_kana / 有手动）
        if (
            not disable_kana
            and not manual_kana
            and contains_kanji(headword)
        ):
            redirect_keys.add(to_hiragana(headword))

        for key in redirect_keys:
            redirects.append(f"{key}\t{headword}")

        # ===== HTML 正文 =====
        html = ""
        if display_sub:
            html += f'<span class="pinyin_h">{display_sub}</span>'
        html += f'<p data-orgtag="meaning">{process_meaning(meaning)}</p>'

        output.append(f"{headword}\t{html}")

    return "\n".join(output), "\n".join(redirects)


# ---------- 入口 ----------
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python txt2mdx_html.py input.txt index.txt syns.txt")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        lines = f.readlines()

    index_txt, syns_txt = convert(lines)

    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(index_txt)

    with open(sys.argv[3], "w", encoding="utf-8") as f:
        f.write(syns_txt)

    print("转换完成 ✔")
