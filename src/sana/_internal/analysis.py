from datetime import UTC, datetime, timedelta
from pathlib import Path

import plotly.graph_objects as go
import polars as pl


def read_file(path: Path) -> pl.DataFrame:
    content = path.read_text()
    xs = []
    ys = []
    for line in content.splitlines():
        x, y = line.split()
        xs.append(float(x))
        ys.append(float(y))
    return pl.DataFrame({"x": xs, "y": ys}).with_columns(
        x=pl.col("x").mul(1000).cast(pl.Duration("ms"))
    )


def plot_raw_data(data: pl.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=(data["x"].cast(pl.Int64) / 1000).to_list(),
            y=data["y"].to_list(),
        )
    )
    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Power (ms<sup>2</sup>)",
    )
    return fig


def plot_sliding_mean(
    data: pl.DataFrame,
    every: timedelta,
    period: timedelta,
    offset: timedelta,
) -> go.Figure:
    base_time = datetime(2024, 1, 1, tzinfo=UTC)
    data = (
        data.with_columns(x=pl.lit(base_time) + pl.col("x"))
        .group_by_dynamic(
            "x",
            every=every,
            period=period,
            offset=offset,
        )
        .agg(pl.col("y").mean())
        .with_columns(x=pl.col("x") - pl.lit(base_time))
    )
    fig = go.Figure(
        go.Scatter(
            x=(data["x"].cast(pl.Int64) / 1000).to_list(),
            y=data["y"].to_list(),
        )
    )
    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Mean Power (ms<sup>2</sup>)",
    )
    return fig


def plot_cum_sum(data: pl.DataFrame) -> go.Figure:
    fig = go.Figure(
        go.Scatter(
            x=(data["x"].cast(pl.Int64) / 1000).to_list(),
            y=data["y"].cum_sum().to_list(),
        )
    )
    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Cumulative Power (ms<sup>2</sup>)",
    )
    return fig
