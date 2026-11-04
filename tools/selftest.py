#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selftest · 可复用留学规划工作流 · 工具与证据链一体化自测

一条命令跑完全部回归：

    python3 tools/selftest.py            # 证据链 + 基线 + 阴性用例
    python3 tools/selftest.py --replay   # 额外验证重放幂等（会重跑基线脚本）

覆盖：
    1. 证据链完整性 —— input_integrity / 阶段快照 manifest / v0.3 MANIFEST
    2. 基线判定     —— AutoRun02、AutoRun03 必须全绿；AutoRun01 必须命中已知历史缺陷
    3. 阴性用例     —— 7 类破坏必须被工具检出并报 ERROR
    4. 重放幂等     —— 脚本重跑后产物必须逐字节不变（仅 --replay）

退出码 0 = 全部通过；1 = 存在失败项。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import wf_core  # noqa: E402

V2 = os.path.join(REPO, "simulations", "规划流程模拟包_v0.2")
V3 = os.path.join(REPO, "simulations", "规划流程模拟包_v0.3")
V1 = os.path.join(REPO, "simulations", "规划流程模拟包_v0.1")

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = YELLOW = DIM = RESET = ""


class Tally:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def ok(self, label, detail=""):
        self.passed += 1
        print(f"  {GREEN}✓{RESET} {label}" + (f"  {DIM}{detail}{RESET}" if detail else ""))

    def bad(self, label, detail=""):
        self.failed += 1
        print(f"  {RED}✗{RESET} {label}" + (f"  {RED}{detail}{RESET}" if detail else ""))

    def info(self, text):
        print(f"  {DIM}·{RESET} {text}")


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------------------------------------------------------------- 1. 证据链

def check_evidence_chain(t):
    print("\n── 证据链完整性 " + "─" * 40)

    # input_integrity
    p = os.path.join(V2, "评测记录", "AutoRun03", "input_integrity.json")
    if not os.path.exists(p):
        t.bad("AutoRun03 input_integrity.json 缺失")
    else:
        data = json.load(open(p, encoding="utf-8"))
        ok = sum(1 for v in data.values() if v.get("matches_source"))
        if ok == len(data) and data:
            t.ok(f"input_integrity 全部匹配", f"{ok}/{len(data)}")
        else:
            t.bad("input_integrity 存在不匹配", f"{ok}/{len(data)}")

    # 阶段快照 manifest
    for tag, mf, sd in (
        ("PRE", "pre_snapshot_manifest.json", os.path.join(V2, "评测记录", "AutoRun03", "首次比较后")),
        ("FINAL", "final_snapshot_manifest.json", os.path.join(V2, "评测记录", "AutoRun03", "更新后")),
    ):
        mp = os.path.join(V2, "评测记录", "AutoRun03", mf)
        if not os.path.exists(mp):
            t.bad(f"{tag} manifest 缺失")
            continue
        man = json.load(open(mp, encoding="utf-8"))
        bad = []
        for name, rec in man.items():
            fp = os.path.join(sd, name)
            if not os.path.exists(fp):
                bad.append(f"{name} 缺失")
                continue
            exp = rec.get("sha256") if isinstance(rec, dict) else rec
            if sha(fp) != exp:
                bad.append(name)
        if bad:
            t.bad(f"{tag} 阶段快照哈希不符", ", ".join(bad[:4]))
        else:
            t.ok(f"{tag} 阶段快照哈希全部吻合", f"{len(man)} 文件")

    # v0.3 MANIFEST
    mp = os.path.join(V3, "MANIFEST.json")
    if not os.path.exists(mp):
        t.bad("v0.3 MANIFEST.json 缺失")
    else:
        man = json.load(open(mp, encoding="utf-8"))
        bad = [k for k, v in man.items()
               if not os.path.exists(os.path.join(V3, k)) or sha(os.path.join(V3, k)) != v]
        if bad:
            t.bad("v0.3 MANIFEST 存在不匹配", ", ".join(bad[:4]))
        else:
            t.ok("v0.3 MANIFEST 全部吻合", f"{len(man)} 文件")

    # AutoRun02 input_integrity
    p2 = os.path.join(V2, "评测记录", "AutoRun02", "input_integrity.json")
    if os.path.exists(p2):
        data = json.load(open(p2, encoding="utf-8"))
        ok = sum(1 for v in data.values() if v.get("matches_source"))
        (t.ok if ok == len(data) else t.bad)(
            f"AutoRun02 input_integrity", f"{ok}/{len(data)}")

    # 跨包一致性：v0.3 的投放材料必须与 v0.2 源逐字节一致
    a = os.path.join(V2, "分轮投放_SYN102")
    b = os.path.join(V3, "分轮投放_SYN102")
    if not (os.path.isdir(a) and os.path.isdir(b)):
        t.bad("跨包材料目录缺失")
    else:
        names = sorted(set(os.listdir(a)) & set(os.listdir(b)))
        diff = [n for n in names if sha(os.path.join(a, n)) != sha(os.path.join(b, n))]
        if diff:
            t.bad("v0.3 投放材料与 v0.2 源不一致", ", ".join(diff))
        else:
            t.ok("v0.3 投放材料与 v0.2 源逐字节一致", f"{len(names)} 份材料")

    # 评测设计一致性：v0.3 应是 v0.2 评测设计的超集
    a = os.path.join(V2, "评测设计_SYN102")
    b = os.path.join(V3, "评测设计_SYN102")
    if not (os.path.isdir(a) and os.path.isdir(b)):
        t.bad("跨包评测设计目录缺失")
    else:
        shared = sorted(set(os.listdir(a)) & set(os.listdir(b)))
        diff = [n for n in shared
                if n.endswith(".md") and sha(os.path.join(a, n)) != sha(os.path.join(b, n))]
        if diff:
            t.bad("v0.3 评测设计与 v0.2 不一致", ", ".join(diff))
        else:
            t.ok("v0.3 评测设计与 v0.2 一致", f"{len(shared)} 份共享文件")


