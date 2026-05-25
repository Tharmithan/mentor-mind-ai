#!/usr/bin/env python3
"""
Day 3 — Exploratory Data Analysis + AI Insights Report.

Generates recruiter-ready charts (matplotlib, seaborn, plotly) and
auto-written insights from cleaned student performance data.

Usage:
  python datasets/scripts/eda_analysis.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = REPO_ROOT / "datasets"
PROCESSED = ROOT / "processed"
EDA_DIR = PROCESSED / "eda"
CLEANED_CSV = PROCESSED / "student_performance_cleaned.csv"
INSIGHTS_JSON = EDA_DIR / "ai_insights_report.json"
INSIGHTS_MD = EDA_DIR / "ai_insights_report.md"

# wellness_score 1–5 used as sleep/wellness proxy (UCI has no sleep column)
SLEEP_PROXY_COL = "wellness_score"
SLEEP_LOW_THRESHOLD = 2
SLEEP_HIGH_THRESHOLD = 4

COURSE_LABELS = {0: "Mathematics", 1: "Portuguese"}


def load_cleaned() -> pd.DataFrame:
    if not CLEANED_CSV.exists():
        raise FileNotFoundError(
            f"{CLEANED_CSV} not found. Run: python datasets/scripts/clean_data.py"
        )
    df = pd.read_csv(CLEANED_CSV)
    df["subject"] = df["course"].map(COURSE_LABELS)
    return df


def pct_diff(low_mean: float, high_mean: float) -> float:
    if high_mean == 0:
        return 0.0
    return round((high_mean - low_mean) / high_mean * 100, 1)


def generate_insights(df: pd.DataFrame) -> list[dict]:
    """Auto-generate AI-style insights from data patterns."""
    insights: list[dict] = []

    # 1. Study hours vs performance
    low_study = df[df["study_hours"] <= df["study_hours"].quantile(0.25)]
    high_study = df[df["study_hours"] >= df["study_hours"].quantile(0.75)]
    diff = pct_diff(low_study["performance_pct"].mean(), high_study["performance_pct"].mean())
    insights.append(
        {
            "category": "study_habits",
            "insight": (
                f"Students in the bottom 25% for study hours score {abs(diff)}% "
                f"{'lower' if diff > 0 else 'higher'} than top-quartile studiers."
            ),
            "metric": "study_hours vs performance_pct",
            "impact_pct": abs(diff),
        }
    )

    # 2. Attendance vs performance
    low_att = df[df["attendance_pct"] < 90]
    high_att = df[df["attendance_pct"] >= 95]
    if len(low_att) and len(high_att):
        diff = pct_diff(low_att["performance_pct"].mean(), high_att["performance_pct"].mean())
        insights.append(
            {
                "category": "attendance",
                "insight": (
                    f"Students with attendance below 90% perform {abs(diff)}% worse "
                    f"than those above 95% attendance."
                ),
                "metric": "attendance_pct vs performance_pct",
                "impact_pct": abs(diff),
            }
        )

    # 3. Sleep/wellness proxy vs grades
    low_well = df[df[SLEEP_PROXY_COL] <= SLEEP_LOW_THRESHOLD]
    high_well = df[df[SLEEP_PROXY_COL] >= SLEEP_HIGH_THRESHOLD]
    if len(low_well) and len(high_well):
        diff = pct_diff(low_well["performance_pct"].mean(), high_well["performance_pct"].mean())
        insights.append(
            {
                "category": "wellness_sleep_proxy",
                "insight": (
                    f"Students with low wellness scores (≤{SLEEP_LOW_THRESHOLD}, sleep proxy) "
                    f"perform {abs(diff)}% worse than high-wellness peers (≥{SLEEP_HIGH_THRESHOLD})."
                ),
                "metric": f"{SLEEP_PROXY_COL} vs performance_pct",
                "impact_pct": abs(diff),
                "note": "UCI dataset uses health score 1–5 as wellness/sleep proxy.",
            }
        )

    # 4. Subject weaknesses
    by_subject = df.groupby("subject")["performance_pct"].agg(["mean", "count"]).reset_index()
    weakest = by_subject.loc[by_subject["mean"].idxmin()]
    strongest = by_subject.loc[by_subject["mean"].idxmax()]
    gap = round(strongest["mean"] - weakest["mean"], 1)
    insights.append(
        {
            "category": "subject_weakness",
            "insight": (
                f"{weakest['subject']} is the weakest subject "
                f"(avg {weakest['mean']:.1f}%), {gap:.1f} points below {strongest['subject']}."
            ),
            "metric": "performance_pct by course",
            "weakest_subject": weakest["subject"],
            "strongest_subject": strongest["subject"],
        }
    )

    # 5. At-risk rate
    risk_rate = df["at_risk"].mean() * 100
    insights.append(
        {
            "category": "risk",
            "insight": (
                f"{risk_rate:.0f}% of students are at-risk (performance below 60%). "
                "Prioritize revision on weak subjects and attendance coaching."
            ),
            "metric": "at_risk rate",
            "impact_pct": round(risk_rate, 1),
        }
    )

    # 6. Top correlation driver
    numeric = df[
        [
            "study_hours",
            "attendance_pct",
            SLEEP_PROXY_COL,
            "past_failures",
            "performance_pct",
        ]
    ]
    corr = numeric.corr()["performance_pct"].drop("performance_pct").abs().sort_values(ascending=False)
    top_feat = corr.index[0]
    insights.append(
        {
            "category": "correlation",
            "insight": (
                f"Strongest predictor of performance is `{top_feat}` "
                f"(|r| = {corr.iloc[0]:.2f})."
            ),
            "metric": "correlation matrix",
            "top_feature": top_feat,
        }
    )

    return insights


def plot_study_hours_vs_marks(df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.regplot(
        data=df,
        x="study_hours",
        y="performance_pct",
        scatter_kws={"alpha": 0.35, "s": 25, "color": "#8b5cf6"},
        line_kws={"color": "#3b82f6", "linewidth": 2},
        ax=ax,
    )
    ax.set_xlabel("Study Hours (weekly proxy)")
    ax.set_ylabel("Performance (%)")
    ax.set_title("Study Hours vs Marks")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_attendance_vs_performance(df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.scatterplot(
        data=df,
        x="attendance_pct",
        y="performance_pct",
        hue="at_risk",
        palette={0: "#22d3ee", 1: "#f43f5e"},
        alpha=0.5,
        ax=ax,
    )
    z = np.polyfit(df["attendance_pct"], df["performance_pct"], 1)
    p = np.poly1d(z)
    xs = np.linspace(df["attendance_pct"].min(), df["attendance_pct"].max(), 50)
    ax.plot(xs, p(xs), color="#f59e0b", linewidth=2, label="Trend")
    ax.set_xlabel("Attendance (%)")
    ax.set_ylabel("Performance (%)")
    ax.set_title("Attendance vs Performance")
    ax.legend(title="At risk")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_sleep_proxy_vs_grades(df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    order = sorted(df[SLEEP_PROXY_COL].unique())
    sns.boxplot(
        data=df,
        x=SLEEP_PROXY_COL,
        y="performance_pct",
        hue=SLEEP_PROXY_COL,
        order=order,
        palette="Purples",
        legend=False,
        ax=ax,
    )
    sns.stripplot(
        data=df.sample(min(200, len(df)), random_state=42),
        x=SLEEP_PROXY_COL,
        y="performance_pct",
        color="#3b82f6",
        alpha=0.25,
        size=3,
        ax=ax,
    )
    ax.set_xlabel("Wellness / Sleep Proxy Score (1=low … 5=high)")
    ax.set_ylabel("Performance (%)")
    ax.set_title("Wellness (Sleep Proxy) vs Grades")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_subject_weaknesses(df: pd.DataFrame, out: Path) -> None:
    by_sub = (
        df.groupby("subject")
        .agg(avg_performance=("performance_pct", "mean"), at_risk_rate=("at_risk", "mean"))
        .reset_index()
    )
    fig, ax1 = plt.subplots(figsize=(8, 6))
    colors = ["#f43f5e" if r > 0.5 else "#8b5cf6" for r in by_sub["at_risk_rate"]]
    bars = ax1.bar(by_sub["subject"], by_sub["avg_performance"], color=colors, edgecolor="white")
    ax1.set_ylabel("Average Performance (%)")
    ax1.set_title("Subject Weaknesses — Avg Performance by Course")
    ax1.set_ylim(0, 100)
    for bar, val in zip(bars, by_sub["avg_performance"]):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{val:.1f}%", ha="center", fontsize=11)
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_correlation_heatmap(df: pd.DataFrame, out: Path) -> None:
    cols = [
        "study_hours",
        "attendance_pct",
        SLEEP_PROXY_COL,
        "past_failures",
        "absences",
        "grade_period_1",
        "grade_period_2",
        "performance_pct",
    ]
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(df[cols].corr(), annot=True, fmt=".2f", cmap="RdYlGn", center=0, ax=ax)
    ax.set_title("Feature Correlation Matrix")
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)


def plot_distribution(df: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    sns.histplot(df["performance_pct"], kde=True, color="#8b5cf6", ax=axes[0])
    axes[0].axvline(60, color="#f43f5e", linestyle="--", label="At-risk (60%)")
    axes[0].set_title("Performance Distribution")
    axes[0].legend()

    sns.histplot(df["study_hours"], kde=True, color="#3b82f6", ax=axes[1])
    axes[1].set_title("Study Hours Distribution")

    sns.histplot(df["attendance_pct"], kde=True, color="#22d3ee", ax=axes[2])
    axes[2].set_title("Attendance Distribution")
    fig.suptitle("Distributions — Week 3 EDA", y=1.02)
    fig.tight_layout()
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_plotly_dashboard(df: pd.DataFrame, out: Path) -> None:
    if not HAS_PLOTLY:
        return
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Study Hours vs Marks",
            "Attendance vs Performance",
            "Wellness vs Grades",
            "Subject Performance",
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=df["study_hours"],
            y=df["performance_pct"],
            mode="markers",
            marker=dict(color="#8b5cf6", opacity=0.5),
            name="Students",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df["attendance_pct"],
            y=df["performance_pct"],
            mode="markers",
            marker=dict(color=df["at_risk"], colorscale=["#22d3ee", "#f43f5e"], opacity=0.5),
            name="Attendance",
        ),
        row=1,
        col=2,
    )
    for score in sorted(df[SLEEP_PROXY_COL].unique()):
        sub = df[df[SLEEP_PROXY_COL] == score]
        fig.add_trace(
            go.Box(y=sub["performance_pct"], name=f"Wellness {score}", marker_color="#a78bfa"),
            row=2,
            col=1,
        )
    by_sub = df.groupby("subject")["performance_pct"].mean().reset_index()
    fig.add_trace(
        go.Bar(x=by_sub["subject"], y=by_sub["performance_pct"], marker_color="#3b82f6"),
        row=2,
        col=2,
    )
    fig.update_layout(
        title="MentorMind AI — EDA Dashboard",
        template="plotly_dark",
        height=700,
        showlegend=False,
    )
    fig.write_html(str(out))


def write_insights_report(insights: list[dict], df: pd.DataFrame) -> None:
    report = {
        "title": "MentorMind AI — Insights Report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_rows": len(df),
        "insights": insights,
    }
    INSIGHTS_JSON.write_text(json.dumps(report, indent=2))

    lines = [
        "# MentorMind AI — Insights Report",
        "",
        f"*Generated: {report['generated_at']}* · *{len(df)} students analyzed*",
        "",
        "---",
        "",
        "## Key findings",
        "",
    ]
    for i, item in enumerate(insights, 1):
        lines.append(f"{i}. **{item['category'].replace('_', ' ').title()}** — {item['insight']}")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Charts",
            "",
            "| Chart | File |",
            "|-------|------|",
            "| Study hours vs marks | `01_study_hours_vs_marks.png` |",
            "| Attendance vs performance | `02_attendance_vs_performance.png` |",
            "| Wellness/sleep proxy vs grades | `03_wellness_sleep_vs_grades.png` |",
            "| Subject weaknesses | `04_subject_weaknesses.png` |",
            "| Correlation heatmap | `05_correlation_heatmap.png` |",
            "| Distributions | `06_distributions.png` |",
            "| Interactive dashboard | `07_eda_dashboard.html` |",
            "",
            "> Wellness score (1–5) is used as a **sleep proxy** — the UCI dataset does not include sleep hours directly.",
            "",
        ]
    )
    INSIGHTS_MD.write_text("\n".join(lines))


def run_eda() -> dict:
    print("=== Day 3: Exploratory Data Analysis ===\n")
    EDA_DIR.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid", palette="muted")
    df = load_cleaned()
    print(f"Loaded {len(df)} rows from cleaned data\n")

    plots = {
        "01_study_hours_vs_marks.png": plot_study_hours_vs_marks,
        "02_attendance_vs_performance.png": plot_attendance_vs_performance,
        "03_wellness_sleep_vs_grades.png": plot_sleep_proxy_vs_grades,
        "04_subject_weaknesses.png": plot_subject_weaknesses,
        "05_correlation_heatmap.png": plot_correlation_heatmap,
        "06_distributions.png": plot_distribution,
    }

    for name, fn in plots.items():
        fn(df, EDA_DIR / name)
        print(f"[OK] {EDA_DIR / name}")

    if HAS_PLOTLY:
        plot_plotly_dashboard(df, EDA_DIR / "07_eda_dashboard.html")
        print(f"[OK] {EDA_DIR / '07_eda_dashboard.html'}")
    else:
        print("[SKIP] plotly not installed — pip install plotly")

    insights = generate_insights(df)
    write_insights_report(insights, df)
    print(f"[OK] {INSIGHTS_MD}")
    print(f"[OK] {INSIGHTS_JSON}")

    print("\n--- AI Insights (preview) ---")
    for item in insights[:4]:
        print(f"  • {item['insight']}")

    return {"plots": len(plots), "insights": len(insights), "output_dir": str(EDA_DIR)}


def main() -> int:
    try:
        run_eda()
        return 0
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
