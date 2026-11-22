"""One consistent, accessible chart style for every figure in the project.

Colours come from a colour-blind-validated categorical palette, used in a
fixed order. Control is always slot 1 (blue) and treatment slot 2 (orange),
in every chart.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter

from . import config

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#0d366b"]
SURFACE, INK, INK_2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
VARIANT_COLORS = {"control": SERIES[0], "treatment": SERIES[1]}


def use_style() -> None:
    mpl.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "figure.figsize": (9, 4.2),
            "figure.dpi": 110,
            "font.family": "sans-serif",
            "font.size": 10,
            "text.color": INK,
            "axes.labelcolor": INK_2,
            "axes.edgecolor": AXIS,
            "axes.linewidth": 0.8,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.titlepad": 12,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "axes.axisbelow": True,
            "axes.prop_cycle": mpl.cycler(color=SERIES),
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelcolor": INK_2,
            "ytick.labelcolor": INK_2,
            "lines.linewidth": 2,
            "legend.frameon": False,
            "legend.fontsize": 9,
        }
    )


def brl(x, _=None) -> str:
    """Format Brazilian reais compactly: R$1.2M, R$350k, R$95."""
    if abs(x) >= 1e6:
        return f"R${x / 1e6:.1f}M"
    if abs(x) >= 1e3:
        return f"R${x / 1e3:.0f}k"
    return f"R${x:.0f}"


BRL = FuncFormatter(brl)
PCT = PercentFormatter(1.0, decimals=0)


def titled(ax, title: str, sub: str | None = None) -> None:
    """Bold left-aligned title with an optional one-line takeaway underneath."""
    ax.set_title(title, pad=24 if sub else 12)
    if sub:
        ax.annotate(sub, xy=(0, 1), xycoords="axes fraction", xytext=(0, 7), textcoords="offset points",
                    ha="left", va="bottom", fontsize=9, color=INK_2)


def save(fig, name: str) -> None:
    config.IMAGES_DIR.mkdir(exist_ok=True)
    fig.savefig(config.IMAGES_DIR / f"{name}.png", dpi=150, bbox_inches="tight")
