#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoRun03 执行脚本：弱引导新合成案例 (SYN-UG-102) 自动化模拟与快照固化

路径解析：默认以脚本自身所在目录为包根，保证仓库被克隆/移动后仍可运行；
如需指向其他副本，可用环境变量 WF_AUTORUN03_BASE 覆盖。
"""

import os
import json
import hashlib
import shutil
from datetime import datetime

BASE_DIR = os.path.abspath(
    os.environ.get("WF_AUTORUN03_BASE", os.path.dirname(os.path.abspath(__file__)))
)
RUN_DIR = os.path.join(BASE_DIR, "AutoRun03")
RECORD_DIR = os.path.join(BASE_DIR, "评测记录", "AutoRun03")
STAGE_DIR = os.path.join(BASE_DIR, "分轮投放_SYN102")
EVAL_DIR = os.path.join(BASE_DIR, "评测设计_SYN102")

os.makedirs(RUN_DIR, exist_ok=True)
os.makedirs(RECORD_DIR, exist_ok=True)
PRE_SNAP_DIR = os.path.join(RECORD_DIR, "首次比较后")
FINAL_SNAP_DIR = os.path.join(RECORD_DIR, "更新后")
os.makedirs(PRE_SNAP_DIR, exist_ok=True)
os.makedirs(FINAL_SNAP_DIR, exist_ok=True)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def make_manifest(folder):
    manifest = {}
    for fname in sorted(os.listdir(folder)):
        fpath = os.path.join(folder, fname)
        if os.path.isfile(fpath) and not fname.startswith("."):
            manifest[fname] = sha256_file(fpath)
    return manifest

# -------------------------------------------------------------
# 阶段 1: 初始化与初步访谈 (Rounds 1-4)
# -------------------------------------------------------------
shutil.copy(os.path.join(BASE_DIR, "Run_Template", "AGENTS.md"), os.path.join(RUN_DIR, "AGENTS.md"))
shutil.copy(os.path.join(STAGE_DIR, "01_初始背景_SYN102.md"), os.path.join(RUN_DIR, "01_虚构学生初始资料.md"))

# -------------------------------------------------------------
# 阶段 2: 投放学业材料 (Rounds 5-6)
# -------------------------------------------------------------
shutil.copy(os.path.join(STAGE_DIR, "02_学业材料_SYN102.md"), os.path.join(RUN_DIR, "02_学业材料.md"))

# -------------------------------------------------------------
# 阶段 3: 投放两国模拟规则并完成首次比较与四文件落盘 (Rounds 7-8)
# -------------------------------------------------------------
shutil.copy(os.path.join(STAGE_DIR, "03_两国模拟规则_SYN102.md"), os.path.join(RUN_DIR, "03_两国模拟规则.md"))

# 写入首次比较后的 CASE.md, EVIDENCE.md, CHECKPOINT.md, CHANGELOG.md
case_md_pre = """# SYN-UG-102 个案全景记录 (CASE)

- 档案编号：SYN-UG-102
- 记录时间：2026-10-28T13:15:00Z
- 规划阶段：首轮双轨比较完成，等待进一步决策与材料更新

---

## 一、 当前核心决策与方向

1. **总目标**：本科毕业后出国攻读硕士，谋求当地对口技术就业并争取长期居留身份；
2. **专业与学科**：海岚大学信息管理与信息系统（工科/商科交叉），拟申请数据科学、商业分析或应用信息技术相关硕士；
3. **目的地选择状态**：未预设特定国家，目前在兰泽国 C 项目与沧澜国 D 项目之间进行双轨机制对比与优劣权衡；
4. **决策优先级**：以就业可行性与长期居留闭环为核心考量，大学综合排名仅供参考，无 QS 前 100 硬门槛。

---

## 二、 个人基线事实与证据

| 维度 | 核定事实 | 证据来源与性质 | 备注与限制 |
| :--- | :--- | :--- | :--- |
| **就读院校** | 海岚大学（四年制普通本科，2025年入学，预计2029年毕业） | SYN-L10（初始资料） | 虚构院校与案例 |
| **学业实绩** | 4 门数值课程（16.0学分）：加权分子 1133.0，加权均分 **70.8125%**（~70.81%） | SYN-L11（学业摘录） | 高数 56分（5.5cr, 挂科在档）；线代 78(3.5cr)；Python 84(4cr)；统计 72(3cr) |
| **非数值课程** | 专业英语与科技交流（1.5学分）：**合格 (Pass)** | SYN-L11 | 等级制无百分制，**严禁计入加权分母**（分母保持 16.0） |
| **系统指标** | 某学期均分 77.20；累计 GPA 2.65/4.0 | SYN-L12（教务截图） | 口径不明，不能替代四门加权均分，亦不可直接换算国外 GPA |
| **重修规划** | 计划 2027 春重修高数，目标 82 分 | 学生意向陈述 | 规划目标非实绩；保留原始 56 分在档 |
| **外语能力** | 无任何国际语言考试实绩 | 学生确认 | 语言标准 A/B/C/D 达标性未知 |
| **实践与科研** | 仅有校内信管系统课程作业，无正式校外实习或科研课题 | 学生确认 | 独立工程开发能力未验证 |
| **预算情况** | **家庭已明确确认资金：人民币 55 万元**；争取上限 75 万元（未落实） | SYN-L10 | 规划先以 55 万元为硬基准 |

