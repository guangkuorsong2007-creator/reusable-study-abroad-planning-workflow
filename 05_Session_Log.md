# Session Log / 会话流水日志

本日志按时间倒序记录“可复用留学规划工作流程”产品库的所有 Agent 会话演进与开发记录。时间戳均使用精确测量时间 (`TZ=Asia/Shanghai date`)。

---

## 2026-10-29T10:14:00+08:00 · Antigravity · 双项目物理拆分完成与工作流独立产品库初始化 (WF-D001)

- **Request**: 用户确认执行双项目物理拆分工作计划（选项 1: 命名为 `可复用留学规划流程`；选项 A: 模拟包 v0.1/v0.2 移入新工作流目录；选项 I: 安全清理原工作区迁出文件）。
- **Execution & Outcome**:
  1. **独立产品仓库脚手架搭建**：创建 `/Users/songguangkuo/Documents/可复用留学规划流程/` 及其 `docs/`, `handoff/`, `templates/`, `simulations/` 目录；
  2. **核心文档与夹具迁移**：从原规划工作区拷贝 4 份核心方案（规划复盘草案、首轮试验说明、SYN-UG-102 验证方案、真实官方核验报告）至 `docs/`；拷贝 4 份接续提示词与教程至 `handoff/`；拷贝通用 `Run_Template/` 至 `templates/`；
  3. **模拟包全量整合**：将 `规划流程模拟包_v0.1` 与 `规划流程模拟包_v0.2` 平移至 `simulations/`，并在原位置保留向后兼容软链接；
  4. **全套独立治理文件构建**：撰写独立 `README.md`、`AGENTS.md`（严禁引入真实个人档案）、`00_Status.md`、`01_Framework.md`、`02_Roadmap.md`、`03_Decisions.md`（WF-D001+）、`04_Evidence_Registry.md` 与本日志；
  5. **哈希与数据一致性认证**：全量 8 份迁移文档与 123 份模拟包文件经 SHA-256 哈希比对 100% 逐字节吻合。
- **Files Created**:
  - `README.md`, `AGENTS.md`, `00_Status.md`, `01_Framework.md`, `02_Roadmap.md`, `03_Decisions.md`, `04_Evidence_Registry.md`, `05_Session_Log.md`；
  - `docs/` 4 文件、`handoff/` 4 文件、`templates/Run_Template/` 4 文件；
  - `simulations/` 整合 `规划流程模拟包_v0.1` (39 文件) 与 `规划流程模拟包_v0.2` (84 文件)。
- **Next**: 待用户启动第二步外部商业客户端（如 Claude Code 或 Web 界面）手动投放测试；或由 Agent 继续推进工具化封装。

---

## 2026-11-04T10:53:58+08:00 · MCode (mavis) · v0.2 基线回归门复验与 v0.3 就绪度审计

- **Request**: 用户询问项目当前阶段与下一步动作（状态盘点型请求，未要求代码变更）。
- **Execution & Outcome**:
  1. **治理文件通读**：读取 `00_Status.md`、`01_Framework.md`、`02_Roadmap.md`、`03_Decisions.md`、`04_Evidence_Registry.md`、`05_Session_Log.md`，确认 v0.2 完成、v0.3 未启动。
  2. **基线回归门复验**：执行 `simulations/规划流程模拟包_v0.2/run_autorun03.py`（经兼容软链接路径）→ 成功，EXIT=0；重生成 `CHECKPOINT.md` 2,512 B、`CASE.md` 3,756 B，与 `独立复核报告.md` 声明值逐字节吻合；`input_integrity.json` 5/5 `matches_source: true`；`transcript.json` 12 条收发节点完整。
  3. **方法学澄清（重要）**：核查脚本源码确认 `run_autorun03.py` 为**确定性重放器**——CASE/EVIDENCE/CHECKPOINT 正文以硬编码断言写入脚本，脚本不实际调用 LLM。15/15 属"产物 + 转录"独立复核判定，非实时智能体评分；实时执行仅存于 2026-10-28 原始 AutoRun03 会话。此结论已写入 `00_Status.md`。
  4. **v0.3 就绪度审计**：定位 4 项缺口 —— G1 `Run_Template/AGENTS.md` 仍标注 SYN-UG-101 且哈希已入证据链（不可原地改）；G2 `仅供评测者/03_结果记录模板.md` 仍为 SYN-UG-101 量表（会导致 SYN-UG-102 外部投放必然误判 FAIL）；G3 `run_autorun03.py` 硬编码绝对路径（仅靠软链接存活，不可开源分发）；G4 缺 LICENSE/.gitignore/Git 仓库（与 AGENTS.md 公开分发合规要求不符）。
