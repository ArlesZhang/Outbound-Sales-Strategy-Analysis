"""
Telemarketing Analysis Utilities

供 notebooks/01–05 复用的共享工具函数：

- find_project_root(): 定位项目根目录（兼容从项目根或 notebooks/ 目录启动内核）
- setup_plot_style(): 统一图表样式（中文字体；交互式环境用 inline 后端，批量执行用 Agg）
- build_design_matrix(): OneHot + 标准化 → 设计矩阵（倾向得分模型/评分模型共用）
- estimate_propensity_score(): 逻辑回归拟合倾向得分，返回带 pscore/logit_ps 的 DataFrame
- nearest_neighbor_match(): 1:1 贪心最近邻匹配（无放回、caliper 限制、logit 距离）
- check_balance(): SMD 平衡性检验（匹配前后对比，数值变量与类别变量每个水平）
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# 数据文件相对项目根的路径，用作项目根定位锚点
_DATA_ANCHOR = Path("data") / "raw" / "bank-additional-full.csv"


def find_project_root(start: Path | None = None) -> Path:
    """从当前工作目录向上探测项目根目录（以 data/raw/bank-additional-full.csv 为锚点）。"""
    cand = Path.cwd() if start is None else Path(start)
    for base in (cand, cand.parent):
        if (base / _DATA_ANCHOR).exists():
            return base
    raise FileNotFoundError(
        "未找到项目根目录：请确认 data/raw/bank-additional-full.csv 存在，"
        "且内核工作目录为项目根或 notebooks/ 目录"
    )


def setup_plot_style() -> None:
    """统一图表样式：中文 Noto Sans CJK SC 字体、负数正常显示、坐标轴刻度抑制。

    交互式环境（Jupyter Lab）尝试切到 inline 后端；批量执行（nbconvert）使用 Agg。
    必须在 import matplotlib.pyplot 之前调用。
    """
    try:
        get_ipython().run_line_magic("matplotlib", "inline")  # type: ignore[name-defined]  # noqa: F821
    except Exception:
        matplotlib.use("Agg")
    matplotlib.rcParams["font.sans-serif"] = [
        "Noto Sans CJK SC",
        "Droid Sans Fallback",
        "DejaVu Sans",
    ]
    matplotlib.rcParams["axes.unicode_minus"] = False
    matplotlib.rcParams["figure.dpi"] = 110
    matplotlib.rcParams["savefig.bbox"] = "tight"


# ---------------------------------------------------------------------------
# PSM 工具函数（notebook 04 用；设计与假设说明见 docs/00_methodology_notes.md）
# ---------------------------------------------------------------------------

def build_design_matrix(
    df: pd.DataFrame, numeric_cols: list[str], categorical_cols: list[str]
) -> tuple[np.ndarray, list[str]]:
    """OneHot 编码类别列（drop='first'，unknown 保留为独立水平）+ 标准化数值列。

    返回 (设计矩阵, 特征名列表)；特征名与 OneHotEncoder 的列一一对应。
    """
    encoder = OneHotEncoder(drop="first", handle_unknown="error").fit(df[categorical_cols])
    cat = encoder.transform(df[categorical_cols]).toarray()
    scaler = StandardScaler().fit(df[numeric_cols])
    num = scaler.transform(df[numeric_cols])
    X = np.hstack([cat, num])
    names = encoder.get_feature_names_out().tolist() + list(numeric_cols)
    return X, names


def estimate_propensity_score(
    df: pd.DataFrame,
    treatment_col: str,
    numeric_cols: list[str],
    categorical_cols: list[str],
    random_state: int = 42,
) -> tuple[pd.DataFrame, LogisticRegression, np.ndarray, list[str]]:
    """用逻辑回归估计倾向得分（处理组 = 1）。

    返回 (df 加 pscore/logit_ps 两列, 拟合模型, 设计矩阵, 特征名)。
    """
    X, names = build_design_matrix(df, numeric_cols, categorical_cols)
    y = (df[treatment_col] == 1).astype(int).values
    model = LogisticRegression(max_iter=2000, random_state=random_state).fit(X, y)
    ps = model.predict_proba(X)[:, 1]
    logit_ps = np.log(ps / (1 - ps))
    out = df.copy()
    out["pscore"] = ps
    out["logit_ps"] = logit_ps
    return out, model, X, names


def nearest_neighbor_match(
    df: pd.DataFrame,
    treatment_col: str,
    logit_col: str = "logit_ps",
    caliper: float | None = None,
) -> tuple[pd.DataFrame, dict]:
    """1:1 贪心最近邻匹配（无放回、caliper 限制、logit 倾向得分距离）。

    处理组按 logit_ps 降序处理（倾向最高者先匹配，标准口径）；
    每个处理组在"尚未被使用"的对照组中找 logit 距离最近的个体；
    距离超过 caliper 则该处理组不匹配（丢弃）。

    返回 (matched_df, meta)，meta 含：
      caliper / matched_pairs / treated / control / 匹配成功率 / 每对距离统计。
    """
    treated_df = df[df[treatment_col] == 1].sort_values(logit_col, ascending=False)
    control_df = df[df[treatment_col] == 0].sort_values(logit_col).reset_index(drop=True)

    if caliper is None:  # 默认：logit 尺度 0.2 倍标准差（Rubin 建议口径）
        caliper = 0.2 * df[logit_col].std()

    control_logits = control_df[logit_col].values
    used = np.zeros(len(control_df), dtype=bool)

    match_row_control = np.full(len(treated_df), -1, dtype=int)
    dists = np.full(len(treated_df), np.inf)

    for i, t_logit in enumerate(treated_df[logit_col].values):
        avail = ~used
        if not avail.any():
            break
        # 在可用对照组上做 1NN 查询（1-D 数据用 numpy；约束是唯一分配逻辑）
        d = np.abs(control_logits - t_logit)
        d[~avail] = np.inf
        j = int(np.argmin(d))
        if d[j] <= caliper:
            used[j] = True
            match_row_control[i] = j
            dists[i] = d[j]

    matched_mask = match_row_control >= 0
    matched_rows = treated_df.reset_index(drop=True)[matched_mask]
    control_rows = control_df.iloc[match_row_control[matched_mask]].reset_index(drop=True)
    # 纵排合并成"配对小表"：每行是一匹配对——处理组列保持原名，对照组列加 _c 后缀。
    # 行内同时携带 {y, age, ...}（处理组观测）与 {y_c, age_c, ...}（对照组观测）。
    control_rows = control_rows.add_suffix("_c")
    matched = pd.concat([matched_rows.reset_index(drop=True), control_rows], axis=1)

    meta = {
        "caliper": float(caliper),
        "matched_pairs": int(matched_mask.sum()),
        "treated": int(len(treated_df)),
        "control": int(len(control_df)),
        "match_rate": float(matched_mask.mean()),
        "max_pair_dist": float(dists[matched_mask].max()),
        "mean_pair_dist": float(dists[matched_mask].mean()),
    }
    return matched, meta


def _smd_numeric(s_t: pd.Series, s_c: pd.Series) -> float:
    """数值变量标准化均差：|均值差| / sqrt((var_t + var_c) / 2)。"""
    vt, vc = s_t.var(ddof=1), s_c.var(ddof=1)
    if vt + vc == 0:
        return 0.0
    return abs(s_t.mean() - s_c.mean()) / np.sqrt((vt + vc) / 2)


def _smd_binary(p_t: float, p_c: float) -> float:
    """二值变量（水平占比）标准化均差。"""
    denom = np.sqrt((p_t * (1 - p_t) + p_c * (1 - p_c)) / 2)
    if denom == 0:
        return 0.0
    return abs(p_t - p_c) / denom


def check_balance(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    treatment_col: str,
    numeric_cols: list[str],
    categorical_cols: list[str],
    threshold: float = 0.10,
) -> pd.DataFrame:
    """SMD 平衡性检验：匹配前 vs 匹配后，逐特征（类别变量按每个水平）对比。

    约定：SMD<threshold(默认0.1) 视为平衡。返回 DataFrame（含是否失衡标记）。
    """
    def _phase_rows(data: pd.DataFrame) -> dict[str, float]:
        t = data[data[treatment_col] == 1]
        c = data[data[treatment_col] == 0]
        out: dict[str, float] = {}
        for col in numeric_cols:
            out[f"{col}(数值)"] = _smd_numeric(t[col], c[col])
        for col in categorical_cols:
            for level in sorted(data[col].astype(str).unique()):
                p_t = (t[col].astype(str) == level).mean()
                p_c = (c[col].astype(str) == level).mean()
                out[f"{col}_{level}"] = _smd_binary(p_t, p_c)
        return out

    before_rows = _phase_rows(df_before)
    after_rows = _phase_rows(df_after)
    out = pd.DataFrame({
        "匹配前SMD": pd.Series(before_rows),
        "匹配后SMD": pd.Series(after_rows),
    })
    out["是否失衡(>0.1)"] = np.where(out["匹配后SMD"] > threshold, "失衡", "平衡")
    return out.round(4)