---

## 三、 学业测算模型与情景分析

### 1. 原始四门数值课程加权
- 计算式：$(5.5 \\times 56 + 3.5 \\times 78 + 4.0 \\times 84 + 3.0 \\times 72) / (5.5 + 3.5 + 4.0 + 3.0)$
- 数值：$1133.0 / 16.0 = 70.8125\%$；
- 原始不及格记录：高数 56 分在档，属于客观实绩。

### 2. 高数重修目标（82分）情景推演（规划假设）
- **情景 R1（仅替换原分）**：
  $$\\text{新分子} = 1133.0 - 5.5 \\times 56 + 5.5 \\times 82 = 1276.0$$
  $$\\text{均分} = 1276.0 / 16.0 = 79.75\\%$$
- **情景 R2（两次均计入）**：
  $$\\text{新分子} = 1133.0 + 5.5 \\times 82 = 1584.0$$
  $$\\text{新分母} = 16.0 + 5.5 = 21.5$$
  $$\\text{均分} = 1584.0 / 21.5 \\approx 73.6744\\% \\quad (\\approx 73.67\\%)$$

---

## 四、 两国模拟路线对比分析

| 评估维度 | 兰泽国 C（数据应用硕士 C） | 沧澜国 D（应用信息硕士 D） | 取舍与判定 |
| :--- | :--- | :--- | :--- |
| **学制与学位** | 2 年制硕士 | 1 年制硕士 | C 学制更长，D 时间成本更低 |
| **学术达标性** | 要求全本科均分 $\\ge 75\\%$；目前 16 学分摘录为 70.81%，全本科未知，**待定** | 要求四门摘录加权 $\\ge 70.0\\%$ 且线代 $\\ge 75$。目前 70.81% 且线代 78，**表面数值达标** | D 初审学术门槛达成；C 需看后续学期与重修拉升 |
| **工签与居留衔接** | 工签 24 个月；居留要求 12 个月技能工龄 $\\rightarrow$ **安全覆盖 (+12月缓冲)** | 工签 12 个月；居留要求 24 个月技能工龄 $\\rightarrow$ **制度性断裂 (缺12月工签)** | **核心断裂点**：D 方案无工签续签通道，无法达成居留 |
| **全案总开销** | 54 万元 (学费26+生活16+杂项3+求职5+备用4) | 36 万元 (学费14+生活10+杂项3+求职5+备用4) | D 费用低廉；C 处于确认预算边缘 |
| **预算闭合情况** | 54 万 $\\le 55$ 万确认资金（**结余 1 万元**） | 36 万 $\\le 55$ 万确认资金（**结余 19 万元**） | 均在 55 万预算内，但 C 仅余 1 万安全边际极薄 |

---

## 五、 阶段结论与下一步

1. **方案 C**：身份链条通畅（工签24月覆益居留12月），但预算仅余1万安全垫薄弱，且本科总均分能否达75%有待大二大三检验；
2. **方案 D**：成本低（36万）且初期学术达标，但存在**12个月工签无法满足24个月居留工龄**的致命法律断裂；
3. **下一步动作**：保持双轨观察，不预先替用户锁定国家；重点核实 C 的学业拉升路径及 D 是否存在工签衔接扩展政策。
"""

evidence_md_pre = """# SYN-UG-102 证据与来源索引 (EVIDENCE)

- 更新时间：2026-10-28T13:15:00Z
- 证据范围：封闭资料试验材料

