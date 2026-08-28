# CLAUDE.md — 外呼销售策略分析：UCI Bank Marketing（项目三）

## 项目定位

面向**策略运营数据分析师**能力建设的实战型作品集项目，作品集第三个。

- **项目一**（`ecommerce-funnel-behavior-analysis`）：描述性分析——"发生了什么、为什么、怎么办"。
- **项目二**（`Mobile_Games_AB_Testing-Cookie_Cats`）：有随机实验条件下的因果推断——"这个改动有没有效"。
- **项目三（本项目）**：**没有随机实验条件下的因果推断**——"没有AB测试，我依然能多大程度上把相关性逼近因果性"。

真实动机不是"练一个PSM算法"，而是承接3年货拉拉销售质检工作里反复遇到、却从没有工具正式回答过的问题：规则/话术调整后效果变化，是调整本身的功劳，还是客群/时段自然变化的假象？这类调整几乎从不走AB测试，只有历史观察数据——UCI Bank Marketing数据集的外呼渠道/次数同样是非随机分配的，结构上复刻了这个真实困境。

> 完整链路：方法论声明 → 数据质量+用户旅程+生命周期分层 → 驱动因素分析 → 客户分层评分 → PSM策略验证（核心） → 节奏描述性分析 → 整合输出（含迁移回货拉拉场景的叙事）

本项目训练的核心是**观察性数据下的因果推断**：知道什么时候能用PSM逼近因果、什么时候连PSM都不该用（如campaign次数的反向因果问题），并诚实地讲清楚方法的边界，而不是"拿到锤子看什么都是钉子"。

## 核心目标

1. **业务目标**：回答"把外呼渠道统一改为手机联系，是否真的因果性提升了转化率，还是客群差异造成的假象"，产出经PSM验证过的效应估计和业务建议。
2. **能力目标**：
   - 用户旅程/生命周期分层框架搭建（区别于孤立特征堆砌）
   - 倾向得分匹配全流程：估计倾向得分 → 共同支撑域检查 → 最近邻匹配 → 平衡性检验(SMD) → ATT估计 → 敏感性/局限性声明
   - 判断一个观察性变量**能不能**用PSM处理（识别反向因果/confounding by indication，如campaign次数）
   - 把"朴素比较 vs PSM调整后"的差距，转化为"选择偏差有多大"的业务语言
3. **可迁移目标**：这套"没有实验条件下逼近因果"的方法论，可直接迁移回货拉拉真实业务场景——评估未经AB测试就上线的规则/策略调整。这是项目三区别于项目二（有实验条件）的核心价值，也是报告和面试话术里必须显式讲出来的部分，不能只停留在"我在UCI数据集上展示了PSM"。

## 协作与学习模式

沿用作品集统一的**以战养战、AI 辅助执行、人工逆向掌握**模式：

```text
AI 辅助快速跑通 → 理解整体结构 → 逆向拆解核心分析 → 建立知识框架
→ 人工重新 Coding → 改变实现方式 → 举一反三 → 提炼可复用能力 → 迁移到货拉拉真实场景
```

按用户所处阶段切换协作方式：

- **执行/跑通模式**（"帮我实现/跑通这个PSM匹配"）：产出完整可运行代码，必须附上**该方法的假设与适用前提**、为什么在这个变量上适用/不适用（尤其是PSM vs 描述性分析的取舍）、以及至少一种可替换实现思路。
- **逆向/学习模式**（"我自己重写/给我提示/为什么用最近邻匹配而不是其他匹配方式"）：只给思路和检查点，**不给完整答案**；用户写完后对比点评。
- 不确定处于哪种模式时，先问一句再动手。

**因果推断相关附加规则**：本项目核心是PSM，凡是给出"处理效应/ATT"结果，必须同时说明——**混杂变量的选择依据**、**共同支撑域是否满足**、**平衡性检验(SMD)结果**、**未观测混杂的存在与局限**。不允许把PSM调整后的估计直接称为"因果效应"，必须使用"经可观测因素调整后的效应估计"这类措辞。

