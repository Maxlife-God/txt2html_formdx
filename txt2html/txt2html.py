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
    en_alias = None
    disable_kana = False

    if "|" in raw:
        raw, en_alias = raw.split("|", 1)
        en_alias = en_alias.strip()

    # 支持手动禁止假名生成
    if "{no_kana}" in raw:
        raw = raw.replace("{no_kana}", "").strip()
        disable_kana = True

    m = re.match(r"^(.*?)\{(.+?)\}$", raw)
    if m:
        headword = m.group(1).strip()
        manual_kana = m.group(2).strip()
    else:
        headword = raw.strip()

    return headword, manual_kana, en_alias, disable_kana

# ---------- 释义加粗（保留自定义标签） ----------
def process_meaning(text):
    # 处理 [note](内容)
    def note_repl(m):
        content = m.group(1)
        return f'<p class="note">{content}</p>'

    # 处理 [example](内容1)(内容2)
    def example_repl(m):
        content1 = m.group(1)
        content2 = m.group(2)
        return f'<p class="example"><span class="example-sentence">{content1}</span>&nbsp;<span class="example-explain">{content2}</span></p>'

    # 先处理自定义标签，避免被 <b> 包裹
    text = re.sub(r'\[note\]\((.+?)\)', note_repl, text)
    text = re.sub(r'\[example\]\((.+?)\)\((.+?)\)', example_repl, text)

    # 然后加粗普通文本，保留 <br> 标签
    parts = re.split(r"(<br>|<p class=\"note\">.*?</p>|<p class=\"example\">.*?</p>|，|；|、|\.|（|）|\[|\]|\+|「|」)", text)
    out = []
    for p in parts:
        if not p:
            continue
        # 跳过自定义标签或换行
        if p.startswith('<p class="note">') or p.startswith('<p class="example">') or p == "<br>":
            out.append(p)
        elif re.match(r"[，；、\.（）\[\]\+「」]", p):
            out.append(p)
        elif p.strip():
            out.append(f"<b>{p.strip()}</b>")
    return "".join(out)

# ---------- 主转换 ----------
def convert(lines):
    output = []
    redirects = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        headword_raw = line
        meaning = lines[i + 1].strip() if i + 1 < len(lines) else ""
        i += 2

        headword, manual_kana, en_alias, disable_kana = parse_headword(headword_raw)
        pure_katakana = is_pure_katakana(headword)

        # ---------- 决定显示副文本 ----------
        display_sub = None
        if not disable_kana:
            if manual_kana:
                display_sub = manual_kana
            elif pure_katakana and en_alias:
                display_sub = en_alias            # 英文，原样显示
            elif contains_kanji(headword):
                display_sub = to_hiragana(headword)

        # ---------- 重定向 ----------
        if contains_kanji(headword) and display_sub:
            redirects.append(f"{display_sub}\t{headword}")
        if pure_katakana and en_alias:
            redirects.append(f"{en_alias}\t{headword}")

        # ---------- HTML 正文 ----------
        html_parts = []
        if display_sub:
            html_parts.append(f'<span class="pinyin_h">{display_sub}</span>')
        html_parts.append(f'<p data-orgtag="meaning">{process_meaning(meaning)}</p>')
        html_content = "".join(html_parts)

        # 输出单行 txt
        output.append(f"{headword}\t{html_content}")

    return "\n".join(output), "\n".join(redirects)

# ---------- 入口 ----------
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python txt2mdx_html.py input.txt index.txt syns.txt")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        lines = f.readlines()

    result_txt, result_syns = convert(lines)

    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(result_txt)

    with open(sys.argv[3], "w", encoding="utf-8") as f:
        f.write(result_syns)

    print("转换完成 ✔")
