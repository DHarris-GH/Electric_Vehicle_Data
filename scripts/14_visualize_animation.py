import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path
import matplotlib as mpl

DATA_FILE = "data/final/master_dataset_full.csv"

OUT_DIR = Path("images")
OUT_DIR.mkdir(exist_ok=True)

ANIM_FILE = OUT_DIR / "EV_animation.gif"
STATIC_FILE = OUT_DIR / "EV_static_all_years.png"

df = pd.read_csv(DATA_FILE)

df = df.dropna(subset=[
    "Ports_per_10k_People",
    "EV_per_10k_People",
    "Population"
])

states = sorted(df["State"].unique())
years = sorted(df["Year"].unique())

sns.set_theme(style="whitegrid")

cols = 4
rows = (len(states) + cols - 1) // cols

# Log scale makes population colors more visible
cmap = mpl.colormaps["turbo"]
norm = mpl.colors.LogNorm(
    vmin=max(df["Population"].min(), 1),
    vmax=df["Population"].max()
)

axis_limits = {}
for state in states:
    sub = df[df["State"] == state]
    x_max = sub["Ports_per_10k_People"].max()
    y_max = sub["EV_per_10k_People"].max()

    axis_limits[state] = {
        "xlim": (0, x_max * 1.1 if x_max > 0 else 1),
        "ylim": (0, y_max * 1.1 if y_max > 0 else 1)
    }

def draw_panel(ax, sub, state):
    ax.set_xlim(axis_limits[state]["xlim"])
    ax.set_ylim(axis_limits[state]["ylim"])

    if not sub.empty:
        ax.scatter(
            sub["Ports_per_10k_People"],
            sub["EV_per_10k_People"],
            c=sub["Population"],
            cmap=cmap,
            norm=norm,
            alpha=0.85,
            s=30
        )

        sns.regplot(
            data=sub,
            x="Ports_per_10k_People",
            y="EV_per_10k_People",
            scatter=False,
            ax=ax,
            color="dodgerblue",
            ci=95,
            truncate=False
        )

    ax.set_title(state, fontsize=14, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("")

def add_labels(fig):
    fig.text(0.5, 0.04, "Ports_per_10k_People", ha="center", fontsize=12)
    fig.text(0.04, 0.5, "EV_per_10k_People", va="center", rotation="vertical", fontsize=12)

def add_colorbar(fig):
    sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # manual legend position so it does not overlap panels
    cbar_ax = fig.add_axes([0.92, 0.35, 0.02, 0.30])
    cbar = fig.colorbar(sm, cax=cbar_ax)
    cbar.set_label("Population", fontsize=11)

# ----------------------------
# STATIC: all years combined
# ----------------------------
fig_static, axes_static = plt.subplots(rows, cols, figsize=(13, 10))
axes_static = axes_static.flatten()

for j in range(len(states), len(axes_static)):
    fig_static.delaxes(axes_static[j])

axes_static = axes_static[:len(states)]

for ax, state in zip(axes_static, states):
    sub = df[df["State"] == state]
    draw_panel(ax, sub, state)

fig_static.suptitle("EV Adoption vs Charging Infrastructure, 2020–2024", fontsize=16)
add_labels(fig_static)
add_colorbar(fig_static)

fig_static.subplots_adjust(left=0.09, right=0.88, bottom=0.09, top=0.90, wspace=0.35, hspace=0.45)
fig_static.savefig(STATIC_FILE, dpi=300)
plt.close(fig_static)

print("Saved static plot to:", STATIC_FILE)

# ----------------------------
# ANIMATION: one year per frame
# ----------------------------
fig, axes = plt.subplots(rows, cols, figsize=(13, 10))
axes = axes.flatten()

for j in range(len(states), len(axes)):
    fig.delaxes(axes[j])

axes = axes[:len(states)]
add_colorbar(fig)

def update(year):
    current = df[df["Year"] == year]

    for ax, state in zip(axes, states):
        ax.clear()
        sub = current[current["State"] == state]
        draw_panel(ax, sub, state)

    fig.suptitle(f"Year: {year}", fontsize=16)
    add_labels(fig)
    fig.subplots_adjust(left=0.09, right=0.88, bottom=0.09, top=0.90, wspace=0.35, hspace=0.45)

anim = FuncAnimation(fig, update, frames=years, repeat=True)
anim.save(ANIM_FILE, writer="pillow", fps=2)
plt.close(fig)

print("Saved animation to:", ANIM_FILE)
