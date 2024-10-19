import plotly.graph_objs as go

from models.trajectories import Trajectories

import random
random_colors_list = [f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 1)' for i in range(500)]

def plot_timeline(
    trajectories: Trajectories,
    y_data: str = 'speed',
    mode: str = 'markers+lines',
    height: int = 250,
    marker: dict = dict(color='red', size=5),
    colors_list: list = random_colors_list,
) -> go.Figure:
    fig = go.Figure()
    for i, trajectory in enumerate(trajectories.trajectories):
        fig.add_trace(go.Scatter(
            x=trajectory.gdf['datetime'],
            y=trajectory.gdf[y_data],
            mode=mode,
            line=dict(
                width=1,
                color=colors_list[i%len(colors_list)],
                shape='spline',
            ),
            marker=dict(
                size=3,
                color=colors_list[i%len(colors_list)],
            ),
            name=f'Trajectory {i}',
            hoverinfo='text',
            showlegend=False,
        ))
    fig.update_layout(
        template='plotly_dark',
        margin=dict(l=0, r=0, t=0, b=0),
        yaxis=dict(
            range=[0, max(50, trajectories.gdf[y_data].quantile(0.99) + 20)]
            ),
        height=250,
    )
    return fig