- **Files Modified**:
  - `00_Status.md`（阶段更新为"v0.2 回归门复验通过，v0.3 待启动"，新增 G1–G4 缺口表与方法学澄清）；
  - `05_Session_Log.md`（本条目）。
- **Files NOT Modified（刻意保留）**: `simulations/` 下全部产物与 `run_autorun03.py`——G1/G3 修复若直接改动将破坏 v0.2 冻结基线的 `input_integrity.json` 哈希证据链，须以 v0.3 新包形式发布。
- **Next**: 待用户在 v0.3 异构实测、G1–G4 修复、v0.4 工具化三条路径间裁定优先级。

---

## 2026-11-04T11:00:00+08:00 · MCode (mavis) · v0.3 外部投放包发布与 G1–G4 就绪度修复 (WF-D002)

- **Request**: 用户裁定推进路径为「修复 G1–G4 并发布 v0.3 模拟包」，并要求产出**双版本投放包**（文件读写型 + 纯粘贴手动保存型）。
- **Execution & Outcome**:
  1. **证据链边界核定**：读取 `pre_snapshot_manifest.json` / `final_snapshot_manifest.json` / `input_integrity.json`，确认哈希覆盖范围为 `AutoRun03/` 下 9 份产物 + 4 份投放材料 + `Run_Template/AGENTS.md`；判定 `run_autorun03.py` **不在哈希覆盖范围内**，可安全改造。
  2. **v0.3 模拟包搭建**：`simulations/规划流程模拟包_v0.3/`，含 `分轮投放_SYN102/`（4 份材料哈希与 v0.2 源逐字节一致）、`评测设计_SYN102/`、`Run_Template/`、`build_delivery.py`、`MANIFEST.json`。
  3. **G1 修复**：`Run_Template/AGENTS.md` 重写为**案例中立**模板（解除 SYN-UG-101 绑定与旧工作区名残留）；仓库根 `templates/Run_Template/` 同步替换。**v0.2 冻结基线零改动**。
  4. **G2 修复**：新增 `评测设计_SYN102/04_外部投放结果记录表_SYN102.md`——含观测元数据（客户端/模型/形态/污染观察/逐轮耗时与人工介入次数）、**硬指标实测栏**（由评测者直接测量，禁采信被测端自述）、15 项正确答案锚点、结论边界约束。
  5. **G3 修复**：`run_autorun03.py` 的 `BASE_DIR` 由硬编码绝对路径改为**以脚本自身目录定位**（`WF_AUTORUN03_BASE` 可覆盖）；`transcript_data` 内绝对路径**刻意冻结不改写**（属历史事实，改写即篡改证据）。
  6. **双版本投放包**：`03_外部投放包_文件读写版.md`（形态 A，含每轮文件准备表与哈希核对指引）、`04_外部投放包_纯粘贴手动保存版.md`（形态 B，5 份材料逐字内联 + 手工保存清单 + 体积核验命令）。六轮提示词**逐字取自 AutoRun03 基线 transcript**，保证与基准可比。
  7. **G4 修复**：补 `LICENSE`（MIT + 数据合规声明）、`.gitignore`、初始化 Git 仓库并完成首次入库（150 文件）。
