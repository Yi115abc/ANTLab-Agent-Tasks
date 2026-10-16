# ANTLab Agent Tasks

文档阅读与信息核验方向 Agent 项目的应用层开发者招募考核：先完成基础题，再从进阶 A/B/C 中选择一套完成。

**截止时间：北京时间 2026 年 10 月 16 日 23:59（UTC+8）。**

## 从哪开始

1. 先读 [开始阅读.md](开始阅读.md)（总体规则、时间、提交方式）。
2. 基础题（必做）：[基础/README.md](基础/README.md) 与 基础/01_考核题目.md。
3. 进阶题（三选一）：[进阶/README.md](进阶/README.md)，在 A / B / C 中选一套。

## 目录结构

```text
开始阅读.md              入口：总体规则、截止时间、提交方式
基础/                    基础题：12 题（4 开发题有公开答案 + 8 评测题），
                         R0/R1/R2/K 四种输入组织条件；模型 API 自费，
                         主请求量与运行命令见 基础/README.md
进阶/                    进阶题（A/B/C 三选一）
├─ 01_A_研究机制迁移.md        A：主张→证据→支持状态机制迁移与对照
├─ 02_B_系统失效诊断.md        B：源码审查、故障归因与修复
├─ 03_C_产品假设验证.md        C：围绕自选用户任务的产品假设验证
├─ materials/                 两份 CC Attribution 公开论文（P1/P2）及抽取数据
├─ challenge_b/               B 题文档查证样机（30 行 Engine，含预埋故障）
└─ templates/                 声明与整合报告模板
```

## 规则要点

- 准备时间为一周（包含基础题和进阶题）；模型调用使用自己的 API，费用自理；实验输入、原始响应、失败和前后对照须保留在仓库中。
- AI 可辅助阅读、实现和排错；需记录它对关键决定的影响、本人如何核验，以及实际完成和未完成的内容。
- 提交：把作品推送到自己的 GitHub 仓库，并在收集表登记仓库链接与最终 commit SHA；收集表地址与仓库评审账号见 Q 群公布（详见 进阶/05_提交与报告格式.md 与 进阶/06_收集表填写说明.md）。
- 本包不含评委参考答案、评测标签、内部开发教程或商业书籍全文。
- 文件完整性：`基础/文件校验.json` 与 `进阶/文件校验.json` 提供逐文件 SHA256，可自行校验。

---

## 参赛者提交信息

- 所选方向：Agent（文档阅读与信息核验）；进阶题选 B（系统失效诊断）
- 最终分支：main
- 最终 commit SHA：eb054d2（进阶题 B 成果快照）；基础题快照 e4ec28c
- 完成情况：基础题全部完成——D01–D04 通过；正式题 40 次主请求（32 基线 + 8 改进，R0 改进后 7/8）；进阶题 B 完成——定位并修复 R02 缓存污染（换快照返回旧结论），回归/变体/边界通过，详见进阶报告

### 运行入口

进入 `基础` 目录执行：

```text
python starter/runner.py --case D01 --condition E --dry-run --config config.local.json   # 试跑（不花钱）
python starter/runner.py --case D01 --condition E --paid --config config.local.json       # 真实调用
```

`config.local.json` 由 `config.example.json` 复制后填写个人 API 信息，含密钥不入库（.gitignore 已排除）。

### 提交物清单

| 路径 | 说明 |
|---|---|
| 基础/starter/student.py | 答卷实现：prepare_messages（统一提示词）+ improve（v6 冻结版：规则前置 + 类型自适应） |
| 基础/versions/ | 改进版本备份：student_baseline_v1 + student_improved_v1~v6 |
| 基础/results/results.csv | 逐例结果表（142 条：40 次主请求 + 探索轮，失败与重试独立成行） |
| 基础/results/scoring/ | 判分与核验脚本（check_baseline / inspect_run / compare_improved / verify_r0 / show_cond） |
| 基础/reports/ | 基础题实验报告 + 决策记录与 AI 申报 |

### 进阶题 B 提交物清单

| 路径 | 说明 |
|---|---|
| 进阶/challenge_b/my_engine.py | 修复版 Engine（缓存键含 doc_ids/snapshot/k），原 challenge.py 未动 |
| 进阶/challenge_b/run_variants.py | 等价变体（版本切换/标识重映射/词序）与自构造边界运行脚本 |
| 进阶/challenge_b/runs/ | baseline.json（原样机基线）、fixed.json（修复后）、variants.json（变体+边界） |
| 进阶/challenge_b/compare.html | 修复前后行为对比页面（区分已核验/未核验） |
| 桌面《ANTLab考核-进阶题B实验报告.docx》 | 故障记录、两候选原因与预测、最小修复、回归/变体/边界、决策记录与 AI 申报 |
