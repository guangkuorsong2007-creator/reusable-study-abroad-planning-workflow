# Reusable Workflow Governance / 工作流项目治理规约

Canonical directory: 本仓库根目录（本机当前副本为 `/Users/songguangkuo/Documents/可复用留学规划流程`；仓库被克隆或移动后以实际所在目录为准）。
Applies to every agent working on the Reusable Study Abroad Planning Workflow product repository.

---

## 核心红线与行为准则

### 1. 绝对隐私隔离与数据脱敏 (Zero Real Data Red Line)
- **严禁引入任何真实个人数据**：绝不允许在测试、代码、模板或方案中引入任何真实申请人的姓名、学号、真实就读院校（如天津师范大学等）、真实成绩单或真实家庭财务数据；
- **全量采用合成夹具**：所有案例测试必须使用脱敏或完全虚构的规则与画像（例如：SYN-UG-101/102、虚构国别“松岚国/澄湾国/兰泽国/沧澜国”）；
- **产品化与可共享标准**：本仓库所有文件必须具备随时公开、分发给第三方顾问或开源评测的合规性。

### 2. 状态文件精简与解耦规约 (Decoupled State Standard)
- **运行实例四文件规范命名**：`CASE.md`（当前事实与决策基线）、`EVIDENCE.md`（来源与局限索引）、`CHECKPOINT.md`（极简导航锚点）、`CHANGELOG.md`（审计轨迹）；
- **`CHECKPOINT.md` 体积硬限制**：严格控制在 **4,000 字节** 以内，禁止递归堆叠历史对话全文；
- **四文件职责单一**：
  - `CASE.md` 仅沉淀学生背景、课程实绩、原始约束、方案矩阵与已接受决定；
  - `EVIDENCE.md` 仅登记来源 ID、支撑范围、局限与模拟日期；
  - `CHECKPOINT.md` 仅包含当前运行阶段、核心锚点数字、未决断点与下一步指令；
  - `CHANGELOG.md` 仅记录分轮会话收发摘要与修改追踪；
- **单一事实源**：同一事实以 `CASE.md` 为当前值，其余三份文件只做引用，不做平行叙述；
- **命名历史**：`simulations/` 下 v0.1–v0.3 冻结基线保留其原始文件名与哈希记录，不做追溯性重命名；新建实例一律使用上述规范命名。详见 `01_Framework.md` 第二节的概念层→规范层映射表。

### 3. 评测证据链严密性 (Evaluation Rigour)
- **客观指标判定**：评测 Agent 或复核脚本必须依据落盘文件、真实执行转录 (`transcript.json`) 及阶段快照 (`首次比较后/`, `更新后/`) 判定得分，严禁依据模型自我宣称推断通过；
- **基线回归门**：运行 `simulations/规划流程模拟包_v0.2/run_autorun03.py` 必须确保 15/15 评测项通过率达标。

---

## Agent 每轮工作规约

### 进入每轮交互时：
1. 实际读取本目录下的 `00_Status.md`，了解当前开发与评测进展；
2. 查阅 `02_Roadmap.md` 与 `03_Decisions.md` 的最新条目；
3. 从记录的未决事项继续工作，避免重复已完成的优化（如 v0.2 的模板解耦、AutoRun03 基准建立已全面完成）。

### 完成每轮交互退出前：
1. 更新 `00_Status.md`（记录本轮实质进展、未决问题与下一步动作）；
2. 若有架构或规则变更，追加至 `03_Decisions.md`（命名空间使用 `WF-D001+`）；
3. 在 `05_Session_Log.md` 追加一条包含精确时间戳 (`TZ=Asia/Shanghai date`)、操作人、修改文件与下一步简报的日志。