- **验收证据（均实测通过）**：
  - 改造后 `run_autorun03.py` 重放，9 份产物 + `transcript.json` 哈希与改造前**完全一致，零漂移**；
  - 迁移副本（无软链接、无原路径）运行，产物与母库**逐字节一致**；
  - v0.3 生成器内置自校验：5 份材料逐字内联校验通过（初次生成曾因占位符缺失漏插 3 份材料，已修复并加装自校验防回归）；
  - Git 入库敏感路径（天津*/.env/secret/private）命中 **0**。
- **Files Created**:
  - `simulations/规划流程模拟包_v0.3/`（10 份：分轮投放 4 + 评测设计 4 + Run_Template 4 + MANIFEST + build_delivery.py）；
  - `LICENSE`、`.gitignore`。
- **Files Modified**:
  - `templates/Run_Template/AGENTS.md`、`templates/Run_Template/01_虚构学生初始资料.md`（案例中立化）；
  - `simulations/规划流程模拟包_v0.2/run_autorun03.py`（仅路径解析改造，产物零漂移）；
  - `README.md`（v0.3 投放包指引 + 可移植性与方法学提示）、`00_Status.md`、`02_Roadmap.md`、`03_Decisions.md`（新增 WF-D002）、`04_Evidence_Registry.md`、`05_Session_Log.md`。
- **Files NOT Modified（刻意保留）**: `simulations/规划流程模拟包_v0.2/` 全部产物与快照、`仅供评测者/03_结果记录模板.md`（作 SYN-UG-101 历史记录留存）。
- **Next**: 待用户执行真实外部客户端投放（形态 A/B 二选一），回收后填结果记录表并归档至 `评测记录/外部投放_<客户端>_<日期>/`。

---

## 2026-11-04T11:36:49+08:00 · MCode (mavis) · 运行实例四文件命名统一 (WF-D003)

- **Request**: 用户同意推进 v0.4 命名统一；同时询问「人工投放投放包」到底在做什么。
- **Execution & Outcome**:
  1. **分布核查**：`grep` 全仓统计两套命名的实际分布——概念层（`01_学生初始画像` 等）仅出现于 **4 份**治理/说明文档；操作层（`CASE/EVIDENCE/CHECKPOINT/CHANGELOG`）出现于 **50 个**文件（全部 `Run_Template`、v0.1–v0.3 基线产物、快照、转录、v0.3 双版本投放包）。
  2. **性质判定**：两套不只是命名不同，**职责划分也不同**——概念层将「学生画像」与「选校进展」拆为两文件；操作层将二者合并入 `CASE.md`，并独有 `EVIDENCE.md` 作为来源可追溯性载体（对应 15 项量表第 15 项「全流程透明度」）。
  3. **决策 (WF-D003)**：以操作层命名为唯一规范命名；概念层表述降级为映射说明。
     - **否决反向统一**（改操作层）：需重命名模板 → 破坏 `input_integrity.json` 与阶段快照哈希 → 量表第 10 项判定标准脱节 → v0.3 已发布投放包需重生成 → 已完成的外部投放将被错误评分；代价远大于收益。
  4. **文档同步**：`01_Framework.md` 第二节重写为「规范层职责表 + 概念层→规范层归位映射表 + 冻结基线命名保留说明」；`AGENTS.md` 第 2 条规约补入规范命名、单一事实源原则与命名历史；`README.md` 第 2 节同步。
  5. **遗留问题发现（未处理，待裁定）**：`handoff/` 4 份文件为 **WF-D001 物理拆分前的个人工作区遗留**，内容指向已分离的 `未来规划`、`01_Profile.md`、`方案/`、`个人档案` 等不存在路径，且 `规划流程复用_跨Agent接续入口.md` 第 35 行「不要初始化 Git」与本轮 G4 已初始化 Git 相矛盾。
- **Files Modified**: `01_Framework.md`、`AGENTS.md`、`README.md`、`00_Status.md`、`03_Decisions.md`（新增 WF-D003）、`05_Session_Log.md`。
- **Files NOT Modified**: `simulations/` 下全部基线产物、快照与哈希记录（**零改动**，命名统一为纯文档层操作）。
- **Next**: 待用户执行外部投放；`handoff/` 遗留文件是否重写待裁定。

---

