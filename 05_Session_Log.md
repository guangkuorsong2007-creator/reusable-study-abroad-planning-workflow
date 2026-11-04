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
