#!/usr/bin/env python3
"""随机漫步：从概念词条中加权抽取，优先复习最久未看的词条"""

import json
import random
import re
from datetime import date, timedelta
from pathlib import Path

# ── 用户配置区 ──────────────────────────────────────────────
VAULT = Path("/your/obsidian/vault")          # Obsidian Vault 根目录
CONCEPTS_DIR = VAULT / "your/concepts/dir"   # 概念词条目录（每个词条一个 .md 文件）
OUTPUT_DIR = VAULT / "随机漫步"               # 每日复习文件输出目录
PICK_COUNT = 4                                # 每次抽取数量
# ────────────────────────────────────────────────────────────

HISTORY_FILE = OUTPUT_DIR / ".history.json"


def load_history() -> dict:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return {}


def save_history(history: dict):
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2))


def pick_concepts(history: dict) -> list[Path]:
    all_concepts = list(CONCEPTS_DIR.glob("*.md"))
    if not all_concepts:
        raise RuntimeError("概念词条目录为空")

    today_str = str(date.today())

    def weight(p: Path) -> int:
        last = history.get(p.name)
        if not last:
            return 365
        delta = (date.today() - date.fromisoformat(last)).days
        return max(delta, 1)

    weights = [weight(p) for p in all_concepts]
    count = min(PICK_COUNT, len(all_concepts))
    picked = random.choices(all_concepts, weights=weights, k=count * 3)

    seen = set()
    result = []
    for p in picked:
        if p.name not in seen:
            seen.add(p.name)
            result.append(p)
        if len(result) == count:
            break

    for p in result:
        history[p.name] = today_str

    return result


def build_markdown(concepts: list[Path]) -> str:
    today = date.today().isoformat()
    lines = [f"# 随机漫步 {today}\n", f"> 今天抽到 {len(concepts)} 个概念，看几条算几条。\n"]

    for i, path in enumerate(concepts, 1):
        content = path.read_text(encoding="utf-8").strip()
        if content.startswith("---"):
            parts = content.split("---", 2)
            body = parts[2].strip() if len(parts) >= 3 else content
        else:
            body = content
        indented = "\n".join(f"> {line}" for line in body.splitlines())
        lines.append(f"\n---\n\n> [!question]- {i}. {path.stem}（点击展开答案）\n{indented}")
        lines.append(f"\n- [ ] 记住了：{path.stem}\n- [ ] 没记住：{path.stem}")

    return "\n".join(lines)


def parse_feedback(file: Path) -> dict[str, bool]:
    if not file.exists():
        return {}
    text = file.read_text(encoding="utf-8")
    result = {}
    for m in re.finditer(r"- \[([ x])\] (记住了|没记住)：(.+)", text):
        checked = m.group(1) == "x"
        label = m.group(2)
        name = m.group(3).strip() + ".md"
        if checked:
            result[name] = (label == "记住了")
    return result


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    output_file = OUTPUT_DIR / f"{today}.md"

    if output_file.exists():
        print(f"今日文件已存在，跳过：{output_file}")
        return

    history = load_history()

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    yesterday_file = OUTPUT_DIR / f"{yesterday}.md"
    feedback = parse_feedback(yesterday_file)
    for name, remembered in feedback.items():
        if remembered:
            history[name] = (date.today() + timedelta(days=30)).isoformat()
        else:
            history.pop(name, None)

    concepts = pick_concepts(history)
    md = build_markdown(concepts)
    output_file.write_text(md, encoding="utf-8")
    save_history(history)

    print(f"已生成：{output_file}")
    print(f"本次复习：{[p.stem for p in concepts]}")


if __name__ == "__main__":
    main()