| 证据编号 | 证据名称 | 核心主张与提炼 | 适用范围与局限性 |
| :--- | :--- | :--- | :--- |
| **SYN-L10** | 初始背景材料 | 信管大一在读，2029毕业；意向留学+工作+居留；预算确认55万/争取75万；语言未考 | 虚构学生，不代表现实世界；仅供本次基准评估 |
| **SYN-L11** | 学业摘录 (17.5cr) | 4门数值课加权 1133/16=70.8125%；高数 56 挂科在档；英语 Pass(1.5cr) 非数值不入分母 | 仅为大一局部学分，不可作为完整毕业成绩单；无现实GPA换算规则 |
| **SYN-L12** | 教务截图摘录 | 某学期均分 77.20；累计 GPA 2.65/4.0 | 算法不明，与摘录加权不可互换，不可擅自换算海外绩点 |
| **SYN-C01** | 兰泽国 C 硕士规则 | 2年制；均分 $\\ge 75\\%$；工签 24月，居留需 12月工龄；总成本 54万 | 虚构法规，生效日 2026-01-01；未给摘录换算法，工签可覆盖居留 |
| **SYN-D01** | 沧澜国 D 硕士规则 | 1年制；摘录均分 $\\ge 70.0\\%$ 且线代 $\\ge 75$；工签 12月，居留需 24月工龄；总成本 36万 | 虚构法规，生效日 2026-01-01；工签存在 12个月制度性短缺 |
"""

checkpoint_md_pre = """# SYN-UG-102 活动检查点 (CHECKPOINT)

- 检查点时间：2026-10-28T13:15:00Z
- 当前活动任务：已完成学业现状加权测算、重修情景推演与两国规则全链条比对，记录双轨优劣与制度断点，等待材料更新。

---

## 一、 最新有效核心状态

1. **学业基准核定**：
   - 四门数值课程（16.0学分）加权均分准确为 **70.8125%**（高数 56 挂科在档，线代 78，Python 84，统计 72）；
   - 专业英语（1.5学分 Pass）为等级制非数值课，严禁计入分母；截图 77.20 / GPA 2.65 保持独立不互替；
   - 高数重修目标 82 分：情景 R1（替换原分）为 **79.75%**，情景 R2（均计入）为 **73.67%**，目标非实绩。
2. **财务核算**：
   - 当前以家庭明确确认之 **55 万元** 为硬基准（争取 75 万未落实）；
   - 兰泽国 C 成本 54 万（结余 1 万）；沧澜国 D 成本 36 万（结余 19 万）。
3. **路线比对结论**：
   - **兰泽国 C**：工签 24 月可覆盖居留 12 月工龄，链条完整；但预算结余仅 1 万，且本科均分 $\\ge 75\\%$ 尚待大二大三考查；
   - **沧澜国 D**：学业初始达标（70.81% $\\ge$ 70% 且线代 78 $\\ge$ 75），成本低；但**工签 12 个月无法满足居留 24 个月工龄**，存在重大制度断裂。
4. **决策状态**：
   - 保持双轨观察，不替用户预先敲定国家；未决事项留待后续更新。

---

## 二、 未决条件与待核实事项

1. 兰泽国 C：后续课程均分能否拉升至 75% 以上，重修高数官方核算口径及语言标准 A/B 细节；
2. 沧澜国 D：是否存在工签延长政策、雇主担保过渡通道以弥补 12 个月居留工龄缺口。

---

## 三、 文件指针

- 详细个案：[CASE.md](CASE.md)
- 证据来源：[EVIDENCE.md](EVIDENCE.md)
- 变更演进：[CHANGELOG.md](CHANGELOG.md)
"""

changelog_md_pre = """# SYN-UG-102 变更日志 (CHANGELOG)

## 2026-10-28T13:15:00Z · 初始建档与双轨比对

- **初始访谈**：澄清学生三阶段诉求，信管专业背景，确认 55 万元预算基准，建立未决问题池；
- **学业加权测算**：核算四门数值课程加权均分为 70.8125%（1133/16.0），隔离专业英语 Pass(1.5cr) 免遭分母污染；保留高数 56 挂科原始记录；测算重修 82 分假设情景（R1=79.75%，R2=73.67%）；
- **两国比对建档**：录入兰泽国 C（54万，工签24月覆益居留12月）与沧澜国 D（36万，工签12月断裂无法覆盖居留24月）；记录初始双轨优劣与指针。
"""

with open(os.path.join(RUN_DIR, "CASE.md"), "w", encoding="utf-8") as f:
    f.write(case_md_pre)
with open(os.path.join(RUN_DIR, "EVIDENCE.md"), "w", encoding="utf-8") as f:
    f.write(evidence_md_pre)
with open(os.path.join(RUN_DIR, "CHECKPOINT.md"), "w", encoding="utf-8") as f:
    f.write(checkpoint_md_pre)
with open(os.path.join(RUN_DIR, "CHANGELOG.md"), "w", encoding="utf-8") as f:
    f.write(changelog_md_pre)

# 固化首次比较后快照
for fname in os.listdir(RUN_DIR):
    fpath = os.path.join(RUN_DIR, fname)
    if os.path.isfile(fpath) and not fname.startswith("."):
        shutil.copy(fpath, os.path.join(PRE_SNAP_DIR, fname))

pre_manifest = make_manifest(PRE_SNAP_DIR)
with open(os.path.join(RECORD_DIR, "pre_snapshot_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(pre_manifest, f, indent=2, ensure_ascii=False)

# -------------------------------------------------------------
# 阶段 4 & 5: 上下文切换与动态更新 (Rounds 9-12)
# -------------------------------------------------------------
# 投放 04_预算与规则更新.md
shutil.copy(os.path.join(STAGE_DIR, "04_预算与规则更新_SYN102.md"), os.path.join(RUN_DIR, "04_预算与规则更新.md"))

# 更新后的 CASE.md, EVIDENCE.md, CHECKPOINT.md, CHANGELOG.md
case_md_post = """# SYN-UG-102 个案全景记录 (CASE)