## 当前状态

> 此节需随项目推进更新，过时时以 notebook 和 git log 的实际内容为准。

骨架已搭好，数据已就位，`docs/`已有部分内容，分析尚未系统跑通：

- `data/raw/bank-additional-full.csv` 已下载。
- `docs/00_methodology_notes.md`、`docs/01_data_quality_and_journey.md`、`docs/interview_prep.md` 已建文件，内容以实际填充为准，不得假设已完成。
- `notebooks/01`–`05` 已创建，内容以实际代码为准。
- `src/telemarketing_utils.py` 是PSM工具函数的正式归属文件。**`src/telemarketing_utils.ipynb` 是遗留的重复文件**（同名notebook不应该和.py模块并存），阶段0启动时应先确认其内容是否已迁移进.py文件，确认后删除，避免两份不同步的实现同时存在。
- `notebooks/05_cadence_descripetive_and_limutations.ipynb` 文件名有拼写错误（`descripetive`应为`descriptive`，`limutations`应为`limitations`），建议尽早重命名，避免之后在README/文档里引用路径时出现不一致。
- `main.py` 是`uv init`默认生成的占位文件，本项目产出物是notebook和报告，不通过main.py运行，可以保留作为空占位或删除，不影响分析流程。

**下一步：阶段0（方法论前置声明），随后进入阶段1（数据质量+用户旅程+生命周期分层）。**

## 常用命令

```bash
# 环境（本项目使用uv原生依赖管理，无requirements.txt）
uv sync

# 启动分析环境
uv run jupyter lab

# 提交前自查（见下方"质量门"）
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/0X_xxx.ipynb

# 新增依赖
uv add <package>

# Git
git add .
git commit -m "阶段X: <一句话内容>, 含<关键方法/发现>"
git push
```

## 项目结构

```
outbound-sales-strategy-analysis/
├── CLAUDE.md
├── README.md                    # 最终写成决策报告风格，含"方法论迁移回货拉拉场景"一节
├── pyproject.toml / uv.lock
├── .venv/                       # gitignore
├── main.py                      # uv init占位文件，不承载分析逻辑
├── data/
│   ├── README.md
│   └── raw/bank-additional-full.csv   # gitignore，只读，禁止修改
├── notebooks/
│   ├── 01_data_quality_and_lifecycle.ipynb
│   ├── 02_driver_analysis.ipynb
│   ├── 03_customer_scoring.ipynb
│   ├── 04_psm_channel_validation.ipynb   # 核心：PSM策略验证
│   └── 05_cadence_descriptive_and_limitations.ipynb  
├── docs/
│   ├── 00_methodology_notes.md   # 数据泄漏/选择偏差/PSM边界/campaign取舍声明
│   ├── 01_data_quality_and_journey.md
│   └── interview_prep.md
├── src/
│   └── telemarketing_utils.py    # PSM工具函数：estimate_propensity_score / nearest_neighbor_match / check_balance
└── reports/                      # 图表产出，待创建
```

## 分析路线与产出物

| 阶段 | Notebook/文档 | 核心业务问题 | 产出要求 |
|---|---|---|---|
| 0 方法论声明 | `docs/00_methodology_notes.md` | 这份数据的陷阱是什么？PSM能用在哪、不能用在哪？ | duration泄漏声明、选择偏差声明、PSM适用边界、为什么campaign不做PSM |
| 1 数据质量+旅程+生命周期 | `01_data_quality_and_lifecycle.ipynb` | 客户带着什么历史信息走到今天？ | 数据质量校验、生命周期分层(5类)、分层转化率对比、再触达窗口描述性发现、局限性声明(无客户唯一ID) |
| 2 驱动因素分析 | `02_driver_analysis.ipynb` | 哪些特征和转化相关？分旅程阶段是否不同？ | 卡方检验+Cramér's V，剔除duration，按`first_time`/`returning`分组呈现 |
| 3 客户分层评分 | `03_customer_scoring.ipynb` | 有限的外呼资源该优先打给谁？ | 剔除duration的分层模型 + Gains Chart |
| 4 PSM策略验证（核心） | `04_psm_channel_validation.ipynb` | 渠道改动是否因果性提升了转化率？ | 朴素比较 + 倾向得分 + 共同支撑域检查 + 最近邻匹配 + SMD平衡性检验 + ATT + 敏感性声明 |
| 5 节奏描述性分析 | `05_cadence_descriptive_and_limitations.ipynb` | 外呼次数和转化的关系？ | 仅描述性呈现，不做因果声称（呼应阶段0的campaign取舍） |
| 6 整合输出 | README + `docs/interview_prep.md` | 该给电销团队什么建议？这套方法怎么用回货拉拉？ | 决策报告风格README、"方法论迁移"一节、五问面试话术 |

