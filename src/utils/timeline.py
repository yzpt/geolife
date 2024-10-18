import plotly.graph_objs as go

from src.models.trajectories import Trajectories

import random
random_colors_list = [f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 1)' for i in range(500)]

def plot_timeline(
    trajectories: Trajectories,
    y_data: str = 'speed',
    mode: str = 'markers',
    height: int = 250,
    marker: dict = dict(color='red', size=5),
    colors_list: list = random_colors_list,
) -> go.Figure:
    fig = go.Figure()
    for i, trajectory in enumerate(trajectories.trajectories):
        color = colors_list[i]
        fig.add_trace(go.Scatter(
            x=trajectory.gdf['datetime'],
            y=trajectory.gdf['speed'],
            mode=mode,
            line=dict(
                width=2,
                color=color
            ),
            marker=dict(
                size=5,
                color=color),
            name=f'Trajectory {i}',
            hoverinfo='text',
        ))
    fig.update_layout(
        template='plotly_dark',
        margin=dict(l=0, r=0, t=0, b=0),
        yaxis=dict(range=[0, 200]),
        height=250,
    )
    return fig