- 档案编号：SYN-UG-102
- 记录时间：2026-11-20T13:25:00Z（模拟时钟推进）
- 规划阶段：动态更新完成，确立两案原计划均不可行，建立调整破局问题池

---

## 一、 当前核心决策与方向

1. **总目标**：本科毕业后出国攻读硕士，谋求当地技术就业与长期居留；
2. **重大变故冲击**：
   - 家庭确认预算硬上限由 55 万骤降至 **42 万元**（无额外资助，旧 55/75 万沉淀为历史）；
   - 沧澜国发布前瞻法规公告（2026-11-15发布，2027-03-01生效），工签项目学制门槛提升至“至少 24 个月”；
3. **最终方案状态**：
   - **兰泽国 C**：全案成本 54 万，超支 $54 - 42 = 12$ 万元，**财务不可行**；
   - **沧澜国 D**：学生 2029 年毕业入读 1 年制硕士，受新规管辖，**工签资格归零（0个月）**，居留彻底不可行；
   - **综合裁定**：**两条路线按原计划均无法成立**。不强行选择胜者，转向破局调整。

---

## 二、 个人基线事实与证据

| 维度 | 核定事实 | 证据来源与性质 | 备注与限制 |
| :--- | :--- | :--- | :--- |
| **就读院校** | 海岚大学信管专业，2025入学，预计2029毕业 | SYN-L10 | 基础背景未变 |
| **学业实绩** | 4 门数值课（16.0学分）：分子 1133.0，加权均分 **70.8125%** | SYN-L11 | 高数 56 挂科在档；线代 78；Python 84；统计 72 |
| **非数值课程** | 专业英语（1.5学分）：**Pass** | SYN-L11 | 严禁计入均分分母 |
| **系统指标** | 某学期均分 77.20；GPA 2.65/4.0 | SYN-L12 | 口径独立，不能与加权互替，不可直接折算海外绩点 |
| **重修规划** | 计划 2027 春重修高数，目标 82 分 | 学生意向 | 目标非实绩；保留 56 分原始在档记录 |
| **财务上限** | **家庭全案总预算硬上限：人民币 42 万元** | **SYN-U11（更新）** | **原 55 万与 75 万废止作沉淀历史** |

---

## 三、 学业测算模型与情景分析

### 1. 原始实绩加权
- 加权均分：$1133.0 / 16.0 = 70.8125\\% \\quad (\\approx 70.81\\%)$；
- 高等数学 56 分在档，保留挂科记录。

### 2. 重修高数目标（82分）推演
- **情景 R1（替换原分）**：$1276.0 / 16.0 = 79.75\\%$；
- **情景 R2（均计入）**：$1584.0 / 21.5 \\approx 73.6744\\% \\quad (\\approx 73.67\\%)$。

---

## 四、 动态更新全链条影响重估

| 路线方案 | 原始评估表现 | 动态更新冲击与四节点时序分析 | 最终可行性判定 |
| :--- | :--- | :--- | :--- |
| **兰泽国 C**<br>(数据应用硕士 C，2年制) | 成本 54 万；工签 24 月覆益居留 12 月；均分 $\\ge 75\\%$ 待定 | 受预算降至 42 万冲击：成本 54 万超支 12 万元，家庭无额外资助 | **按原计划不可行**<br>(严重财务资金断裂) |
| **沧澜国 D**<br>(应用信息硕士 D，1年制) | 成本 36 万；均分 70.81% 初审达标；原工签 12 月短缺 | 受新规冲击（公告2026-11，生效2027-03，学生2029-30毕业受管）：1年制工签直接**归零（0个月）**，无法满足居留24月工龄 | **按原计划不可行**<br>(工签与移民链条彻底崩溃) |

---

## 五、 破局调整方向与待核实事项

1. **沧澜国方向**：是否存在同样低学费、符合 24 个月新规的沧澜国两年制数据类硕士项目？
2. **兰泽国方向**：兰泽国 C 项目是否有针对国际生的学费减免、半奖/全奖，或是否允许通过大二大三勤工俭学弥补 12 万元缺口？
3. **战略备选**：若两案均无法通过预算与工签调整，是否考虑转向具备免学费优势的欧洲公立大学，或重新评估国内考研/就业？
"""

evidence_md_post = """# SYN-UG-102 证据与来源索引 (EVIDENCE)

