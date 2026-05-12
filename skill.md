---
name: random-walk-review
description: |
  每日知识库随机漫步。从 Obsidian 概念词条库中加权抽取词条，生成当日复习文件。
  越久未复习的词条权重越高，支持 checkbox 反馈（记住了/没记住），次日自动调整权重。

  触发条件：
  - 用户说"运行随机漫步"、"生成今日复习"、"random walk"
  - "/random-walk"
---

# Random Walk Review Skill

## 配置前提

用户需要先完成 `random_walk_generic.py` 顶部的路径配置：

```python
VAULT = Path("/your/obsidian/vault")
CONCEPTS_DIR = VAULT / "your/concepts/dir"
OUTPUT_DIR = VAULT / "随机漫步"
PICK_COUNT = 4
```

配置完成后，脚本路径记为 `SCRIPT`，后续步骤使用。

## 执行流程

### Step 1：运行脚本

```bash
python3 "$SCRIPT"
```

脚本幂等——今日文件已存在则跳过。

### Step 2：输出结果

告知用户今天抽到的词条列表，提示去 Obsidian 打开 `OUTPUT_DIR/YYYY-MM-DD.md`。

### Step 3：处理特殊指令

**"重新生成"：**
```bash
rm "$OUTPUT_DIR/$(date +%Y-%m-%d).md" && python3 "$SCRIPT"
```

**"统计昨天" / "看反馈"：**
读取昨日文件，统计 checkbox 状态，输出：
- 记住了 X 个
- 没记住 X 个
- 未标记 X 个

## 权重规则

| 状态 | 权重逻辑 |
|------|----------|
| 从未抽过 | 365，最高优先级 |
| 抽过未标记 | 距上次抽取天数 |
| 标记"记住了" | 推迟30天再出现 |
| 标记"没记住" | 重置为365，尽快再出现 |

## 用户操作说明

每个词条下方有两个 checkbox，在 Obsidian 中点击即可：

```
- [ ] 记住了：词条名
- [ ] 没记住：词条名
```

次日脚本运行时自动读取，无需额外操作。

## 自动触发设置（macOS）

```bash
crontab -e
# 添加：
0 8,12,20 * * * /usr/bin/python3 "/your/path/random_walk_generic.py" >> /tmp/random_walk.log 2>&1
```

Windows 用户使用任务计划程序替代。