## 数据说明

来源：UCI Machine Learning Repository **Bank Marketing**，`data/raw/bank-additional-full.csv`，**直接读取，不得修改**。约41,188条记录（葡萄牙银行电销活动）。

| 字段 | 含义 |
|---|---|
| `age`/`job`/`marital`/`education`等 | 客户人口统计特征，用作PSM混杂变量 |
| `contact` | 联系渠道：`cellular`（手机）/ `telephone`（座机），本项目的处理变量T |
| `campaign` | 本次活动联系次数——**存在反向因果，不做PSM，仅描述性分析** |
| `pdays` | 距上次联系的天数，`999`表示从未联系过 |
| `previous` | 本次活动之前的联系次数 |
| `poutcome` | 上次活动结果：`success`/`failure`/`nonexistent` |
| `duration` | 本次通话时长——**数据泄漏字段，不得用于任何预测/决策用途** |
| `y` | 目标变量：是否办理定存 |

**关键陷阱（分析前必须知道）：**

- **duration数据泄漏**：通话时长是结果不是原因，只有客户表现出兴趣销售才会持续通话。任何"外呼前决策"模型不得使用，仅可用于事后EDA并显式标注"解释用途，非预测/决策用途"。
- **选择偏差（核心）**：`contact`（渠道）和`campaign`（次数）都不是随机分配的，销售人员根据客户特征和现场判断决定。这是本项目引入PSM的根本原因——朴素组间比较无法区分"渠道效果"和"客群本身差异"。
- **campaign的反向因果（confounding by indication）**：打更多电话本身就是"销售判断这个客户有希望"的结果，混杂因素（销售主观判断）不可观测，**不得对campaign做PSM**，只做描述性边际效益分析，这是主动的方法论取舍，不是遗漏。
- **无客户唯一ID**：每行是一次外呼活动记录，不是跨活动追踪同一人。生命周期分层是"用当前活动可观测的历史痕迹字段重建的近似状态"，不是真正的纵向留存追踪，报告中必须显式声明这个边界。
- **类别不平衡**：目标变量`y`正类约11%，注意后续如涉及模型评估指标的选择（不要只看Accuracy）。

## 技术栈

- **uv 原生依赖管理**：`pyproject.toml` + `uv.lock`，无 `requirements.txt`。新增依赖用 `uv add`，同步环境用 `uv sync`。
- **Pandas / NumPy**：数据清洗、分组聚合。
- **SciPy（`scipy.stats`）**：卡方检验、Cramér's V。
- **Scikit-learn**：`LogisticRegression`（倾向得分估计）、`NearestNeighbors`（最近邻匹配）——**仅用于PSM流程本身，不引入完整因果推断工具箱（EconML/CausalML等不在本项目范围）**。
- **Matplotlib / Seaborn**：可视化，含PSM共同支撑域分布图。
- 假设检验与匹配逻辑优先用成熟库实现，**不手写易错的统计/匹配算法**；PSM工具函数统一沉淀在 `src/telemarketing_utils.py`，供notebook复用，不在每个notebook里重复实现。

## 编码与写作规范

