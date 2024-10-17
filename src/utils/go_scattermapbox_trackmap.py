import plotly.graph_objects as go
import pandas as pd
import os

def plot_map(
    df: pd.DataFrame,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    color_col: str = "trajectory_id",
    mapbox_token: str = os.getenv("MAPBOX_TOKEN"),
    center_lat: float = None,
    center_lon: float = None,
    zoom: float = 8,
    mapbox_style: str = "dark",
    template: str = "plotly_dark",
    marker_size: int = 10,
):
    fig = go.Figure() # ======================== make a loop for each trajectory
    fig.add_trace(
        go.Scattermapbox(
            lat=df[lat_col],
            lon=df[lon_col],
            marker=dict(
                size=marker_size,
                color=df[color_col].astype('category').cat.codes,
            ),
            mode='markers',
            # cluster=dict(enabled=True),
        )
    )
    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_token,
            center=dict(
                lat=center_lat if center_lat else df[lat_col].mean(),
                lon=center_lon if center_lon else df[lon_col].mean()
            ),
            zoom=zoom,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        # mapbox_style="dark",
        template=template,
    )
    return fig
