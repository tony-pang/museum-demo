from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt


def scatter_population_visitors(df: pd.DataFrame, loglog: bool = False, title: Optional[str] = None):
    fig, ax = plt.subplots(figsize=(6, 4))
    if not df.empty:
        ax.scatter(df["population"], df["visitors"], alpha=0.6)
    ax.set_xlabel("City population")
    ax.set_ylabel("Museum annual visitors")
    if loglog:
        ax.set_xscale("log")
        ax.set_yscale("log")
    if title:
        ax.set_title(title)
    fig.tight_layout()
    return fig, ax