# ---------------------------------------------------------------- 2. 基线判定

def check_baselines(t):
    print("\n── 基线判定 " + "─" * 44)

    for name, path in (("AutoRun02", os.path.join(V2, "AutoRun02")),
                       ("AutoRun03", os.path.join(V2, "AutoRun03"))):
        rep = wf_core.verify_run(path)
        if rep.ok and not rep.warns:
            t.ok(f"{name} 全绿", "0 ERROR / 0 WARN")
        else:
            t.bad(f"{name} 未达全绿",
                  f"{len(rep.errors)} ERROR / {len(rep.warns)} WARN: "
                  + "; ".join(f"{f.code} {f.title}" for f in (rep.errors + rep.warns)[:3]))

    # AutoRun01 必须命中已知历史缺陷（CHECKPOINT 体积超限）
    rep = wf_core.verify_run(os.path.join(V1, "AutoRun01"))
    codes = {f.code for f in rep.errors}
    if "E003" in codes:
        size = os.path.getsize(os.path.join(V1, "AutoRun01", "CHECKPOINT.md"))
        t.ok("AutoRun01 命中已知历史缺陷", f"E003 CHECKPOINT {size:,} B 超硬上限")
    else:
        t.bad("AutoRun01 未命中已知历史缺陷", f"errors={sorted(codes)}")


# ---------------------------------------------------------------- 3. 阴性用例

def _mut_oversize(d):
    with open(os.path.join(d, "CHECKPOINT.md"), "a", encoding="utf-8") as f:
        f.write("\n" + "历史噪声。" * 600)


def _mut_arith(d):
    for n in ("CASE.md", "CHECKPOINT.md"):
        p = os.path.join(d, n)
        t = open(p, encoding="utf-8").read().replace("70.8125", "72.5").replace("70.81", "72.5")
        open(p, "w", encoding="utf-8").write(t)


