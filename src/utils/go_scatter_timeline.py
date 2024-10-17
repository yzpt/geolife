import pandas as pd
import plotly.graph_objs as go

def plot_timeline(
    df: pd.DataFrame,
    y_data: str,
    mode: str = 'markers',
    height: int = 250,
    marker: dict = dict(color='red', size=5),
) -> go.Figure:
    if df.empty:
        return go.Figure(go.Scatter(), layout=dict(title="No data available"))
    
    df = df.copy()
    
    fig = go.Figure()

    # Define color map
    color_map = {'walk': 'blue', 'bike': 'green', 'bus': 'red', 'car': 'orange', 'train': 'purple', 'subway': 'black'}
    
    # Add traces for each label
    for label, color in color_map.items():
        label_df = df[df['label'] == label]
        fig.add_trace(
            go.Scatter(
                x=label_df['datetime'],
                y=label_df[y_data],
                mode=mode,
                marker=dict(size=marker['size'], color=color, opacity=marker.get('opacity', 1)),
                line=dict(width=2, color=color),
                name=label,
                hoverinfo='text',
                hovertext=label_df.columns,
                showlegend=True,
                visible=True,
            )
        )
    
    fig.update_layout(
        yaxis1=dict(
            title=y_data,
        ),
        mapbox_style='dark',
        template='plotly_dark',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(
            title="Traces:",
            x=0,
            y=1,
            xanchor='left',
            yanchor='top',
            orientation='h',
        ),
        height=height,
    )
    return fig
