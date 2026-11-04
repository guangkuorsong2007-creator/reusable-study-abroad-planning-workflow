#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wf_core · 可复用留学规划工作流 · 运行实例校验核心库

供 `wf-verify` 与 `wf-init` 共用。所有路径均相对于脚本所在位置解析，
仓库克隆到任意路径后均可直接运行。

设计原则：判定必须依据**落盘文件本体**，不采信任何自述结论。
"""

from __future__ import annotations

import difflib
import os
import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------- 常量

STATE_FILES = ["CASE.md", "EVIDENCE.md", "CHECKPOINT.md", "CHANGELOG.md"]

CHECKPOINT_LIMIT = 4000      # AGENTS.md 第 2 条：硬上限
CASE_SOFT_LIMIT = 10000      # AutoRun03 复核报告口径：软上限
NEST_WARN = 150              # CHECKPOINT 与他文件的最长公共子串告警阈值（字符）
NEST_ERROR = 400             # 超过此长度判定为嵌套历史全文
SELF_DUP = 150               # CHECKPOINT 内部自重复块阈值

# 非数值（等级制）成绩标记
NON_NUMERIC_MARKS = [
    "pass", "fail", "p/f", "n/p", "合格", "不合格", "通过", "免修", "缓考",
    "良好", "优秀", "中", "等级制", "无百分制", "不计入", "credit", "nc",
]

# 命中即视为「门槛/要求语境」的上下文，该处的百分数不作为学生实绩均分
REQUIREMENT_CTX = re.compile(
    r"(要求|门槛|至少|不得低于|不低于|需达|录取条件|入学要求|标准|≥|>=|\\ge|\\geq|\\leq|\\le)"
)

# 真实院校名黑名单（合成夹具不含这些校名；命中即疑似引入真实数据）
REAL_INSTITUTIONS = [
    "北京大学", "清华大学", "复旦大学", "上海交通大学", "浙江大学", "南京大学",
    "中山大学", "武汉大学", "四川大学", "中国人民大学", "北京航空航天大学",
    "同济大学", "哈尔滨工业大学", "华中科技大学", "中国科学技术大学",
    "西安交通大学", "北京师范大学", "南京师范大学", "东南大学", "南开大学",
    "天津大学", "天津师范大学", "北京科技大学", "电子科技大学", "西北工业大学",
    "大连理工大学", "吉林大学", "山东大学", "厦门大学", "重庆大学",
]

PRIVACY_PATTERNS = [
    ("手机号", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("身份证号", re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")),
    ("学号", re.compile(r"学\s*号\s*[:：]?\s*\d{6,}")),
    ("银行卡号", re.compile(r"(?<!\d)\d{16,19}(?!\d)")),
]


# ---------------------------------------------------------------- 数据结构

@dataclass
class Finding:
    level: str          # ERROR / WARN / INFO
    code: str
    title: str
    detail: str = ""
    hint: str = ""


@dataclass
class Report:
    target: str
    findings: list = field(default_factory=list)
    sections: list = field(default_factory=list)   # [(标题, [(符号, 文本), ...])]
    stats: dict = field(default_factory=dict)

    def add(self, level, code, title, detail="", hint=""):
        self.findings.append(Finding(level, code, title, detail, hint))

    def section(self, title, rows):
        self.sections.append((title, rows))

    @property
    def errors(self):
        return [f for f in self.findings if f.level == "ERROR"]

    @property
    def warns(self):
        return [f for f in self.findings if f.level == "WARN"]

    @property
    def ok(self):
        return not self.errors


# ---------------------------------------------------------------- 文本工具

def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def strip_latex(text):
    """去掉 LaTeX 装饰，避免 \\% / $ 等干扰数值提取。"""
    t = text.replace("\\%", "%").replace("\\approx", "约 ")
    t = t.replace("\\text", " ").replace("\\quad", " ")
    t = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", t)
    t = t.replace("$", "").replace("\\", "")
    return t


def strip_md(text):
    """去掉 markdown 强调与链接语法。"""
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    t = re.sub(r"\*([^*]+)\*", r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    return t


def normalize_md(text):
    return strip_md(strip_latex(text))


def _f(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def num(v):
    """数值友好显示：至少保留一位小数，去掉无意义尾零。"""
    if v is None:
        return "—"
    s = f"{v:.4f}".rstrip("0")
    if s.endswith("."):
        s += "0"
    return s


# ---------------------------------------------------------------- 学分表解析

@dataclass
class Course:
    name: str
    credits: float
    score_raw: str
    score: float | None      # None 表示非数值（等级制）

    @property
    def is_numeric(self):
        return self.score is not None


def parse_credit_tables(text):
    """从 markdown 表格中解析「课程 | 学分 | 总评」行。

    判定依据：第 2 列能解析为浮点 → 学分；第 3 列为数值 → 数值成绩；
    第 3 列含 Pass/合格 等标记 → 等级制非数值课程（不计入均分分母）。
    """
    courses = []
    seen = set()
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if all(set(c) <= set(":-* ") for c in cells if c):
            continue                                   # 分隔行
        name = normalize_md(cells[0]).strip()
        if not name or name in seen:
            continue
        credits = _f(normalize_md(cells[1]).replace("cr", "").strip())
        if credits is None:
            continue                                   # 表头或非学分列
        score_raw = normalize_md(cells[2]).strip()
        low = score_raw.lower()
        score = None
        if not any(m in low for m in NON_NUMERIC_MARKS):
            score = _f(score_raw)
        if score is None and not any(m in low for m in NON_NUMERIC_MARKS):
            continue                                   # 既非数值也非已知标记，跳过
        seen.add(name)
        courses.append(Course(name, credits, score_raw, score))
    return courses


@dataclass
class AverageResult:
    numeric: list
    non_numeric: list
    numerator: float
    denominator: float
    weighted: float | None
    arithmetic: float | None

    @property
    def excluded_credits(self):
        return sum(c.credits for c in self.non_numeric)


def compute_average(courses):
    num = [c for c in courses if c.is_numeric]
    non = [c for c in courses if not c.is_numeric]
    numerator = sum(c.credits * c.score for c in num)
    denominator = sum(c.credits for c in num)
    weighted = numerator / denominator if denominator else None
    arithmetic = (sum(c.score for c in num) / len(num)) if num else None
    return AverageResult(num, non, numerator, denominator, weighted, arithmetic)


def discover_material_files(run_dir, explicit=None):
    """在运行目录中定位含学分表的材料文件（优先命中数值课程最多者）。"""
    if explicit:
        return [os.path.join(run_dir, e) if not os.path.isabs(e) else e
                for e in explicit]
    cands = []
    for name in sorted(os.listdir(run_dir)):
        if not name.endswith(".md") or name in STATE_FILES:
            continue
        p = os.path.join(run_dir, name)
        if not os.path.isfile(p):
            continue
        try:
            crs = parse_credit_tables(read(p))
        except OSError:
            continue
        n_num = sum(1 for c in crs if c.is_numeric)
        if n_num:
            cands.append((n_num, p))
    cands.sort(key=lambda x: (-x[0], x[1]))
    return [p for _, p in cands[:1]]


# ---------------------------------------------------------------- 数值声明抽取

def extract_percentages(text):
    """返回 [(数值, 前后文窗口)]，已剥离 LaTeX。"""
    t = strip_latex(text)
    out = []
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*%", t):
        ctx = t[max(0, m.start() - 30):m.end() + 30]
        out.append((float(m.group(1)), ctx))
    return out


# 「均分」与数值之间允许出现的连接词（白名单，避免把任意文本当作均分声明）
AVG_CONNECT = (
    r"(?:仅|为|是|升至|拉升至|提高到|提升到|达到|到|达|约|≈|=|＝|:|：|、|，|的|和|与|\s)*"
)

# 命中即判定为「门槛 / 情景 / 目标」语境，不是当前实绩均分
NOT_ACTUAL_CTX = re.compile(
    r"(升至|拉升至|提高到|提升到|达到|至少|不低于|预期|预计|情景|假设|上限|目标|"
    r"要求|门槛|需达|录取条件|入学要求|标准|≥|>=|\\ge|\\geq|\\leq|\\le)"
)

# 教务系统 / 截图类指标，与摘录加权均分口径不同，不可混用（对应量表第 5 项）
SYSTEM_METRIC_CTX = re.compile(r"(系统|截图|教务系统|累计本校|累计GPA|本校GPA)")

# 数值后若紧跟数字/字母/汉字/空白，则不视为一个完整的均分声明
NUM_TAIL = r"(?![0-9A-Za-z\u4e00-\u9fff\s])"

# 「均分」前不能是「平」——否则「平均分」（某学期平均分）会被误当作加权均分
# 「学分加权平均」是等价表述，一并纳入
AVG_TOKEN = r"(?:(?<!平)均分|加权平均(?:分)?)"

# 句末的取值表述：`约70.71分`、`= 70.71 分`（常见于算式结论）
ROUNDED_AVG = re.compile(r"(?:约|＝|=)\s*(\d+(?:\.\d+)?)\s*分")


def extract_avg_claims(text):
    """抽取作为「当前实绩均分」出现的数值。

    均分在本工作流中有三种表述：`70.8125%`、`70.71 分`、以及 v0.1 期的裸数字
    `均分仅 70.71`；三者同义，均予接受。
    以下语境一律排除：
      - 门槛语境（≥ / 要求 / 至少 / 达到）
      - 情景语境（升至 / 目标 / 情景）
      - 教务系统与截图类指标（口径不同，不可与摘录加权混用）
      - 公式中的分子分母（`加权均分 1133.0 / 16.0 = 70.8125%` 的 1133.0）
    返回归一化（2 位小数）后的数值集合。
    """
    t = normalize_md(text)
    vals = set()
    pats = [
        re.compile(AVG_TOKEN + AVG_CONNECT + r"(\d+(?:\.\d+)?)\s*(?:[%分])?" + NUM_TAIL),
        re.compile(r"(\d+(?:\.\d+)?)\s*[%分]" + r"[^。；;，,]{0,10}?" + AVG_TOKEN),
    ]
    for p in pats:
        for m in p.finditer(t):
            if NOT_ACTUAL_CTX.search(m.group(0)):
                continue
            # 公式分子：`均分 1133.0 / 16.0 = ...` 中的 1133.0 不是均分
            tail = t[m.end(): m.end() + 12]
            if re.match(r"\s*/\s*\d", tail):
                continue
            # 教务系统 / 截图类指标
            head = t[max(0, m.start() - 16): m.start()]
            if SYSTEM_METRIC_CTX.search(head):
                continue
            v = _f(m.group(1))
            if v is not None:
                vals.add(round(v, 2))

    # 句式回退：`学分加权平均 = (...) = 990/14 = 70.714285…，约70.71分`
    # 数值以「约N分 / = N分」形式落在同一句的末尾，取该表述作为声明值
    for sent in re.split(r"[。；;\n]", t):
        if not re.search(AVG_TOKEN, sent):
            continue
        if SYSTEM_METRIC_CTX.search(sent):
            continue
        for rm in ROUNDED_AVG.finditer(sent):
            v = _f(rm.group(1))
            if v is not None:
                vals.add(round(v, 2))
    return vals


def extract_scenario_claims(text, tag):
    """抽取 R1 / R2 情景声明值。

    采用**分块法**：从标签出现处取到下列任一边界为止——
    下一个情景标签（R1/R2）、下一个 markdown 标题（避免串到下一章节）、或 400 字符上限。
    以此兼容 LaTeX 分行书写（分子/分母/结果分列多行），同时防止跨章节串值。
    """
    t = normalize_md(text)
    positions = [(m.start(), m.group(0))
                 for m in re.finditer(r"\b(R1|R2)\b", t)]
    headings = [m.start() for m in re.finditer(r"^#{1,6}\s", t, re.M)]
    vals = set()
    for pos, label in positions:
        if label != tag:
            continue
        bounds = [p for p, l in positions if p > pos]
        bounds += [h for h in headings if h > pos]
        end = min(bounds) if bounds else len(t)
        window = t[pos: min(end, pos + 400)]
        for pm in re.finditer(r"(\d+(?:\.\d+)?)\s*[%分]", window):
            v = _f(pm.group(1))
            if v is not None:
                vals.add(round(v, 2))
    return vals


def longest_common_substring(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    block = sm.find_longest_match(0, len(a), 0, len(b))
    return a[block.a: block.a + block.size]


def find_self_repeats(text, threshold):
    """检测文件内部的长块自重复（历史全文嵌套的典型特征）。"""
    hits = []
    paras = [p.strip() for p in text.split("\n\n") if len(p.strip()) >= threshold]
    for i in range(len(paras)):
        for j in range(i + 1, len(paras)):
            common = longest_common_substring(paras[i], paras[j])
            if len(common) >= threshold:
                hits.append((len(common), common[:60]))
    return hits


def scan_privacy(text, extra_denylist=()):
    """扫描疑似真实个人数据。返回 [(类别, 命中串)]。"""
    hits = []
    for label, pat in PRIVACY_PATTERNS:
        for m in pat.finditer(text):
            hits.append((label, m.group(0)))
    for term in list(REAL_INSTITUTIONS) + list(extra_denylist):
        if term and term in text:
            hits.append(("疑似真实院校名", term))
    return hits


# ---------------------------------------------------------------- 表格与章节解析

def parse_markdown_tables(text):
    """返回 [(表头单元格列表, [数据行单元格列表, ...])]，逐表解析。"""
    tables = []
    header, rows = None, []

    def flush():
        if header and rows:
            tables.append((header, rows))

    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            flush()
            header, rows = None, []
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c) <= set(":-* ") for c in cells if c):
            continue                                   # 分隔行
        if header is None:
            header = cells
        else:
            rows.append(cells)
    flush()
    return tables


def parse_sections(text):
    """返回 [(标题, 正文)]，按 markdown 标题切分。"""
    sections, cur, body = [], "(前言)", []
    for line in text.splitlines():
        if re.match(r"^#{1,6}\s+\S", line):
            sections.append((cur, "\n".join(body)))
            cur, body = line.strip("# ").strip(), []
        else:
            body.append(line)
    sections.append((cur, "\n".join(body)))
    return sections


PLACEHOLDER_VALUES = {"", "-", "—", "无", "N/A", "n/a", "TBD", "待补充", "待定", "略"}


def is_placeholder(cell):
    return normalize_md(cell).strip().strip("*`").strip() in PLACEHOLDER_VALUES


# ---------------------------------------------------------------- 语义检查

# CASE.md 必备章节概念（任一关键词命中即视为该章节存在）
REQUIRED_CASE_CONCEPTS = [
    ("事实基线", ("事实", "基线", "背景", "个人基线")),
    ("学业测算或情景", ("测算", "情景", "学业", "成绩", "加权")),
    ("方案对比", ("方案", "对比", "路线", "比选", "全链条", "重估")),
    ("结论与下一步", ("结论", "下一步", "阶段结论", "破局", "调整方向",
                      "待核实", "行动", "后续动作")),
]

# 声明「等级制课程不计入分母」的表述
# 注意否定式前置写法：`严禁计入加权分母` / `不得计入` —— 不能只匹配「不计」二字
EXCLUSION_CTX = re.compile(
    r"(?:严禁|不得|不能|不应|不可|不予|非)[^。；;\n]{0,6}计入"
    r"|不计|不纳入|排除|隔离|不含|不作为分母|不计入"
)


def check_evidence_table(evid_text):
    """检查 EVIDENCE 表格结构与局限列完整性。

    返回 (rows, problems)；problems 中每项为 (级别, 说明)。
    """
    problems = []
    rows = []
    tables = parse_markdown_tables(evid_text)
    target = None
    for header, body in tables:
        h = " ".join(normalize_md(c) for c in header)
        if "局限" in h or "限制" in h:
            target = (header, body)
            break
    if target is None:
        problems.append(("WARN", "未找到含「局限」列的证据表格"))
        return rows, problems
    header, body = target
    if len(header) < 4:
        problems.append(("ERROR", f"证据表头仅 {len(header)} 列，缺少「主张」与「局限」列"))
    for cells in body:
        rows.append(cells)
        if len(cells) < 4:
            problems.append(("ERROR", f"证据行「{normalize_md(cells[0])[:24]}」仅 {len(cells)} 列"))
            continue
        if is_placeholder(cells[-1]):
            problems.append(("WARN", f"证据「{normalize_md(cells[0])[:24]}」的局限列为空或为占位符"))
    return rows, problems


def check_case_sections(case_text):
    """检查 CASE.md 必备章节是否齐备。返回缺失的概念列表。"""
    sections = parse_sections(case_text)
    headings = " ".join(h for h, _ in sections)
    bodies = "\n".join(b for _, b in sections)
    haystack = headings + "\n" + bodies
    missing = []
    for concept, keys in REQUIRED_CASE_CONCEPTS:
        if not any(k in haystack for k in keys):
            missing.append(concept)
    return missing


def check_changelog_entries(chg_text):
    """检查 CHANGELOG 每条日期条目是否有实质内容。返回空洞条目列表。"""
    entries = re.findall(r"^#{2,3}\s*\[?\d{4}-\d{2}-\d{2}.*$", chg_text, re.M)
    if not entries:
        return []
    hollow = []
    for title, body in parse_sections(chg_text):
        if not re.match(r"\d{4}-\d{2}-\d{2}", title):
            continue
        bullets = [l for l in body.splitlines()
                   if l.strip().startswith(("-", "*", "·")) and len(l.strip()) > 8]
        if not bullets:
            hollow.append(title[:40])
    return hollow


def extract_amounts(text):
    """抽取「N 万元 / N万」金额，保留整数值。"""
    t = normalize_md(text)
    vals = set()
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*万", t):
        v = _f(m.group(1))
        if v is not None:
            vals.add(round(v, 2))
    return vals


# ---------------------------------------------------------------- 校验主流程

def verify_run(run_dir, materials=None, denylist=(), case_soft_limit=CASE_SOFT_LIMIT):
    rep = Report(target=os.path.abspath(run_dir))

    if not os.path.isdir(run_dir):
        rep.add("ERROR", "E000", "运行目录不存在", run_dir)
        return rep

    # ---- 1. 四文件结构
    struct_rows = []
    texts = {}
    for fn in STATE_FILES:
        p = os.path.join(run_dir, fn)
        if not os.path.exists(p):
            struct_rows.append(("✗", f"{fn:<14} 缺失"))
            rep.add("ERROR", "E001", f"{fn} 缺失", "运行实例必须维护四份状态文件")
            continue
        size = os.path.getsize(p)
        if size == 0:
            struct_rows.append(("✗", f"{fn:<14} 空文件"))
            rep.add("ERROR", "E002", f"{fn} 为空文件", "状态文件不得为空占位")
            continue
        texts[fn] = read(p)
        limit = f"  (上限 {CHECKPOINT_LIMIT:,} B)" if fn == "CHECKPOINT.md" else (
            f"  (软上限 {case_soft_limit:,} B)" if fn == "CASE.md" else "")
        struct_rows.append(("✓", f"{fn:<14} {size:,} B{limit}"))
        if fn == "CHECKPOINT.md" and size > CHECKPOINT_LIMIT:
            rep.add("ERROR", "E003", "CHECKPOINT.md 超出体积硬上限",
                    f"实测 {size:,} B > 上限 {CHECKPOINT_LIMIT:,} B",
                    "精简为单点状态，历史演进沉淀至 CHANGELOG.md")
        if fn == "CASE.md" and size > case_soft_limit:
            rep.add("WARN", "W001", "CASE.md 超出软上限",
                    f"实测 {size:,} B > 软上限 {case_soft_limit:,} B",
                    "拆分次要内容至 EVIDENCE.md 或 CHANGELOG.md")
    rep.section("文件结构", struct_rows)

    if "CASE.md" not in texts:
        return rep

    case_t = texts["CASE.md"]
    ckpt_t = texts.get("CHECKPOINT.md", "")
    evid_t = texts.get("EVIDENCE.md", "")
    chg_t = texts.get("CHANGELOG.md", "")

    # ---- 2. 加权均分复算
    avg_rows = []
    mat_files = discover_material_files(run_dir, materials)
    avg = None
    if not mat_files:
        avg_rows.append(("·", "未找到含学分表的材料文件，跳过复算"))
        rep.add("WARN", "W002", "未找到可用于均分复算的学业材料",
                "未在运行目录中发现含「学分 | 总评」表格的 .md",
                "可用 --materials 指定，或确认材料是否已投放")
    else:
        src = mat_files[0]
        courses = parse_credit_tables(read(src))
        avg = compute_average(courses)
        avg_rows.append(("·", f"源材料：{os.path.basename(src)}"))
        for c in avg.numeric:
            avg_rows.append(("·", f"    {c.name}  {c.credits}cr × {c.score:g}"))
        for c in avg.non_numeric:
            avg_rows.append(("·", f"    {c.name}  {c.credits}cr  {c.score_raw}  → 非数值，已排除"))
        avg_rows.append(("·", f"分子 {num(avg.numerator)}   分母 {num(avg.denominator)}"
                              f"（排除非数值 {num(avg.excluded_credits)} cr）"))
        avg_rows.append(("·", f"加权均分 = {num(avg.numerator)} / {num(avg.denominator)} = {num(avg.weighted)}%"))
        if avg.arithmetic is not None:
            avg_rows.append(("ℹ", f"算术均分 = {num(avg.arithmetic)}%（若文中出现该值，说明用了未加权平均）"))

        # 复算值必须在 CASE 与 CHECKPOINT 中命中
        target = round(avg.weighted, 2)
        for fn, body in (("CASE.md", case_t), ("CHECKPOINT.md", ckpt_t)):
            if not body:
                continue
            claims = extract_avg_claims(body)
            hit = any(abs(c - target) <= 0.01 for c in claims)
            if hit:
                shown = sorted(c for c in claims if abs(c - target) <= 0.01)
                avg_rows.append(("✓", f"{fn} 均分声明命中复算值 {shown[0]:g}%"))
            elif not claims:
                # 尚未声明（脚手架初始态）—— 不是数值冲突，降级为待填
                avg_rows.append(("·", f"{fn} 尚未声明均分（待填）"))
                rep.add("WARN", "W006", f"{fn} 尚未声明加权均分",
                        "运行实例未声明任何均分值，无法与复算值交叉核对",
                        "CASE.md 为事实源、CHECKPOINT.md 为锚点，均应载明加权均分")
            else:
                avg_rows.append(("✗", f"{fn} 未命中复算值 {target:g}%"))
                rep.add("ERROR", "E004", f"{fn} 声明均分与复算值不符",
                        f"复算 {target:g}%；文中均分声明 {sorted(claims)}",
                        "核对学分加权口径、是否误用算术均分、是否遗漏非数值课程分母")
        rep.stats["recomputed_average"] = round(avg.weighted, 4) if avg.weighted else None
    rep.section("加权均分复算", avg_rows)

    # ---- 3. 跨文件数值一致性
    cons_rows = []
    metrics = [("加权均分", extract_avg_claims)]
    for tag, label in (("R1", "重修情景 R1"), ("R2", "重修情景 R2")):
        metrics.append((label, lambda t, tg=tag: extract_scenario_claims(t, tg)))
    for label, fn in metrics:
        cvals = fn(case_t)
        kvals = fn(ckpt_t) if ckpt_t else set()
        if not cvals and not kvals:
            cons_rows.append(("·", f"{label}: 未声明，跳过"))
            continue
        if not kvals:
            cons_rows.append(("·", f"{label}: 仅 CASE 声明 {sorted(cvals)}"))
            continue
        inter = cvals & kvals
        if inter:
            cons_rows.append(("✓", f"{label}: CASE / CHECKPOINT 一致 ({sorted(inter)[0]:g}%)"))
        else:
            cons_rows.append(("✗", f"{label}: CASE {sorted(cvals)} vs CHECKPOINT {sorted(kvals)}"))
            rep.add("ERROR", "E005", f"{label} 跨文件数值漂移",
                    f"CASE={sorted(cvals)}；CHECKPOINT={sorted(kvals)}",
                    "同一事实以 CASE.md 为当前值，CHECKPOINT.md 只做引用")
    rep.section("跨文件数值一致性", cons_rows)

    # ---- 4. 嵌套与自重复
    nest_rows = []
    if ckpt_t:
        for other in ("CASE.md", "EVIDENCE.md", "CHANGELOG.md"):
            if other not in texts:
                continue
            common = longest_common_substring(ckpt_t, texts[other])
            if len(common) >= NEST_ERROR:
                nest_rows.append(("✗", f"CHECKPOINT 含 {other} 的大段正文（{len(common)} 字符）"))
                rep.add("ERROR", "E006", f"CHECKPOINT.md 疑似嵌套 {other} 全文",
                        f"最长公共子串 {len(common)} 字符",
                        "CHECKPOINT 仅保留当前单点状态与文件指针")
            elif len(common) >= NEST_WARN:
                nest_rows.append(("!", f"CHECKPOINT 与 {other} 有 {len(common)} 字符重合，建议复核"))
                rep.add("WARN", "W003", f"CHECKPOINT.md 与 {other} 存在较大文本重合",
                        f"最长公共子串 {len(common)} 字符")
        dups = find_self_repeats(ckpt_t, SELF_DUP)
        if dups:
            nest_rows.append(("✗", f"CHECKPOINT 内部存在 {len(dups)} 处长块重复"))
            rep.add("ERROR", "E007", "CHECKPOINT.md 内部存在长块自重复",
                    "; ".join(f"{n} 字符：{c!r}" for n, c in dups[:3]),
                    "典型成因是把旧 CHECKPOINT 全文嵌套进新 CHECKPOINT")
        if not nest_rows:
            nest_rows.append(("✓", "未检出历史全文嵌套"))
    rep.section("嵌套与自重复检测", nest_rows)

    # ---- 5. 结构要素
    struct2_rows = []
    if ckpt_t:
        missing = [f for f in ("CASE.md", "EVIDENCE.md", "CHANGELOG.md")
                   if f not in ckpt_t]
        if missing:
            struct2_rows.append(("✗", f"CHECKPOINT 未指向：{', '.join(missing)}"))
            rep.add("ERROR", "E008", "CHECKPOINT.md 缺少文件指针",
                    f"缺少 {', '.join(missing)}",
                    "新会话仅凭 CHECKPOINT 即可接续，必须给出其余文件指针")
        else:
            struct2_rows.append(("✓", "CHECKPOINT 指向 CASE / EVIDENCE / CHANGELOG"))
    if evid_t:
        ids = re.findall(r"\|\s*\*{0,2}([A-Z]{1,4}(?:-[A-Z])?\d+)\*{0,2}\s*\|", evid_t)
        if ids:
            struct2_rows.append(("✓", f"EVIDENCE 含 {len(ids)} 条来源编号：{', '.join(ids[:6])}"))
        else:
            struct2_rows.append(("✗", "EVIDENCE 未检出来源编号行"))
            rep.add("WARN", "W004", "EVIDENCE.md 未检出来源编号",
                    "未匹配到形如 `| **SYN-L10** |` 或 `| **S01** |` 的证据行")
        # E010 证据表结构与局限列完整性
        _, ev_problems = check_evidence_table(evid_t)
        for level, msg in ev_problems:
            struct2_rows.append(("✗" if level == "ERROR" else "!", msg))
            rep.add(level, "E010", "EVIDENCE 证据表结构或局限列不完整", msg,
                    "每条证据都须写明支持范围与局限性，这是量表第 15 项「全流程透明度」的载体")
    if chg_t:
        entries = re.findall(r"^#{2,3}\s*\[?\d{4}-\d{2}-\d{2}", chg_t, re.M)
        if entries:
            struct2_rows.append(("✓", f"CHANGELOG 含 {len(entries)} 条日期化变更记录"))
            hollow = check_changelog_entries(chg_t)
            if hollow:
                struct2_rows.append(("!", f"{len(hollow)} 条 CHANGELOG 条目无实质内容"))
                rep.add("WARN", "W007", "CHANGELOG.md 存在空洞条目",
                        "; ".join(hollow[:3]),
                        "每条变更记录须写明改了什么、依据哪条来源、为什么")
        else:
            struct2_rows.append(("✗", "CHANGELOG 未检出日期化条目"))
            rep.add("WARN", "W005", "CHANGELOG.md 缺少日期化条目",
                    "未匹配到 `## YYYY-MM-DD...` 形式的变更标题")
    rep.section("结构要素", struct2_rows)

    # ---- 5b. CASE 章节完备性
    case_rows = []
    missing_secs = check_case_sections(case_t)
    if missing_secs:
        case_rows.append(("!", f"CASE 缺少章节：{', '.join(missing_secs)}"))
        rep.add("WARN", "W008", "CASE.md 必备章节不完备",
                f"缺少 {', '.join(missing_secs)}",
                "CASE 应覆盖：事实基线、学业测算与情景、方案对比、结论与下一步")
    else:
        case_rows.append(("✓", "CASE 必备章节齐备（事实基线 / 学业测算 / 方案对比 / 结论下一步）"))
    rep.section("CASE 章节完备性", case_rows)

    # ---- 5c. 非数值课程排除声明（量表第 2 项）
    excl_rows = []
    if avg is not None and avg.non_numeric:
        names = [c.name for c in avg.non_numeric]
        excl_rows.append(("·", f"材料含 {len(names)} 门非数值课程：{', '.join(names)}"))
        if EXCLUSION_CTX.search(case_t):
            excl_rows.append(("✓", "CASE 已声明排除/不计入分母的处置"))
        else:
            excl_rows.append(("!", "CASE 未见「不计入分母 / 隔离」类排除声明"))
            rep.add("WARN", "W009", "CASE.md 未声明非数值课程的排除处置",
                    f"材料含非数值课程 {', '.join(names)}，但 CASE 中未见排除说明",
                    "量表第 2 项要求明确说明等级制课程不污染数值分母")
    elif avg is not None:
        excl_rows.append(("·", "材料无等级制非数值课程，跳过"))
    rep.section("非数值课程排除声明", excl_rows)

    # ---- 5d. 跨文件金额一致性
    amt_rows = []
    case_amt = extract_amounts(case_t)
    ckpt_amt = extract_amounts(ckpt_t) if ckpt_t else set()
    if case_amt and ckpt_amt:
        inter = case_amt & ckpt_amt
        if inter:
            amt_rows.append(("✓", f"金额口径一致，共享锚点：{sorted(inter)[:6]}"))
        else:
            only_c = sorted(case_amt - ckpt_amt)
            only_k = sorted(ckpt_amt - case_amt)
            amt_rows.append(("!", f"金额锚点无交集 CASE={only_c[:6]} / CHECKPOINT={only_k[:6]}"))
            rep.add("WARN", "W010", "CASE 与 CHECKPOINT 的金额锚点无交集",
                    f"CASE={only_c[:8]}；CHECKPOINT={only_k[:8]}",
                    "预算与成本类金额应在两份文件中同源，注意历史值与当前值是否已正确沉淀")
    else:
        amt_rows.append(("·", "金额信息不足，跳过"))
    rep.section("跨文件金额一致性", amt_rows)

    # ---- 6. 隐私红线
    priv_rows = []
    all_text = "\n".join(texts.values())
    for name in sorted(os.listdir(run_dir)):
        if name.endswith(".md") and name not in texts:
            p = os.path.join(run_dir, name)
            if os.path.isfile(p):
                try:
                    all_text += "\n" + read(p)
                except OSError:
                    pass
    hits = scan_privacy(all_text, denylist)
    if hits:
        seen = set()
        for label, val in hits:
            key = (label, val)
            if key in seen:
                continue
            seen.add(key)
            priv_rows.append(("✗", f"{label}: {val}"))
            rep.add("ERROR", "E009", f"疑似真实个人数据（{label}）", val,
                    "本产品库仅允许合成夹具；真实数据须完全脱敏后方可进入")
    else:
        priv_rows.append(("✓", "未检出真实个人数据模式与真实院校名"))
    rep.section("隐私红线扫描", priv_rows)

    rep.stats["errors"] = len(rep.errors)
    rep.stats["warns"] = len(rep.warns)
    return rep
