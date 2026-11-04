#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v0.3 外部投放包生成器 (G3: 路径相对化)
从本脚本所在位置解析所有相对路径，不依赖任何绝对路径或外部软链接。
可用环境变量 WF_V03_ROOT 覆盖包根目录。
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.environ.get("WF_V03_ROOT", os.path.join(HERE, os.pardir)))
PKG = os.path.join(ROOT, "规划流程模拟包_v0.3")
STAGE = os.path.join(PKG, "分轮投放_SYN102")
TPL = os.path.join(PKG, "Run_Template")
DESIGN = os.path.join(PKG, "评测设计_SYN102")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    if not os.path.isdir(STAGE):
        sys.exit("找不到投放材料目录: %s" % STAGE)

    agents = read(os.path.join(TPL, "AGENTS.md"))
    r1 = read(os.path.join(STAGE, "01_初始背景_SYN102.md"))
    r2 = read(os.path.join(STAGE, "02_学业材料_SYN102.md"))
    r3 = read(os.path.join(STAGE, "03_两国模拟规则_SYN102.md"))
    r4 = read(os.path.join(STAGE, "04_预算与规则更新_SYN102.md"))

    # ---------- 版本 A：文件读写型 ----------
    a = []
    a.append("# 外部投放包 · 版本 A（文件读写型客户端）\n")
    a.append("> 适用：Claude Code、Codex CLI、Gemini CLI 等**能读写本地工作目录**的客户端。\n")
    a.append("> 案例：SYN-UG-102（弱引导虚构案例）｜基准对照：AutoRun03（15/15 PASS）\n")
    a.append("\n## 0. 前置准备\n")
    a.append("```bash")
    a.append("# 在本模拟包根目录下执行；RUN 目录名自定，一次投放用一个新目录，不要覆盖旧结果")
    a.append("mkdir -p RUN_SYN102")
    a.append("cp Run_Template/AGENTS.md RUN_SYN102/AGENTS.md")
    a.append("cp 分轮投放_SYN102/01_初始背景_SYN102.md RUN_SYN102/01_虚构学生初始资料.md")
    a.append("```")
    a.append("\n把 `RUN_SYN102/` 的**绝对路径**记为 `<RUN_DIR>`，下文所有提示词中的 `{RUN_DIR}` 需替换为它。\n")
    a.append("\n### 每轮投放前的文件准备（关键，别漏）\n")
    a.append("本形态由客户端自主读取运行目录，**每轮投放前必须先把该轮材料拷入 `<RUN_DIR>`**：\n")
    a.append("| 轮次 | 投放前需执行 |")
    a.append("| :--- | :--- |")
    a.append("| 第 1 轮 | 已完成（AGENTS.md + 01_虚构学生初始资料.md） |")
    a.append("| 第 2 轮 | 无需拷文件（同一会话回答提问） |")
    a.append("| 第 3 轮 | `cp 分轮投放_SYN102/02_学业材料_SYN102.md <RUN_DIR>/02_学业材料.md` |")
    a.append("| 第 4 轮 | `cp 分轮投放_SYN102/03_两国模拟规则_SYN102.md <RUN_DIR>/03_两国模拟规则.md` |")
    a.append("| 第 5 轮 | 无需拷文件（**开启全新会话**，仅靠目录文件接续） |")
    a.append("| 第 6 轮 | `cp 分轮投放_SYN102/04_预算与规则更新_SYN102.md <RUN_DIR>/04_预算与规则更新.md` |")
    a.append("\n> 拷贝后建议核对哈希：`shasum -a 256 <RUN_DIR>/02_学业材料.md` 应与 `MANIFEST.json` 中"
             "`分轮投放_SYN102/02_学业材料_SYN102.md` 的值一致，确保材料未被编辑器改写。\n")
    a.append("\n## 1. 投放纪律（务必遵守）\n")
    a.append("1. 每一轮**单独一个会话轮次**，按顺序投放，不要合并、不要跳轮；")
    a.append("2. 同一会话内不要中途改写已投放的材料；")
    a.append("3. 第 5 轮必须**开启全新会话**（清空上下文），以验证纯文件接续能力；")
    a.append("4. 全程不得向被测客户端提供本包内的 `评测设计_SYN102/`（含标准核对答案与评分量表），否则构成强引导污染；")
    a.append("5. 不联网、不安装、不提交任何真实申请。\n")

    turns = [
        ("第 1 轮 · 初始化与概念澄清（新建会话）", "AGENTS.md + 01_虚构学生初始资料.md",
         "你的授权工作目录为：{RUN_DIR}。请仅在此目录工作。实际读取本目录下的 AGENTS.md 和 01_虚构学生初始资料.md。"
         "不要读取上级/相邻文件夹或其他聊天。说明你实际能读取、计算、保存什么。按当前阶段分批提问（每次1–3题），"
         "帮助我明确本轮要比较的内容；我不清楚的概念请先解释，不要替我编造偏好。"),
        ("第 2 轮 · 回答澄清问题（同一会话）", "无新材料",
         "1. 硕士培养导向：我不了解两种硕士日常的实际区别，暂时不选，先保持未知；博士也未决定。做过校内信管系统小组作业，无正式科研实习。\n"
         "2. 目的地候选范围：目的地未定，本次只依据后续提供的模拟规则比较，不借用现实国家或学校。\n"
         "3. 优先级权衡：希望找到喜欢且能就业的方向，也看重长期居留；还不能精确排序，希望通过比较看清取舍。排名有参考价值，但没有 QS 前100 之类的硬门槛。\n"
         "先到这里。请把这些记录为当前事实、偏好与未知，不影响本轮比较的问题先留待后续。完成当前记录后，等待我提供学业材料。"),
        ("第 3 轮 · 学业材料与重修情景", "02_学业材料.md",
         "现提供本目录的 02_学业材料.md。请分析我的学业现状与目前成绩水平；并测算若我大三重修高等数学达到82分以上时，"
         "对目前成绩会产生什么影响。说明哪些是实绩、哪些仍是目标，保留我的原始记录，并实际更新本工作区的记录文件。"
         "完成后向我汇报核心计算与分析结论。"),
        ("第 4 轮 · 两国规则全链条比对", "03_两国模拟规则.md",
         "现提供本目录的 03_两国模拟规则.md。请仅依据这个虚构规则包和当前个案，结合我的背景与预算，对兰泽国C与沧澜国D两条路线进行全链条对比分析，"
         "说明各自优劣与未决条件，给出你的分析建议，并实际写入并更新本工作区四份状态文件（CASE.md、EVIDENCE.md、CHECKPOINT.md、CHANGELOG.md）。"
         "完成后向我汇报核心比较结论。"),
        ("第 5 轮 · 纯文件接续（**必须开启全新会话**）", "仅目录文件，不再提供材料",
         "请仅从我提供的 {RUN_DIR} 目录文件继续 SYN-UG-102 虚构试验。先实际读取本目录下的 AGENTS.md、CHECKPOINT.md 和必要的关联材料。"
         "能读取与不能读取的部分请说明。不要重新做完整背景访谈。请先说清：目前这个学生的目标、确认资金与未确认资金、已修成绩和重修目标的区别、"
         "国家选择状态、当前未决问题，以及下一步。接续阶段先不用采取新的外部行动。汇报后等待我的后续指令。"),
        ("第 6 轮 · 动态更新与前瞻推演（接续会话）", "04_预算与规则更新.md",
         "现提供本目录的 04_预算与规则更新.md。模拟时钟推进到 2026-11-20。请读取更新，识别它改变了哪些事实和规则，以及影响哪些既有结论。"
         "重新计算预算与两条路线的关系，分析各项时间节点的作用。如果两条路线按原计划都无法成立，请如实说明并给出有依据的调整建议，"
         "不要强行选一个胜者。更新四份记录文件并保留历史变更原因（CHECKPOINT 保持最新单点状态，严禁全文嵌套）。完成更新后向我汇报。"),
    ]

    a.append("\n## 2. 六轮投放提示词（逐轮复制）\n")
    for title, mat, prompt in turns:
        a.append("\n### %s\n" % title)
        a.append("**本轮新增材料**：%s\n" % mat)
        a.append("```text\n%s\n```\n" % prompt)

    a.append("\n## 3. 回收清单\n")
    a.append("投放结束后，请从 `<RUN_DIR>` 收集：\n")
    a.append("- `AGENTS.md`、`01_虚构学生初始资料.md` ~ `04_预算与规则更新.md`（输入留档）")
    a.append("- `CASE.md`、`EVIDENCE.md`、`CHECKPOINT.md`、`CHANGELOG.md`（**四份状态文件落盘产物**）")
    a.append("- 每轮客户端回复的原始文本（保存为 `轮次记录.md` 或截图）\n")
    a.append("连同元数据填写 `评测设计_SYN102/04_外部投放结果记录表_SYN102.md`。\n")
    a.append("\n## 4. 独立复核纪律\n")
    a.append("**不要让被测客户端给自己打分。** 评分必须由评测者依据落盘文件与轮次原始记录，对照 "
             "`评测设计_SYN102/03_评分量表与复核模板_SYN102.md` 逐项判定（15 项）。\n")

    with open(os.path.join(TPL, "03_外部投放包_文件读写版.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(a))

    # ---------- 版本 B：纯粘贴 + 手动保存型 ----------
    b = []
    b.append("# 外部投放包 · 版本 B（纯粘贴 + 手动保存型客户端）\n")
    b.append("> 适用：ChatGPT、Claude 网页版、豆包、Kimi 等**不能读写本地目录**的客户端。\n")
    b.append("> 案例：SYN-UG-102（弱引导虚构案例）｜基准对照：AutoRun03（15/15 PASS）\n")
    b.append("\n## 0. 本版本与版本 A 的关键差异\n")
    b.append("版本 A 依赖客户端自主读写目录；本版本**由你手工把每轮的答复文本存成文件**，"
             "因此「状态文件规范落盘」与「CHECKPOINT 瘦身」两项无法由被测端自动证明，"
             "需由评测者**直接检查你保存下来的文件本体**（体积、嵌套、字段完整性），而非依赖被测端自述。\n")
    b.append("\n## 1. 投放纪律（务必遵守）\n")
    b.append("1. 每一轮**单独一个会话轮次**，按顺序投放，不要合并、不要跳轮；")
    b.append("2. 第 5 轮必须**开启全新会话**（清空上下文），以验证纯文件接续能力；")
    b.append("3. 在全新会话中，你需要把上一轮保存的四份文件**作为附件或正文重新喂给客户端**——"
             "本版本模拟的是「只能读到你提供的内容」的客户端，这是该形态的固有限制，应如实记录为观察项；")
    b.append("4. 全程不得向被测客户端提供本包内的 `评测设计_SYN102/`（含标准核对答案与评分量表）；")
    b.append("5. 不联网、不提交任何真实申请。\n")
    b.append("\n## 2. 建目录与首投（客户端无文件能力时的准备）\n")
    b.append("```bash")
    b.append("mkdir -p RUN_SYN102_PASTE")
    b.append("```")
    b.append("\n把 `Run_Template/AGENTS.md` 全文作为**第一条消息**发送给客户端（它是全程约束），然后依次粘贴下列各轮。\n")
    b.append("\n### 第 0 步 · 发送约束文件（全文粘贴）\n")
    b.append("```text\n%s\n```\n" % agents)

    inline = [
        ("第 1 轮 · 初始化与概念澄清（新建会话）", r1,
         "你的授权工作目录为：{RUN_DIR}。请仅在此目录工作。实际读取本目录下的 AGENTS.md 和 01_虚构学生初始资料.md。"
         "不要读取上级/相邻文件夹或其他聊天。说明你实际能读取、计算、保存什么。按当前阶段分批提问（每次1–3题），"
         "帮助我明确本轮要比较的内容；我不清楚的概念请先解释，不要替我编造偏好。\n\n"
         "以下是 01_虚构学生初始资料.md 的全文：\n\n<<<MATERIAL_01>>>"),
        ("第 2 轮 · 回答澄清问题（同一会话）", None,
         "1. 硕士培养导向：我不了解两种硕士日常的实际区别，暂时不选，先保持未知；博士也未决定。做过校内信管系统小组作业，无正式科研实习。\n"
         "2. 目的地候选范围：目的地未定，本次只依据后续提供的模拟规则比较，不借用现实国家或学校。\n"
         "3. 优先级权衡：希望找到喜欢且能就业的方向，也看重长期居留；还不能精确排序，希望通过比较看清取舍。排名有参考价值，但没有 QS 前100 之类的硬门槛。\n"
         "先到这里。请把这些记录为当前事实、偏好与未知，不影响本轮比较的问题先留待后续。完成当前记录后，等待我提供学业材料。"),
        ("第 3 轮 · 学业材料与重修情景", r2,
         "现提供 02_学业材料.md。请分析我的学业现状与目前成绩水平；并测算若我大三重修高等数学达到82分以上时，"
         "对目前成绩会产生什么影响。说明哪些是实绩、哪些仍是目标，保留我的原始记录，并给出你建议保存的记录文件内容。"
         "完成后向我汇报核心计算与分析结论。\n\n<<<MATERIAL_02>>>"),
        ("第 4 轮 · 两国规则全链条比对", r3,
         "现提供 03_两国模拟规则.md。请仅依据这个虚构规则包和当前个案，结合我的背景与预算，对兰泽国C与沧澜国D两条路线进行全链条对比分析，"
         "说明各自优劣与未决条件，给出你的分析建议，并给出你建议保存的四份状态文件内容"
         "（CASE.md、EVIDENCE.md、CHECKPOINT.md、CHANGELOG.md）的完整正文。完成后向我汇报核心比较结论。\n\n<<<MATERIAL_03>>>"),
        ("第 5 轮 · 纯文件接续（**必须开启全新会话**）", None,
         "请仅从我提供的 {RUN_DIR} 目录文件继续 SYN-UG-102 虚构试验。先实际读取本目录下的 AGENTS.md、CHECKPOINT.md 和必要的关联材料。"
         "能读取与不能读取的部分请说明。不要重新做完整背景访谈。请先说清：目前这个学生的目标、确认资金与未确认资金、已修成绩和重修目标的区别、"
         "国家选择状态、当前未决问题，以及下一步。接续阶段先不用采取新的外部行动。汇报后等待我的后续指令。\n\n"
         "<<<ATTACH_PREVIOUS_STATE>>>"),
        ("第 6 轮 · 动态更新与前瞻推演（接续会话）", r4,
         "现提供 04_预算与规则更新.md。模拟时钟推进到 2026-11-20。请读取更新，识别它改变了哪些事实和规则，以及影响哪些既有结论。"
         "重新计算预算与两条路线的关系，分析各项时间节点的作用。如果两条路线按原计划都无法成立，请如实说明并给出有依据的调整建议，"
         "不要强行选一个胜者。给出你更新后的四份记录文件内容并保留历史变更原因（CHECKPOINT 保持最新单点状态，严禁全文嵌套）。完成更新后向我汇报。\n\n<<<MATERIAL_04>>>"),
    ]

    b.append("\n## 3. 六轮投放提示词（逐轮复制）\n")
    for title, mat, prompt in inline:
        b.append("\n### %s\n" % title)
        if mat is None:
            b.append("```text\n%s\n```\n" % prompt)
        else:
            tag = "<<<MATERIAL_%s>>>" % ("01" if mat is r1 else "02" if mat is r2 else "03" if mat is r3 else "04")
            if tag not in prompt:
                sys.exit("提示词缺少材料占位符: %s (%s)" % (title, tag))
            body = prompt.replace(tag, "```\n" + mat + "\n```")
            b.append("```text\n%s\n```\n" % body)

    b.append("\n## 4. 手工保存清单（每轮必做）\n")
    b.append("| 轮次 | 需保存的文件 | 说明 |")
    b.append("| :--- | :--- | :--- |")
    b.append("| 1 | `01_虚构学生初始资料.md` | 初始资料留档 |")
    b.append("| 2 | `CASE.md`（初版） | 记录澄清后的事实/偏好/未知 |")
    b.append("| 3 | `CASE.md`、`EVIDENCE.md`、`CHECKPOINT.md`、`CHANGELOG.md` | 学业测算与情景落盘 |")
    b.append("| 4 | 同上（覆盖更新） | 两国比对与制度断点落盘 |")
    b.append("| 5 | —（只读验证） | 新会话接续，验证零遗忘 |")
    b.append("| 6 | 同上（覆盖更新） | 预算收紧与新规推演落盘 |")
    b.append("\n每轮保存后**用命令核验体积**（CHECKPOINT 硬上限 4,000 字节）：\n")
    b.append("```bash")
    b.append("wc -c RUN_SYN102_PASTE/*.md")
    b.append("grep -c \"CHECKPOINT\" RUN_SYN102_PASTE/CHECKPOINT.md   # 检查是否嵌套旧 CHECKPOINT 全文")
    b.append("```\n")

    b.append("\n## 5. 回收清单\n")
    b.append("- `RUN_SYN102_PASTE/` 下全部保存文件")
    b.append("- 每轮客户端回复的原始文本")
    b.append("- 每轮保存时的耗时与人工介入步骤数（手工保存是本形态的固有成本，须如实记录）\n")
    b.append("连同元数据填写 `评测设计_SYN102/04_外部投放结果记录表_SYN102.md`。\n")

    with open(os.path.join(TPL, "04_外部投放包_纯粘贴手动保存版.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(b))

    # ---------- 自校验：材料必须逐字内联 ----------
    paste_path = os.path.join(TPL, "04_外部投放包_纯粘贴手动保存版.md")
    paste = read(paste_path)
    for label, body in (("01_初始背景", r1), ("02_学业材料", r2), ("03_两国模拟规则", r3), ("04_预算与规则更新", r4)):
        if body not in paste:
            sys.exit("自校验失败: %s 未逐字内联到粘贴版投放包" % label)
    if agents not in paste:
        sys.exit("自校验失败: AGENTS.md 未逐字内联到粘贴版投放包")

    # ---------- MANIFEST ----------
    manifest = {}
    for base in (STAGE, DESIGN, TPL):
        for name in sorted(os.listdir(base)):
            p = os.path.join(base, name)
            if os.path.isfile(p) and name != "MANIFEST.json":
                manifest["%s/%s" % (os.path.basename(base), name)] = sha(p)
    with open(os.path.join(PKG, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("v0.3 投放包生成完成")
    print("  Run_Template/03_外部投放包_文件读写版.md")
    print("  Run_Template/04_外部投放包_纯粘贴手动保存版.md")
    print("  MANIFEST.json (%d 条哈希)" % len(manifest))
    print("  自校验通过: 5 份材料逐字内联")


if __name__ == "__main__":
    main()