- 交流、notebook markdown、业务解读用**中文**；代码、变量名、函数名用**英文**。
- Notebook 结构：业务问题 → 口径与方法假设定义 → 实现 → 结果 → 业务解读 → 决策建议。
- **PSM报告四件套**：混杂变量选择依据、共同支撑域检查结果、平衡性检验(SMD)、ATT估计，缺一不可，并说明未观测混杂的局限。
- **口径显式化**：对哪个变量做PSM、为什么不对另一个变量做（如campaign），分析开头写明。
- 图表：中文标签清晰可读，`bbox_inches='tight'`，存入 `reports/`。
- 分析中主动回答因果推断四问：**这个变量能不能做PSM（有没有反向因果/不可观测的核心混杂）→ 混杂变量选够了吗 → 匹配后平衡了吗 → 效应量多大、边界在哪**。

## 质量门（完成标准）

一个 notebook / 阶段产出物达到以下标准才算完成：

- [ ] `Restart Kernel & Run All` 全程无报错
- [ ] 若涉及PSM，四件套（混杂变量依据/共同支撑域/SMD/ATT）齐全，且明确使用"调整后估计"而非"因果效应"的措辞
- [ ] 所有图表已保存至 `reports/`，标签为中文
- [ ] 该阶段业务问题在 notebook 末尾有一段明确的中文业务解读
- [ ] 涉及campaign等不适合PSM的变量时，已显式说明为什么不做、只做描述性分析
- [ ] 涉及生命周期分层/旅程重建时，已声明"无客户唯一ID"的局限

## Git 与仓库礼仪

- Commit message 格式：`阶段X: <一句话内容>, 含<关键方法/发现>`，中文。
- 每个阶段（notebook 01–05、docs、README）至少一次独立 commit，不攒到最后一次性提交。
- 不提交 `data/raw/`、`.venv/`；改动前确认未被误加。
- `src/telemarketing_utils.ipynb`（遗留重复文件）确认内容已迁移后应删除，删除本身作为一次独立的清理性commit，说明原因。
- 直接在 `main` 分支开发，不需要 PR 流程。

## Agent 权限边界

- ✅ 可自主：读写 `notebooks/`、`docs/`、`reports/`、`src/telemarketing_utils.py` 下的文件；运行/调试代码；本地执行 `uv run jupyter nbconvert` 校验。
- ⚠️ 需先确认：新增第三方依赖（`uv add` 前告知用户）；修改 `CLAUDE.md` 本身；删除 `src/telemarketing_utils.ipynb` 等清理性操作（先确认内容已迁移）；重命名 `05_cadence_descripetive_and_limutations.ipynb`（涉及文件引用，需一并检查其他文件是否引用了旧文件名）；`git commit`（可准备好commit message，push前需用户确认）。
- ❌ 不自主执行：`git push`；修改或删除 `data/raw/` 下任何文件；对 `campaign` 等已声明不适合PSM的变量强行套用PSM方法（除非用户明确要求作为反例演示"为什么不该这样做"）。

## 禁止事项 / 边界

- ❌ 把PSM调整后的估计效应直接称为"因果效应"，必须使用"经可观测因素调整后的效应估计"。
- ❌ 对 `campaign`（存在反向因果/confounding by indication）做PSM并当作确证性结论。
- ❌ 跳过共同支撑域检查和平衡性检验(SMD)直接报告ATT数字。
- ❌ 把"生命周期分层"包装成真正的纵向留存追踪（数据集无客户唯一ID）。
- ❌ 堆砌完整因果推断工具箱（RDD/IV/合成控制法/CausalML/EconML等）——本项目目标是把PSM这一个方法做扎实、讲清楚边界，不是展示工具箱广度。
- ❌ 输出没有业务解读的裸数字/裸效应量/裸图表。
- ❌ 编造或猜测数字，一切以真实计算为准。
- ❌ 报告或interview_prep中完全不提这套方法论如何迁移回货拉拉真实业务场景——这是项目三区别于"随便找数据集练手"的核心价值，不能省略。
