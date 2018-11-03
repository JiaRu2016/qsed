import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


def ohlc_plot(ax, df, open_='open', high_='high', low_='low', close_='close', t_='trading_day', width_=0.7, n_=10):
    assert isinstance(df, pd.DataFrame)
    assert all([x in df.columns for x in (open_, high_, low_, close_)])
    n = len(df)
    width = width_
    offset = width / 2.0

    for i in range(n):
        op = df[open_].values[i]
        hi = df[high_].values[i]
        lo = df[low_].values[i]
        cl = df[close_].values[i]

        x = i
        y = min(op, cl)
        height = abs(cl - op)
        is_raise = op < cl
        clr = 'red' if is_raise else 'green'
        fill = True  # True if is_raise else False

        rect = Rectangle((x - offset, y), width, height, facecolor=clr, edgecolor=clr, linewidth=1, fill=fill)
        vline = Line2D(xdata=(x, x), ydata=(lo, hi), linewidth=1, color=clr)

        ax.add_patch(rect)
        ax.add_line(vline)

    ax.autoscale_view()

    x_label_idx = n_ * np.array(range(len(df) // n_ + 1))
    x_labels = df[t_].iloc[x_label_idx].values
    ax.xaxis.set_major_locator(plt.FixedLocator(x_label_idx))
    ax.xaxis.set_major_formatter(plt.FixedFormatter(x_labels))