## 2026-11-04T11:41:27+08:00 · MCode (mavis) · handoff 接续入口重写与仓库死链清理 (WF-D004)

- **Request**: 用户确认「听你的直接动手」——采纳上一轮建议，重写 `handoff/` 4 份遗留文件以消除死链与隐私冲突。
- **Execution & Outcome**:
  1. **死链全量扫描**：全仓 `/Users/songguangkuo` 引用按目录分布统计——`simulations/规划流程模拟包_v0.2` 28 处、v0.1 11 处（多属历史转录与冻结基线）、`handoff/` 13 处（**功能性死链**）、`docs/` 1 处、`AGENTS.md`/`00_Status.md`/`05_Session_Log.md`/`03_Decisions.md` 各 1–2 处（引用性表述，保留）。
  2. **哈希覆盖核验**：确认 v0.2 的 `00_从这里开始_全流程教程.md` 与 `01_让Agent自动执行_调度提示词.md` **不在** `pre/final_snapshot_manifest.json` 与 `input_integrity.json` 覆盖范围，属运营文档而非证据产物，可安全改造。
  3. **handoff 4 份全部重写**：
     - `规划流程复用_跨Agent接续入口.md`：改指当前产品库阅读顺序与材料位置，**保留并升级「证据边界与局限」整节**（补入重放脚本性质、重置命名规则、数据保护）；
     - `规划流程复用_可复制启动提示词.md`：改指本产品库，删去「个人档案」指令与 `未来规划` 路径，新增隐私红线前提、命名规则与 v0.3 准备动作；
     - `自动模拟运行结果.md`：由 AutoRun01 单点记录改为**历次运行汇总索引**（AutoRun01/02/03 + v0.3 待执行），链接全部改仓库相对路径，原叙述与「证据边界与审计校准」6 条完整保留并增至 6 条；
     - `新Agent模拟教程入口.md`：改为「现在该用哪套包」对照表，指向 v0.3 双版本投放包与 v0.2 教程，保留答案卡隔离/不联网/诚实记录边界三纪律，补充形态 B 固有局限。
  4. **每份文件加「历史说明」段**，显式声明旧指向已于 WF-D001 作废，避免与历史存档混淆。
  5. **v0.2 运营文档路径参数化**：教程与调度提示词中的绝对路径改为相对模拟包根目录；两处「真实『未来规划』」表述改为「模拟包以外的任何目录」。
- **Files Modified**:
  - `handoff/规划流程复用_跨Agent接续入口.md`、`handoff/规划流程复用_可复制启动提示词.md`、`handoff/自动模拟运行结果.md`、`handoff/新Agent模拟教程入口.md`（**全部重写**）；
  - `simulations/规划流程模拟包_v0.2/00_从这里开始_全流程教程.md`、`.../01_让Agent自动执行_调度提示词.md`（路径参数化）；
  - `03_Decisions.md`（新增 WF-D004）、`04_Evidence_Registry.md`（新增第四节接续入口索引）、`00_Status.md`、`05_Session_Log.md`。
- **Files NOT Modified**: `AutoRun01/02/03` 全部产物、快照、manifest、转录、输入材料、答案卡；`v0.1` 全包；`v0.3` 全包；`Run_Template/AGENTS.md`（其哈希已入 `input_integrity.json`，其中旧工作区名属历史快照，保留原貌）。
- **Next**: 待用户执行 v0.3 外部投放；回收结果后按结果记录表复核并归档登记。

---

## 2026-11-04T11:56:50+08:00 · MCode (mavis) · v0.4 工具化：wf-verify 校验器与 wf-init 脚手架 (WF-D005)