def _mut_nest(d):
    with open(os.path.join(d, "CHECKPOINT.md"), "a", encoding="utf-8") as f:
        f.write("\n\n## 历史快照\n" + open(os.path.join(d, "CHANGELOG.md"), encoding="utf-8").read())


def _mut_missing(d):
    os.remove(os.path.join(d, "EVIDENCE.md"))


def _mut_priv(d):
    with open(os.path.join(d, "CASE.md"), "a", encoding="utf-8") as f:
        f.write("\n学生现就读于清华大学，学号 202512345678。\n")


def _mut_drift(d):
    p = os.path.join(d, "CHECKPOINT.md")
    t = open(p, encoding="utf-8").read().replace("70.8125", "70.714")
    open(p, "w", encoding="utf-8").write(t)


def _mut_empty(d):
    open(os.path.join(d, "CHANGELOG.md"), "w", encoding="utf-8").close()


NEGATIVE_CASES = [
    ("CHECKPOINT 超体积", _mut_oversize, "E003"),
    ("误用算术均分", _mut_arith, "E004"),
    ("CHECKPOINT 嵌套旧全文", _mut_nest, "E006"),
    ("缺失 EVIDENCE.md", _mut_missing, "E001"),
    ("真实院校与学号泄漏", _mut_priv, "E009"),
    ("跨文件均分漂移", _mut_drift, "E004"),
    ("空文件", _mut_empty, "E002"),
]


def check_negatives(t):
    print("\n── 阴性用例 " + "─" * 44)
    src = os.path.join(V2, "AutoRun03")
    with tempfile.TemporaryDirectory(prefix="wf_selftest_") as tmp:
        for label, mutate, expect in NEGATIVE_CASES:
            d = os.path.join(tmp, label.replace(" ", "_"))
            shutil.copytree(src, d)
            mutate(d)
            rep = wf_core.verify_run(d)
            codes = {f.code for f in rep.errors}
            if expect in codes:
                t.ok(f"{label} 被检出", f"{expect}")
            else:
                t.bad(f"{label} 未检出", f"期望 {expect}，实得 {sorted(codes)}")
            shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------- 4. 重放幂等

def check_replay(t):
    print("\n── 重放幂等 " + "─" * 44)
    script = os.path.join(V2, "run_autorun03.py")
    run_dir = os.path.join(V2, "AutoRun03")
    before = {}
    for root, _, files in os.walk(run_dir):
        for f in files:
            p = os.path.join(root, f)
            before[p] = sha(p)
    rec = os.path.join(V2, "评测记录", "AutoRun03", "transcript.json")
    before[rec] = sha(rec)

    r = subprocess.run([sys.executable, script], capture_output=True, text=True, cwd=V2)
    if r.returncode != 0:
        t.bad("重放脚本执行失败", (r.stderr or "").strip().splitlines()[-1:] and
              (r.stderr or "").strip().splitlines()[-1] or "")
        return

    drifted = [p for p, h in before.items() if os.path.exists(p) and sha(p) != h]
    if drifted:
        t.bad("重放产物发生漂移", ", ".join(os.path.basename(p) for p in drifted[:4]))
    else:
        t.ok("重放产物逐字节不变", f"{len(before)} 个产物")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(prog="selftest", description="工作流工具与证据链自测")
    ap.add_argument("--replay", action="store_true", help="额外验证基线脚本重放幂等")
    args = ap.parse_args()

    print(f"{'selftest · 工作流工具与证据链自测'}")
    print(f"仓库：{REPO}")

    t = Tally()
    check_evidence_chain(t)
    check_baselines(t)
    check_negatives(t)
    if args.replay:
        check_replay(t)

    print()
    if t.failed:
        print(f"{RED}结论：未通过 — {t.failed} 项失败，{t.passed} 项通过{RESET}")
        sys.exit(1)
    print(f"{GREEN}结论：全部通过 — {t.passed} 项检查，0 项失败{RESET}")
    sys.exit(0)


if __name__ == "__main__":
    main()
