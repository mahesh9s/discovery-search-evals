"""Draw the one chart the write-up needs: NDCG@10 by intent slice.

    python -m evals.chart        # writes results/dev/ndcg_by_slice.png

Three systems only. The point of the picture is that an average hides the
shape underneath it, and more series would bury that.
"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from .data import RESULTS

SERIES = [  # (system, legend label, colour)
    ("keyword_meta", "Baseline: keywords on title, cast, genre", "#2a78d6"),
    ("semantic", "Semantic POC: embeddings", "#eb6834"),
    ("keyword_pinned", "Going to A/B: synopsis index + exact-match pinning", "#1baf7a"),
]
SURFACE, INK, INK_2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BAR, GAP = 0.2, 0.025   # bar width and the sliver of surface between neighbours, in slot units


def main() -> None:
    metrics = json.loads((RESULTS / "dev" / "metrics.json").read_text(encoding="utf-8"))
    means = metrics["means"]
    slices = [s for s in means["keyword_meta"] if s != "all"]
    groups = [("all", "All 40 queries")] + [(s, s.capitalize()) for s in slices]
    # The overall group sits apart from the per-intent groups.
    centres = [0.0] + [1.35 + i for i in range(len(slices))]

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, ax = plt.subplots(figsize=(9.6, 4.5), dpi=200, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.set_xlim(-0.6, centres[-1] + 0.6)
    ax.set_ylim(0, 1.06)
    fig.subplots_adjust(left=0.065, right=0.985, top=0.74, bottom=0.11)

    # Rounded tops, square at the baseline: draw a rounded box that starts
    # below zero and let the axes clip the bottom off.
    box = ax.get_window_extent()
    aspect = (1.06 / box.height) / ((ax.get_xlim()[1] - ax.get_xlim()[0]) / box.width)
    for i, (system, _, colour) in enumerate(SERIES):
        offset = (i - (len(SERIES) - 1) / 2) * (BAR + GAP)
        for (key, _), centre in zip(groups, centres):
            value = means[system][key]["ndcg@10"]
            if value > 0.012:
                ax.add_patch(FancyBboxPatch(
                    (centre + offset - BAR / 2, -0.2), BAR, value + 0.2,
                    boxstyle="round,pad=0,rounding_size=0.035", mutation_aspect=aspect,
                    facecolor=colour, edgecolor="none", clip_on=True, zorder=3))
            else:  # too short to round: a flat sliver so a zero still reads as a bar
                ax.bar(centre + offset, max(value, 0.006), BAR, color=colour, zorder=3)
            ax.text(centre + offset, value + 0.018, f"{value:.2f}", ha="center", va="bottom",
                    fontsize=7.5, color=INK if key == "all" else INK_2,
                    fontweight="bold" if key == "all" else "normal", zorder=4)

    ax.set_xticks(centres)
    ax.set_xticklabels([label for _, label in groups], color=INK_2, fontsize=9)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0", "0.25", "0.50", "0.75", "1.00"], color=MUTED, fontsize=8)
    ax.tick_params(length=0, pad=6)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.axvline((centres[0] + centres[1]) / 2, color=GRID, linewidth=0.8, zorder=1)

    fig.text(0.065, 0.945, "Same average, opposite shape", fontsize=14, fontweight="bold", color=INK, va="top")
    fig.text(0.065, 0.875, "NDCG@10 by query intent on the development set (8 queries per intent). Higher is better.",
             fontsize=9, color=INK_2, va="top")
    handles = [plt.Rectangle((0, 0), 1, 1, color=colour) for _, _, colour in SERIES]
    legend = fig.legend(handles, [label for _, label, _ in SERIES], loc="upper left",
                        bbox_to_anchor=(0.058, 0.83), ncol=3, frameon=False, fontsize=8.5,
                        handlelength=1.0, handleheight=1.0, columnspacing=1.6, handletextpad=0.6)
    for text in legend.get_texts():
        text.set_color(INK_2)

    out = RESULTS / "dev" / "ndcg_by_slice.png"
    fig.savefig(out, facecolor=SURFACE)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