- **Request**: 用户批准推进 v0.4 工具化——「做掉」。
- **Execution & Outcome**:
  1. **规则设计对着真实产物做**：先通读 AutoRun03 的 `CHECKPOINT.md`、`CASE.md`、`02_学业材料.md` 结构与各文件百分比分布，再据此设计检查项，避免凭空猜规则。
  2. **`tools/wf_core.py`**：学分表解析（等级制非数值课程自动识别）、加权均分复算、均分/情景指标抽取、嵌套与自重复检测（difflib 最长公共子串）、隐私模式扫描；共用核心库。
  3. **`tools/wf-verify`**：分级输出（ERROR/WARN/INFO）、`--json`、`--strict`、`--quiet`、退出码（0 通过 / 1 失败）。
  4. **`tools/wf-init`**：按材料内容自动归位到标准文件名，生成案例中立目录与四文件骨架（内嵌单一事实源、不擅自换算、目标非实绩、CHECKPOINT 硬限与禁嵌套、未知即记未知五条纪律），**不拷入任何答案卡**。
  5. **实测三个基线**：AutoRun02/03 全绿；**AutoRun01 检出真实历史缺陷**（`CHECKPOINT` 实测 4,572 B，与文档记录的 4,572 B 吻合，超硬上限；`CASE` 超软上限）。
  6. **阴性用例 7/7 全部正确报 FAIL**（退出码 1）：CHECKPOINT 超体积、误用算术均分、CHECKPOINT 嵌套旧全文、缺失文件、真实院校+学号泄漏、跨文件均分漂移、空文件。
- **开发中修正的实现缺陷**（均由实测暴露，非推测）：
  - 均分抽取误把 `平均分`（某学期平均分）当作 `均分` —— 加 `(?<!平)` 前瞻排除；
  - 公式分子 `加权均分 1133.0 / 16.0` 被当作均分值 —— 增加「后接 `/` 即跳过」判据；
  - 教务截图指标 `某学期平均分 77.20` 被当作实绩均分 —— 增加系统/截图语境排除；
  - 情景语境 `均分升至 82.50 分` 被当作实绩 —— 引入连接词白名单 + 情景/门槛语境排除；
  - v0.1 期裸数字写法 `约70.71分` 未被识别 —— 增加句式回退与 `加权平均` 同义词；
  - `wf-init` 材料归位错乱（`04_预算与规则更新` 同时命中「规则」被误归 03）—— 路由改为按具体性排序并去重；
  - 骨架态被误报为 ERROR —— 「尚未声明」降级为 WARN。
- **Files Created**: `tools/wf_core.py`、`tools/wf-verify`、`tools/wf-init`、`tools/README.md`。
- **Files Modified**: `README.md`（目录结构 + 工具化使用说明）、`02_Roadmap.md`（v0.4 标记交付）、`00_Status.md`、`03_Decisions.md`（新增 WF-D005）、`05_Session_Log.md`。
- **Next**: 待用户执行 v0.3 外部投放；回收后按结果记录表复核归档。工具的 CI 接入与更多指标自动判定列为 v0.4 后续待办。

---

## 2026-11-04T12:07:47+08:00 · MCode (mavis) · v0.4 收尾：判定扩展、持续集成与仓库可分发性扫描 (WF-D006)

- **Request**: 用户批准推进 v0.4 收尾两件事——「接入 CI」与「扩展自动判定范围」。
- **Execution & Outcome**:
  1. **判定范围扩展（新增 5 项检查）**：`E010` EVIDENCE 证据表列数不足 / 局限列为空或占位符；`W007` CHANGELOG 空洞条目；`W008` CASE 必备章节不完备；`W009` CASE 未声明等级制课程排除处置；`W010` CASE 与 CHECKPOINT 金额锚点无交集。
  2. **`tools/selftest.py`**：证据链哈希完整性（input_integrity / PRE·FINAL 快照 manifest / v0.3 MANIFEST）+ 跨包一致性（v0.3 投放材料与评测设计须与 v0.2 源逐字节一致）+ 基线判定 + 7 类阴性用例（夹具临时生成，不入库）+ 可选 `--replay` 重放幂等。
  3. **`tools/scan_repo.py`**：仓库级可分发性扫描——隐私红线、真实院校名只许出现在治理文档反面示例（`simulations/` 内一律禁止）、markdown 相对链接全可达、操作型文档不得硬编码本机绝对路径。
  4. **`.github/workflows/verify.yml`**：push / PR / 手动触发五步——自测 → 重放幂等（`git diff --exit-code`）→ 现行基线 `--strict` → 投放包生成器幂等 → 仓库扫描。
  5. **v0.1 用户面文档路径参数化**：教程与调度提示词的绝对路径及旧工作区表述（核验二者不在任何哈希覆盖范围内）。
