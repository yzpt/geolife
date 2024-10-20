import plotly.graph_objects as go
import geopandas as gpd
import os

from models.trajectories import Trajectories

import random
random_colors_list = [f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 1)' for i in range(500)]

def plot_map(
    trajectories: Trajectories,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    colors_list: list = random_colors_list,
    mode: str = "markers+lines",
    mapbox_token: str = os.getenv("MAPBOX_TOKEN"),
    center_lat: float = None,
    center_lon: float = None,
    zoom: float = 8,
    mapbox_style: str = "dark",
    template: str = "plotly_dark",
    marker_size: int = 10,
    height: int = 400,
):
    fig = go.Figure()
    for i, trajectory in enumerate(trajectories.trajectories):
        color = colors_list[i % len(colors_list)]
        fig.add_trace(go.Scattermapbox(
            lat=trajectory.gdf['latitude'],
            lon=trajectory.gdf['longitude'],
            mode=mode,
            line=dict(
                width=2,
                color=trajectory.color,
            ),
            marker=dict(
                size=marker_size,
                color=trajectory.color,
            ),
            name=f'Trajectory {i}',
            hoverinfo='text',
            showlegend=False,
        ))
        
    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_token,
            center=dict(
                lat=trajectory.gdf['latitude'].mean() if center_lat is None else center_lat, 
                lon=trajectory.gdf['longitude'].mean() if center_lon is None else center_lon
            ),
            zoom=zoom,
            style=mapbox_style,
        ),
        template=template,
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
    )
    
    return fig