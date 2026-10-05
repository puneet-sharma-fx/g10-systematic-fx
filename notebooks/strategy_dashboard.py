"""
Strategy dashboard — single-PNG summary of every strategy in the repo.

Groups every strategy by asset class and status, produces a horizontal
bar chart of net Sharpes with color-coded status legend. Companion visual
to STRATEGIES.md.

Regenerate: python notebooks/strategy_dashboard.py
Output    : reports/strategy_dashboard.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REPORTS = REPO / "reports"

# ── Strategy scoreboard ──────────────────────────────────────────────────────
# Fields: (#, short label, group, status, net_sharpe)
# Groups : "FX (rate-diff)", "FX (portfolio)", "FX (TA)", "Cross-asset trend",
#          "US equity", "Crypto", "India equity", "Overlays", "Rigour / diag"
# Status : "working", "borderline", "rejected", "timing_artefact", "overlay",
#          "rigour"
STRATEGIES = [
    # Rate-diff family — look-ahead confirmed by notebooks/fx_timestamp_audit.py
    (1,  "EURUSD Δ2Y-diff",               "FX (rate-diff)",    "timing_artefact", 2.75),
    (2,  "GBPUSD Δ2Y-diff",               "FX (rate-diff)",    "timing_artefact", 1.50),
    (3,  "AUDUSD Δ2Y-diff",               "FX (rate-diff)",    "timing_artefact", 1.22),
    (4,  "NZDUSD Δ2Y-diff",               "FX (rate-diff)",    "timing_artefact", 0.92),
    (5,  "USDJPY Δ2Y-diff",               "FX (rate-diff)",    "timing_artefact", 1.44),
    (6,  "USDCAD Δ2Y-diff",               "FX (rate-diff)",    "timing_artefact", 2.06),
    (7,  "USDCHF Δ2Y-diff",               "FX (rate-diff)",    "rejected",        0.00),
    (8,  "USDSEK Δ2Y-diff",               "FX (rate-diff)",    "timing_artefact", 2.13),
    # 9 deferred (NOK 2Y unavailable)
    (10, "Portfolio (core4)",             "FX (portfolio)",    "timing_artefact", 2.70),
    (11, "X-sec 21d momentum",            "FX (TA)",           "rejected",       -0.34),
    (12, "Portfolio calibrated",          "FX (portfolio)",    "timing_artefact", 2.73),
    (13, "COT ±2σ + 21-DMA (L+S)",        "FX (TA)",           "rejected",       -0.07),
    (14, "Portfolio + trend filter",      "FX (portfolio)",    "timing_artefact", 1.59),
    (15, "EURUSD SMA+RSI combo",          "FX (TA)",           "rejected",       -0.34),
    (16, "VIX safe-haven short",          "FX (TA)",           "rejected",       -0.39),
    (17, "Oil → USDCAD",                  "FX (TA)",           "timing_artefact", 3.96),
    (18, "Portfolio equal-weight",        "FX (portfolio)",    "timing_artefact", 2.90),
    (19, "Oil → USDCAD +1d lag (verify)", "Rigour / diag",     "rigour",         -0.84),
    (20, "Vol-normalised carry",          "FX (portfolio)",    "borderline",      0.07),
    (21, "EURUSD +1d lag (verify)",       "Rigour / diag",     "rigour",         -0.58),
    (22, "Carry crash filter overlay",    "Overlays",          "overlay",         2.91),  # applied to #18
    (23, "Donchian/ATR breakout",         "FX (TA)",           "rejected",       -0.18),
    (24, "Turtle System 1 (FX)",          "FX (TA)",           "rejected",       -0.28),  # 24b
    (25, "Turtle on commods+crypto",      "Cross-asset trend", "working",         0.43),
    (26, "Carry-TSMOM overlay on #20",    "Overlays",          "rejected",        0.01),
    (27, "20/50 MA cross (FX)",           "FX (TA)",           "rejected",       -0.09),
    (28, "20/50 MA cross (commods+crypto)","Cross-asset trend","working",         0.42),
    (29, "Crash filter overlay on #28",   "Overlays",          "working",         0.51),
    (30, "Crash filter overlay on #25",   "Overlays",          "rejected",        0.41),
    (31, "X-sec 5d MR (FX)",              "FX (TA)",           "rejected",       -0.19),
    (32, "Inflation-diff x-sec (FX)",     "FX (TA)",           "rejected",       -0.13),
    (33, "SPY 200-DMA tactical",          "US equity",         "borderline",      0.88),
    (34, "Faber 5-asset GTAA",            "US equity",         "rejected",        0.61),
    (35, "Crypto x-sec 3M momentum",      "Crypto",            "working",         1.44),
    (36, "Crash filter overlay on #35",   "Overlays",          "rejected",        1.45),
    (37, "#35 robustness sweep (24 var)", "Rigour / diag",     "rigour",          1.35),   # median across grid
    (38, "Nifty 100 Low-Vol 30",          "India equity",      "working",         1.34),
    (39, "US SPDR sector 12-1 mom",       "US equity",         "rejected",        0.65),
    (40, "Dollar carry factor (DOL)",     "FX (portfolio)",    "rejected",        0.10),
    (41, "Commodity→FX weekly",           "FX (portfolio)",    "rejected",       -0.28),
    (42, "Crypto mom + risk layer",       "Crypto",            "working",         1.68),
    (43, "Diversified TSMOM 25 ETFs",     "Cross-asset trend", "borderline",      0.29),
    (44, "Business-cycle FX (CLI)",       "FX (portfolio)",    "borderline",      0.14),
    (45, "FX value (REER)",               "FX (portfolio)",    "rejected",       -0.15),
    (46, "FX carry+mom+value",            "FX (portfolio)",    "rejected",        0.05),
    (47, "India 12-1 momentum",           "India equity",      "borderline",      1.42),
]

# ── Colors and legend ────────────────────────────────────────────────────────
STATUS_COLORS = {
    "working":          "#2ca02c",  # green
    "borderline":       "#ff9500",  # amber
    "rejected":         "#d62728",  # red
    "timing_artefact":  "#8c8c8c",  # grey
    "overlay":          "#1f77b4",  # blue
    "rigour":           "#8e44ad",  # purple
}

STATUS_LEGEND = [
    ("working",          "Working (deployable prior)"),
    ("borderline",       "Borderline / caveated"),
    ("rejected",         "Rejected"),
    ("timing_artefact",  "Timing artefact (rate-diff family, per #21)"),
    ("overlay",          "Overlay / risk filter"),
    ("rigour",           "Rigour check / diagnostic"),
]

# Preserve group ordering by first appearance
GROUP_ORDER = [
    "FX (rate-diff)",
    "FX (portfolio)",
    "FX (TA)",
    "Cross-asset trend",
    "Crypto",
    "US equity",
    "India equity",
    "Overlays",
    "Rigour / diag",
]


def main() -> None:
    # Group strategies
    grouped: dict[str, list[tuple]] = {g: [] for g in GROUP_ORDER}
    for row in STRATEGIES:
        num, label, group, status, sharpe = row
        grouped[group].append(row)

    # Build a flat plotting list, group-by-group, top-to-bottom
    plot_rows: list[tuple] = []           # (num, label, group, status, sharpe)
    group_separators: list[int] = []      # y-index where a new group starts

    for group in GROUP_ORDER:
        entries = sorted(grouped[group], key=lambda r: r[0])   # by strategy #
        for e in entries:
            plot_rows.append(e)
        if entries:
            group_separators.append(len(plot_rows))

    n = len(plot_rows)
    y_positions = np.arange(n)[::-1]      # top = first, matplotlib bars grow bottom→top

    labels = [f"#{r[0]:>2} — {r[1]}" for r in plot_rows]
    sharpes = [r[4] for r in plot_rows]
    colors = [STATUS_COLORS[r[3]] for r in plot_rows]
    groups = [r[2] for r in plot_rows]

    # ── Figure ───────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 14))

    bars = ax.barh(y_positions, sharpes, color=colors,
                   edgecolor="white", linewidth=0.5, height=0.72)

    # Value labels on bar ends
    for bar, val in zip(bars, sharpes):
        x = bar.get_width()
        y = bar.get_y() + bar.get_height() / 2
        anchor = x + (0.03 if x >= 0 else -0.03)
        ha = "left" if x >= 0 else "right"
        ax.text(anchor, y, f"{val:+.2f}", va="center", ha=ha,
                fontsize=8.5, color="#222")

    # Reference lines
    ax.axvline(0.0, color="black", lw=0.6, alpha=0.7)
    ax.axvline(1.0, color="#2ca02c", lw=0.6, alpha=0.5, linestyle="--")
    ax.text(1.02, 0.5, "SR=1.0 (deployable threshold)",
            transform=ax.transAxes,
            va="bottom", ha="left", rotation=90,
            fontsize=8, color="#2ca02c", alpha=0.7)

    # Group separators — thin horizontal lines and group labels on right
    prev_end = 0
    for end_idx in group_separators:
        span_y = y_positions[prev_end:end_idx]
        if len(span_y) == 0:
            continue
        # bracket line at the top of each group
        top = span_y[0] + 0.5
        bottom = span_y[-1] - 0.5
        if end_idx < n:  # separator between groups
            sep_y = span_y[-1] - 0.6
            ax.axhline(sep_y, color="#e0e0e0", lw=0.8)
        # Group label on right, at group center
        group_name = groups[prev_end]
        mid_y = (top + bottom) / 2
        ax.text(1.03, mid_y, group_name,
                transform=ax.get_yaxis_transform(),
                va="center", ha="left",
                fontsize=9.5, color="#333", fontweight="semibold")
        prev_end = end_idx

    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Net Sharpe Ratio (2010–2024, or as constrained by data)", fontsize=11)
    ax.set_xlim(-1.2, 4.3)
    ax.set_ylim(-0.8, n - 0.2)
    ax.grid(True, axis="x", alpha=0.25, linestyle=":")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Title
    n_working    = sum(1 for r in plot_rows if r[3] == "working")
    n_borderline = sum(1 for r in plot_rows if r[3] == "borderline")
    n_rejected   = sum(1 for r in plot_rows if r[3] == "rejected")
    n_timing     = sum(1 for r in plot_rows if r[3] == "timing_artefact")
    n_overlay    = sum(1 for r in plot_rows if r[3] == "overlay")
    n_rigour     = sum(1 for r in plot_rows if r[3] == "rigour")
    ax.set_title(
        f"g10-systematic-fx — strategy scoreboard  ·  {n} strategies · "
        f"{n_working} working, {n_borderline} borderline, {n_rejected} rejected, "
        f"{n_timing} timing-artefact (rate-diff family), {n_overlay+n_rigour} overlays/diagnostics",
        fontsize=12, pad=14,
    )

    # Legend
    handles = [mpatches.Patch(color=STATUS_COLORS[k], label=lbl)
               for k, lbl in STATUS_LEGEND]
    ax.legend(handles=handles, loc="lower right",
              fontsize=9, frameon=True, framealpha=0.95,
              edgecolor="#ccc", title="Status", title_fontsize=9.5)

    fig.text(0.02, 0.005,
             "Sharpes for the rate-diff family (#1–#10, #12, #18) are apparent — flagged as timing artefact by #21's +1d-lag verification. "
             "See STRATEGIES.md for the full audit trail and per-strategy caveats.",
             fontsize=8, color="#666", style="italic")

    plt.tight_layout(rect=[0, 0.02, 0.92, 1])
    out = REPORTS / "strategy_dashboard.png"
    plt.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out.relative_to(REPO)}")
    print(f"  {n} strategies · {n_working} working · {n_borderline} borderline · "
          f"{n_rejected} rejected · {n_timing} timing-artefact · "
          f"{n_overlay} overlays · {n_rigour} rigour checks")


if __name__ == "__main__":
    main()