- **开发中修正的误判**（均由实测暴露）：
  - CASE 章节完备性初版误报「缺结论与下一步」——实际章节名为「五、 破局调整方向与待核实事项」，关键词集合过窄，已改为语义等价集合；
  - 非数值课程排除声明初版误报——原文是「**严禁计入**加权分母」，仅匹配「不计」二字会漏判，已改为否定式前置正则；
  - `scan_repo.py` 初版把工具自身的黑名单与阴性夹具误判为违规，已改为**显式豁免并注明理由**（而非放宽规则）；
  - `scan_repo.py` 初版把冻结快照中的 `file://` 绝对 URL 误判为死链，已改为只校验相对链接。
- **验收（全部实测）**：
  - 本地按 CI 五步逐条模拟执行，**全部通过**；
  - `selftest.py --replay`：**18 项检查全通过**，重放后 10 个产物逐字节不变；
  - `scan_repo.py`：0 项违规（2 条反面示例豁免记录），49 条相对链接全可达；
  - 扫描器自身阴性用例：注入真实校名 + 学号 + 死链后正确报 3 项违规并以退出码 1 失败；
  - `build_delivery.py` 重跑后 `simulations/` 零变更（生成器幂等）。
- **Files Created**: `tools/selftest.py`、`tools/scan_repo.py`、`.github/workflows/verify.yml`。
- **Files Modified**: `tools/wf_core.py`（新增检查与语义化关键词）、`tools/README.md`、`README.md`、`02_Roadmap.md`、`00_Status.md`、`03_Decisions.md`（新增 WF-D006）、`05_Session_Log.md`、`simulations/规划流程模拟包_v0.1/00_从这里开始_全流程教程.md` 与 `.../01_让Agent自动执行_调度提示词.md`（路径参数化）。
- **Files NOT Modified**: 全部哈希覆盖产物（AutoRun01/02/03 产物、快照、manifest、转录、输入材料、答案卡）；`simulations/规划流程模拟包_v0.2/Run_Template/AGENTS.md`；`v0.3` 已发布投放包内容。
- **Next**: 待用户执行 v0.3 外部投放；回收后按结果记录表复核归档。CI 在推送到 GitHub 后自动生效。

---

## 2026-11-04T12:47:42+08:00 · MCode (mavis) · 公开前合规审计与完全开源发布 (WF-D007)

- **Request**: 用户决定「建远程并推上去」，并明确「准备完全开源」。
- **Execution & Outcome**:
  1. **认证与仓库状态核查**：`gh` CLI 已认证（`guangkuorsong2007-creator`，scope 含 `repo` + `workflow`，后者为 CI 所需）；本地仓库此前无 remote，分支 `main`，5 次提交，`.git` 体积 1.0 MB。
  2. **公开前专项合规审计**（针对「即将永久公开」这一新状态）：
     - 个人数据模式（手机号 / 身份证 / 学号 / 银行卡）：**0 处**；
     - 真实就读院校 / 真实成绩单 / 真实家庭财务：**0 处**，全部为合成夹具；
     - 真实院校名：2 处，**均在治理文档的反面示例语境**，由 `scan_repo.py` 显式豁免；
     - 凭证 / `.env` / 私钥文件：**0 处**；
     - git 全历史敏感模式扫描：**0 处**；
     - 大文件：无（最大 36 KB）；
     - 操作型文档硬编码绝对路径：**0 处**。
  3. **唯一需用户裁定项**：`docs/规划工作流程复盘与复用草案.md` 含 4 处 Alberta、1 处 Canada，以第三人称方法论口吻描述工作流起源（用户本人规划历程），无可识别信息。已告知「推送后 git 历史固定、事后抹除需重写历史」的不可逆性，用户明确选择**原样推送**。
  4. **`docs/真实官方来源核验报告_三项关键主张.md` 保留**：内容为加拿大 IRCC PGWP 公开政策，用于示范「主张须有官方来源支撑」的审计方法，非个人数据。
  5. **README 新增「开源说明与参与方式」章节**：许可与 MIT 说明、数据合规声明（含「唯一真实世界内容」的边界交代）、5 条贡献建议（含「不得修改冻结基线」）、以及当前成熟度与**「请勿把单次内部试验推广为通用结论」**的声明。
  6. **创建并推送**：`guangkuorsong2007-creator/reusable-study-abroad-planning-workflow`（public），添加 origin，推送 `main`，确认 GitHub Actions 工作流已识别。
