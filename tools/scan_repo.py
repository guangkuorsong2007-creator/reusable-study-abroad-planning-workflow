#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_repo · 可复用留学规划工作流 · 仓库级可分发性扫描

本产品库要公开分发给第三方顾问与开源评测，因此必须持续满足：

    1. 隐私红线 —— 任何文件都不得出现真实个人数据模式（手机号 / 身份证 / 学号 / 银行卡）
    2. 真实院校名 —— 只允许作为**反面示例**出现在治理文档中，
                    **绝不**允许出现在任何模拟包产物（simulations/）内
    3. 死链     —— 全部 markdown 相对链接必须可达
    4. 绝对路径 —— 仅允许出现在历史存档与决策/日志记录中（可追溯的引用），
                    任何**操作型文档**不得硬编码本机绝对路径

用法：
    python3 tools/scan_repo.py
退出码：0 通过 / 1 存在违规
"""

from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import wf_core  # noqa: E402

# 允许出现真实院校名的文件 —— 均为「反面示例」语境的红线声明
ALLOWED_REAL_INSTITUTION_FILES = {
    "AGENTS.md",                                   # 红线规约中的反面示例
    "docs/弱引导新案例验证方案_SYN-UG-102.md",      # 量表第 1 项的反面示例
}

# 工具自身文件 —— 其中的真实校名与学号是**检测器数据与阴性测试夹具**，按设计存在
ALLOWED_PATTERN_SOURCES = {
    "tools/wf_core.py",      # 真实院校黑名单本体
    "tools/selftest.py",     # 阴性用例夹具（含刻意构造的学号与校名）
}

# 允许出现绝对路径的文件前缀 —— 全部为历史存档或审计记录
ALLOWED_ABSOLUTE_PREFIXES = (
    "simulations/",            # 冻结基线与转录/复核报告中的历史执行路径
)
ALLOWED_ABSOLUTE_FILES = {
    "00_Status.md",            # 状态记录中的历史引用
    "03_Decisions.md",         # 决策记录中的历史引用
    "05_Session_Log.md",       # 会话流水中的历史引用
    "AGENTS.md",               # Canonical directory 标注
    "handoff/规划流程复用_可复制启动提示词.md",  # 本机副本标注
}

ABSOLUTE_PATH = re.compile(r"/Users/[A-Za-z0-9_.\-]+/")


def repo_files():
    out = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv")]
        for f in files:
            if f.endswith((".md", ".json", ".py", ".yml", ".yaml")):
                out.append(os.path.relpath(os.path.join(root, f), REPO))
    return sorted(out)


def main():
    errors, warns, notes = [], [], []

    print("scan_repo · 仓库级可分发性扫描")
    print(f"仓库：{REPO}\n")

    files = repo_files()

    # ---- 1 & 2. 隐私红线 + 真实院校名
    print("── 隐私红线与真实院校名 " + "─" * 36)
    priv_hits = 0
    inst_hits = 0
    for rel in files:
        p = os.path.join(REPO, rel)
        try:
            text = wf_core.read(p)
        except (OSError, UnicodeDecodeError):
            continue
        if rel in ALLOWED_PATTERN_SOURCES:
            continue
        for label, val in wf_core.scan_privacy(text, ()):
            if label == "疑似真实院校名":
                if rel in ALLOWED_REAL_INSTITUTION_FILES:
                    notes.append(f"{rel}: 真实校名「{val}」出现于反面示例语境（已豁免）")
                else:
                    errors.append(f"{rel}: 疑似真实院校名「{val}」")
                inst_hits += 1
            else:
                errors.append(f"{rel}: 疑似真实个人数据（{label}）{val!r}")
                priv_hits += 1
    if priv_hits:
        print(f"  ✗ 个人数据模式命中 {priv_hits} 处")
    else:
        print("  ✓ 未检出个人数据模式（手机号 / 身份证 / 学号 / 银行卡）")
    if inst_hits:
        exempt = sum(1 for n in notes if "已豁免" in n)
        print(f"  · 真实校名命中 {inst_hits} 处，其中 {exempt} 处为反面示例（已豁免）")
        for n in notes:
            print(f"      {n}")
    else:
        print("  ✓ 未检出真实院校名")

    # ---- 3. 死链
    print("\n── markdown 相对链接 " + "─" * 40)
    total, broken = 0, []
    for rel in files:
        if not rel.endswith(".md"):
            continue
        base = os.path.dirname(rel)
        text = wf_core.read(os.path.join(REPO, rel))
        for m in re.findall(r"\]\(([^)]+)\)", text):
            # 仅校验**相对**链接；file:// 与 http(s) 属绝对引用，由绝对路径检查项负责
            if m.startswith(("http://", "https://", "file://", "#", "mailto:")):
                continue
            total += 1
            target = os.path.normpath(os.path.join(REPO, base, m))
            if not os.path.exists(target):
                broken.append(f"{rel} → {m}")
    if broken:
        for b in broken[:12]:
            errors.append(f"死链：{b}")
        print(f"  ✗ {len(broken)}/{total} 条链接不可达")
    else:
        print(f"  ✓ {total} 条相对链接全部可达")

    # ---- 4. 绝对路径
    print("\n── 操作型文档硬编码绝对路径 " + "─" * 30)
    abs_hits = 0
    for rel in files:
        if rel.startswith(ALLOWED_ABSOLUTE_PREFIXES) or rel in ALLOWED_ABSOLUTE_FILES:
            continue
        try:
            text = wf_core.read(os.path.join(REPO, rel))
        except (OSError, UnicodeDecodeError):
            continue
        for m in ABSOLUTE_PATH.finditer(text):
            errors.append(f"{rel}: 硬编码绝对路径 {m.group(0)}…")
            abs_hits += 1
    if abs_hits:
        print(f"  ✗ {abs_hits} 处")
    else:
        print("  ✓ 操作型文档未硬编码本机绝对路径")

    # ---- 汇总
    print()
    if errors:
        print(f"结论：未通过 — {len(errors)} 项违规")
        for e in errors[:15]:
            print(f"  · {e}")
        if len(errors) > 15:
            print(f"  … 另有 {len(errors) - 15} 项")
        sys.exit(1)
    print(f"结论：通过 — 0 项违规（豁免记录 {len(notes)} 条）")
    sys.exit(0)


if __name__ == "__main__":
    main()