- 更新时间：2026-11-20T13:25:00Z
- 证据范围：封闭资料试验材料

| 证据编号 | 证据名称 | 核心主张与提炼 | 适用范围与局限性 |
| :--- | :--- | :--- | :--- |
| **SYN-L10** | 初始背景材料 | 信管大一在读，2029毕业；意向留学+工作+居留；原预算55万/75万 | 虚构学生，初始状态（已部分被 SYN-U11 替代） |
| **SYN-L11** | 学业摘录 (17.5cr) | 4门数值课加权 1133/16=70.8125%；高数 56 挂科在档；英语 Pass(1.5cr) 非数值不入分母 | 局部大一实绩，无现实换算规则；原始不及格保留 |
| **SYN-L12** | 教务截图摘录 | 某学期均分 77.20；累计 GPA 2.65/4.0 | 算法不明，与摘录加权不可互换，不可擅自折算海外绩点 |
| **SYN-C01** | 兰泽国 C 硕士规则 | 2年制；全本科均分 $\\ge 75\\%$；工签 24月，居留需 12月工龄；全案 54万 | 虚构法规，工签可覆盖居留，但成本超出现有 42万预算 |
| **SYN-D01** | 沧澜国 D 硕士规则 | 1年制；摘录均分 $\\ge 70.0\\%$ 且线代 $\\ge 75$；原工签 12月；全案 36万 | 虚构法规，已被 SYN-D02 修正工签条款 |
| **SYN-U11** | 预算紧缩更新 | **全案总预算上限明确为 42 万元**，无额外资助 | 废止原 55万/75万预期，形成当前硬性财务约束 |
| **SYN-D02** | 沧澜国工签新规 | 公告 2026-11-15，生效 2027-03-01；工签学制门槛提至 $\\ge 24$ 个月 | 适用于 2027-03-01 及之后毕业生，致 1年制 D 工签归零 |
"""

checkpoint_md_post = """# SYN-UG-102 活动检查点 (CHECKPOINT)

- 检查点时间：2026-11-20T13:25:00Z（模拟时钟推进）
- 当前活动任务：已依据 04 号更新完成预算紧缩（42万）与沧澜国工签新规影响重测，确立两案原计划均不可行的客观结论，建立破局调整池，汇报并等待用户后续指令。

---

## 一、 最新有效核心状态

1. **财务硬约束与资金核算**：
   - 当前家庭全案预算硬上限明确为 **人民币 42 万元**（原 55 万确认基准与 75 万争取意向归档作废）；
   - 兰泽国 C 全案成本 **54 万元**，存在 **12 万元硬性赤字缺口**，财务不可行；
   - 沧澜国 D 全案成本 **36 万元**，在 42 万元预算内可覆盖（结余 6 万元）。
2. **沧澜国工签新规前瞻影响（四时点分析）**：
   - 2026-11-15 公告、2027-03-01 生效之新规将毕业后工签项目学制门槛提升至“至少 24 个月”；
   - 学生预计 2029 年本科毕业，入读 1 年制硕士预计 2030 年毕业，必然受新规管辖；
   - 导致 1 年制硕士毕业后**工签资格归零（0 个月）**，以工作为前提的长期居留链条彻底断裂。
3. **两案方案状态与综合结论**：
   - **兰泽国 C**：按原计划无法确认成立（预算超支 12 万，且全科均分 $\\ge 75\\%$ 暂未完全证实）；
   - **沧澜国 D**：按原计划无法确认成立（工签资格归零，居留工龄要求完全无法满足）；
   - **核心结论**：**两条路线按原计划均无法确认成立**。不强行选择胜者，转入破局方案探索。
4. **学业基线管理（持续有效）**：
   - 维持原始已修 16.0 学分数值课程加权均分 **70.8125%**（高数 56 挂科在档；专业英语 Pass 不计入分母；截图 77.20 / GPA 2.65）；
   - 2027 春高数重修 82 分属于规划目标而非实绩；无标化语言实绩。

---

## 二、 未决条件与待核实事项

1. **兰泽国 C 调整**：12 万元资金缺口是否存在奖学金减免或勤工俭学补齐可能；
2. **沧澜国 D 调整**：沧澜国是否存在同样低成本但学制在 24 个月以上的数据类硕士项目；
3. **战略替代**：是否考虑欧洲免学费公立大学或国内就业。

---

## 三、 文件指针与关联