- **Files Modified**: `README.md`（新增开源说明章节）、`00_Status.md`、`03_Decisions.md`（新增 WF-D007）、`05_Session_Log.md`。
- **Files NOT Modified**: `docs/规划工作流程复盘与复用草案.md`（按用户决定原样推送）；全部冻结基线与证据链资产。
- **Next**: 待用户执行 v0.3 外部投放；CI 在首次推送后自动运行，可据其结果确认远端环境一致。

---

## 2026-11-04T12:50:56+08:00 · MCode (mavis) · 开源发布与 CI 首跑失败修复 (WF-D007 / WF-D008)

- **Request**: 用户决定「建远程并推上去」，并明确「准备完全开源」。
- **Execution & Outcome**:
  1. **公开前专项合规审计**：个人数据模式 0 处；真实院校/成绩单/财务 0 处；凭证文件 0 处；git 全历史敏感模式 0 处；大文件无；操作型文档硬编码绝对路径 0 处。唯一需裁定项经用户明确选择为**原样推送**（见 WF-D007）。
  2. **创建并推送公开仓库**：`guangkuorsong2007-creator/reusable-study-abroad-planning-workflow`（public），origin 已配置，`main` 已推送。
  3. **拆分数据合规声明**：原 `LICENSE` 在 MIT 正文后追加中文声明导致 GitHub licensee 无法识别（仓库页显示无许可）。已将合规声明独立为 `DATA_COMPLIANCE.md`，`LICENSE` 恢复纯 MIT 正文，README 与 AGENTS.md 改为引用。
  4. **CI 首跑失败 → 根因定位（关键）**：`v0.3 MANIFEST 存在不匹配`，缺失的是全部 4 个 `Run_Template/` 文件。
     - **根因**：`.gitignore` 的 `RUN_*/` 在 macOS 默认 `core.ignorecase=true` 下**大小写不敏感**，误匹配了 `Run_Template/`；
     - **影响**：8 个文件从未被提交——v0.3 的**两份外部投放包**、v0.2 的 Run_Template、**仓库根模板**。公开仓库因此是残缺的；
     - **为何本地全绿**：本地工作区确有这些文件，工具读取的是真实文件；只有**远端 CI 的干净检出**才暴露缺失。
  5. **修复**：`.gitignore` 改为精确前缀 `RUN_SYN*/` 并显式反忽略 `!**/Run_Template/`；补提交 8 个遗漏文件。
  6. **新增守护**：`scan_repo.py` 增加「必需文件入库检查」——19 个必须随仓库发布的文件逐一校验存在性 + git 跟踪状态，并泛化报告「被 `.gitignore` 意外忽略」的文档/代码文件。守护有效性已实测（还原错误规则后正确报错并退出码 1）。
- **Files Created**: `DATA_COMPLIANCE.md`。
- **Files Modified**: `.gitignore`、`tools/scan_repo.py`（新增入库守护）、`README.md`、`AGENTS.md`、`LICENSE`、`03_Decisions.md`（新增 WF-D007 / WF-D008）、`05_Session_Log.md`、`00_Status.md`。
- **Files Added to git（此前被误忽略）**: `simulations/规划流程模拟包_v0.2/Run_Template/` ×2、`simulations/规划流程模拟包_v0.3/Run_Template/` ×4、`templates/Run_Template/` ×2。
- **Next**: 推送修复并确认 CI 转绿；随后待用户执行 v0.3 外部投放。