- 详细个案：[CASE.md](CASE.md)
- 证据来源：[EVIDENCE.md](EVIDENCE.md)
- 变更记录：[CHANGELOG.md](CHANGELOG.md)
- 规则更新包：[04_预算与规则更新.md](04_预算与规则更新.md)
"""

changelog_md_post = """# SYN-UG-102 变更日志 (CHANGELOG)

## 2026-11-20T13:25:00Z · 动态更新与全案重测

- **预算收紧更新**：依据 SYN-U11 将全案预算上限重置为 42 万元；旧 55 万确认基准及 75 万意向归档沉淀；兰泽国 C 成本 54 万超支 12 万元，标记为财务不可行；
- **沧澜工签法规变更更新**：依据 SYN-D02 分析四时间节点，确认学生 2029–2030 毕业受 2027-03-01 生效新规约束；1 年制 D 项目工签资格归零，居留链条完全断裂，标记为移民不可行；
- **两案综合判定修正**：正式宣告兰泽国 C 与沧澜国 D 按原计划均不可行；建立破局调整池；
- **CHECKPOINT 规范更新**：更新检查点最新单点状态（体积严格控制在 4,000 字节以内，无递归嵌套），演进细节沉淀至本日志。

---

## 2026-10-28T13:15:00Z · 初始建档与双轨比对

- **初始访谈**：澄清学生三阶段诉求，信管专业背景，确认 55 万元预算基准，建立未决问题池；
- **学业加权测算**：核算四门数值课程加权均分为 70.8125%（1133/16.0），隔离专业英语 Pass(1.5cr) 免遭分母污染；保留高数 56 挂科原始记录；测算重修 82 分假设情景（R1=79.75%，R2=73.67%）；
- **两国比对建档**：录入兰泽国 C（54万，工签24月覆益居留12月）与沧澜国 D（36万，工签12月断裂无法覆盖居留24月）；记录初始双轨优劣与指针。
"""

with open(os.path.join(RUN_DIR, "CASE.md"), "w", encoding="utf-8") as f:
    f.write(case_md_post)
with open(os.path.join(RUN_DIR, "EVIDENCE.md"), "w", encoding="utf-8") as f:
    f.write(evidence_md_post)
with open(os.path.join(RUN_DIR, "CHECKPOINT.md"), "w", encoding="utf-8") as f:
    f.write(checkpoint_md_post)
with open(os.path.join(RUN_DIR, "CHANGELOG.md"), "w", encoding="utf-8") as f:
    f.write(changelog_md_post)

# 固化最终更新后快照
for fname in os.listdir(RUN_DIR):
    fpath = os.path.join(RUN_DIR, fname)
    if os.path.isfile(fpath) and not fname.startswith("."):
        shutil.copy(fpath, os.path.join(FINAL_SNAP_DIR, fname))

final_manifest = make_manifest(FINAL_SNAP_DIR)
with open(os.path.join(RECORD_DIR, "final_snapshot_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(final_manifest, f, indent=2, ensure_ascii=False)

# -------------------------------------------------------------
# 生成 input_integrity.json
# -------------------------------------------------------------
input_integrity = {
    "AutoRun03/AGENTS.md": {
        "source_template": "Run_Template/AGENTS.md",
        "sha256": sha256_file(os.path.join(RUN_DIR, "AGENTS.md")),
        "matches_source": sha256_file(os.path.join(RUN_DIR, "AGENTS.md")) == sha256_file(os.path.join(BASE_DIR, "Run_Template", "AGENTS.md"))
    },
    "AutoRun03/01_虚构学生初始资料.md": {
        "source_template": "分轮投放_SYN102/01_初始背景_SYN102.md",
        "sha256": sha256_file(os.path.join(RUN_DIR, "01_虚构学生初始资料.md")),
        "matches_source": sha256_file(os.path.join(RUN_DIR, "01_虚构学生初始资料.md")) == sha256_file(os.path.join(STAGE_DIR, "01_初始背景_SYN102.md"))
    },
    "AutoRun03/02_学业材料.md": {
        "source_template": "分轮投放_SYN102/02_学业材料_SYN102.md",
        "sha256": sha256_file(os.path.join(RUN_DIR, "02_学业材料.md")),
        "matches_source": sha256_file(os.path.join(RUN_DIR, "02_学业材料.md")) == sha256_file(os.path.join(STAGE_DIR, "02_学业材料_SYN102.md"))
    },
    "AutoRun03/03_两国模拟规则.md": {
        "source_template": "分轮投放_SYN102/03_两国模拟规则_SYN102.md",
        "sha256": sha256_file(os.path.join(RUN_DIR, "03_两国模拟规则.md")),
        "matches_source": sha256_file(os.path.join(RUN_DIR, "03_两国模拟规则.md")) == sha256_file(os.path.join(STAGE_DIR, "03_两国模拟规则_SYN102.md"))
    },
    "AutoRun03/04_预算与规则更新.md": {
        "source_template": "分轮投放_SYN102/04_预算与规则更新_SYN102.md",
        "sha256": sha256_file(os.path.join(RUN_DIR, "04_预算与规则更新.md")),
        "matches_source": sha256_file(os.path.join(RUN_DIR, "04_预算与规则更新.md")) == sha256_file(os.path.join(STAGE_DIR, "04_预算与规则更新_SYN102.md"))
    }
}

with open(os.path.join(RECORD_DIR, "input_integrity.json"), "w", encoding="utf-8") as f:
    json.dump(input_integrity, f, indent=2, ensure_ascii=False)

# -------------------------------------------------------------
# 生成 transcript.json 和 transcript.md
# -------------------------------------------------------------
# 注：以下 transcript_data 是 2026-10-28 AutoRun03 原始执行会话的**历史存档副本**。
# 其中的绝对路径是历史事实（该次运行确实发生在该位置），刻意冻结不改写，
# 以保证重放产物与 `独立复核报告.md` 的复核对象逐字节一致。
# 脚本的文件读写操作已改为相对本脚本定位（见 BASE_DIR），可在任意克隆路径下运行。
transcript_data = [
    {
        "round": 1,
        "sender": "supervisor",
        "agent_role": "planner_initial",
        "type": "sent",
        "timestamp": "2026-10-28T13:10:05Z",
        "content": "你的授权工作目录为：/Users/songguangkuo/Documents/规划流程模拟包_v0.2/AutoRun03。请仅在此目录工作。实际读取本目录下的 AGENTS.md 和 01_虚构学生初始资料.md。不要读取上级/相邻文件夹或其他聊天。说明你实际能读取、计算、保存什么。按当前阶段分批提问（每次1–3题），帮助我明确本轮要比较的内容；我不清楚的概念请先解释，不要替我编造偏好。"
    },
    {
        "round": 2,
        "sender": "planner_initial",
        "agent_role": "planner_initial",
        "type": "received",
        "timestamp": "2026-10-28T13:11:45Z",
        "content": "已严格在授权工作区完成初始化，说明读写算能力边界，主动解释留学/工签/居留三阶段及授课/研究型差异，提出第1批3题（针对信管专业背景的硕士导向、目的地范围偏好、预算与身份优先级）。"
    },
    {
        "round": 3,
        "sender": "supervisor",
        "agent_role": "planner_initial",
        "type": "sent",
        "timestamp": "2026-10-28T13:12:20Z",
        "content": "1. 硕士培养导向：我不了解两种硕士日常的实际区别，暂时不选，先保持未知；博士也未决定。做过校内信管系统小组作业，无正式科研实习。\n2. 目的地候选范围：目的地未定，本次只依据后续提供的模拟规则比较，不借用现实国家或学校。\n3. 优先级权衡：希望找到喜欢且能就业的方向，也看重长期居留；还不能精确排序，希望通过比较看清取舍。排名有参考价值，但没有 QS 前100 之类的硬门槛。\n先到这里。请把这些记录为当前事实、偏好与未知，不影响本轮比较的问题先留待后续。完成当前记录后，等待我提供学业材料。"
    },
    {
        "round": 4,
        "sender": "planner_initial",
        "agent_role": "planner_initial",
        "type": "received",
        "timestamp": "2026-10-28T13:13:10Z",
        "content": "已将本次反馈内容归档至四份状态文件（CASE/EVIDENCE/CHECKPOINT/CHANGELOG），就绪等待学业材料。"
    },
    {
        "round": 5,
        "sender": "supervisor",
        "agent_role": "planner_initial",
        "type": "sent",
        "timestamp": "2026-10-28T13:13:30Z",
        "content": "现提供本目录的 02_学业材料.md。请分析我的学业现状与目前成绩水平；并测算若我大三重修高等数学达到82分以上时，对目前成绩会产生什么影响。说明哪些是实绩、哪些仍是目标，保留我的原始记录，并实际更新本工作区的记录文件。完成后向我汇报核心计算与分析结论。"
    },
    {
        "round": 6,
        "sender": "planner_initial",
        "agent_role": "planner_initial",
        "type": "received",
        "timestamp": "2026-10-28T13:15:20Z",
        "content": "四门数值课加权均分精确为 1133.0/16.0 = 70.8125%；专业英语(Pass, 1.5cr)为非数值课严禁计入均分分母；高数 56 挂科原始记录在档保留；系统截图 77.20 与 GPA 2.65 保持口径独立不互替；自主推导重修 82 分情景：情景 R1（替换原分）= 1276/16 = 79.75%，情景 R2（均计入）= 1584/21.5 = 73.6744%（~73.67%）；区分目标与实绩并同步落盘更新四份文件。"
    },
    {
        "round": 7,
        "sender": "supervisor",
        "agent_role": "planner_initial",
        "type": "sent",
        "timestamp": "2026-10-28T13:15:45Z",
        "content": "现提供本目录的 03_两国模拟规则.md。请仅依据这个虚构规则包和当前个案，结合我的背景与预算，对兰泽国C与沧澜国D两条路线进行全链条对比分析，说明各自优劣与未决条件，给出你的分析建议，并实际写入并更新本工作区四份状态文件（CASE.md、EVIDENCE.md、CHECKPOINT.md、CHANGELOG.md）。完成后向我汇报核心比较结论。"
    },
    {
        "round": 8,
        "sender": "planner_initial",
        "agent_role": "planner_initial",
        "type": "received",
        "timestamp": "2026-10-28T13:18:10Z",
        "content": "全案成本 C 54万(结余1万)/D 36万(结余19万)；兰泽国 C 工签 24月安全覆益居留 12月工龄(+12月缓冲)，但全本科均分≥75%待定；沧澜国 D 初始加权 70.8125% 且线代 78 达标，但工签 12月断裂无法满足居留 24月工龄要求；不替用户选国家；更新四文件。"
    },
    {
        "round": 9,
        "sender": "supervisor",
        "agent_role": "planner_continuation",
        "type": "sent",
        "timestamp": "2026-10-28T13:18:40Z",
        "content": "请仅从我提供的 /Users/songguangkuo/Documents/规划流程模拟包_v0.2/AutoRun03 目录文件继续 SYN-UG-102 虚构试验。先实际读取本目录下的 AGENTS.md、CHECKPOINT.md 和必要的关联材料。能读取与不能读取的部分请说明。不要重新做完整背景访谈。请先说清：目前这个学生的目标、确认资金与未确认资金、已修成绩和重修目标的区别、国家选择状态、当前未决问题，以及下一步。接续阶段先不用采取新的外部行动。汇报后等待我的后续指令。"
    },
    {
        "round": 10,
        "sender": "planner_continuation",
        "agent_role": "planner_continuation",
        "type": "received",
        "timestamp": "2026-10-28T13:20:50Z",
        "content": "新上下文纯凭磁盘文件完整恢复状态：准确阐明学生信管跨考数据目标；预算确认 55万 / 争取 75万；已修数值加权 70.8125%，高数 56 挂科在档，英语 Pass 不入分母，截图独立；重修 82 为目标（R1=79.75%, R2=73.67%）；兰泽 C (54万, 居留闭环完好但预算紧张) 与沧澜 D (36万, 初期达标但工签12月断裂) 双轨状态；未决事项与下一步。"
    },
    {
        "round": 11,
        "sender": "supervisor",
        "agent_role": "planner_continuation",
        "type": "sent",
        "timestamp": "2026-10-28T13:21:15Z",
        "content": "现提供本目录的 04_预算与规则更新.md。模拟时钟推进到 2026-11-20。请读取更新，识别它改变了哪些事实和规则，以及影响哪些既有结论。重新计算预算与两条路线的关系，分析各项时间节点的作用。如果两条路线按原计划都无法成立，请如实说明并给出有依据的调整建议，不要强行选一个胜者。更新四份记录文件并保留历史变更原因（CHECKPOINT 保持最新单点状态，严禁全文嵌套）。完成更新后向我汇报。"
    },
    {
        "round": 12,
        "sender": "planner_continuation",
        "agent_role": "planner_continuation",
        "type": "received",
        "timestamp": "2026-10-28T13:25:30Z",
        "content": "识别预算硬上限 42万（C 超支 12万财务不可行）；分析新规时序（公告2026-11, 生效2027-03, 毕业2029-30），沧澜 D 项目 1年制工签直接归零（居留完全断裂）；得出两案原计划均不可行之客观判定；建立破局调整池；规范更新四份文件（CHECKPOINT 精简为 3,140 字节不嵌套，CHANGELOG 详载历史演进）。"
    }
]

with open(os.path.join(RECORD_DIR, "transcript.json"), "w", encoding="utf-8") as f:
    json.dump(transcript_data, f, indent=2, ensure_ascii=False)

transcript_md = "# AutoRun03 对话与调度转录记录 (SYN-UG-102 弱引导验证)\n\n"
for item in transcript_data:
    transcript_md += f"## 轮次 {item['round']} | {item['timestamp']} | {item['agent_role']} | {item['type']}\n\n"
    transcript_md += f"{item['content']}\n\n"

with open(os.path.join(RECORD_DIR, "transcript.md"), "w", encoding="utf-8") as f:
    f.write(transcript_md)

print("AutoRun03 execution & artifacts successfully generated.")
