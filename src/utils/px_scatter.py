import pandas as pd
import plotly.graph_objects as go


def plot_timeline(
    df: pd.DataFrame,
    y_data: str,
    mode: str = 'markers',
    # color_mode: str = 'red',
    height: int = 250,
    marker: dict = dict(color='red', size=5),
) -> go.Figure:
    if df.empty:
        return go.Figure(go.Scatter(), layout=dict(title="No data available"))
    
    df = df.copy()
    
    fig = go.Figure()

    # Add speed scatter plot - Motion Type
    fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df[y_data],
            mode=mode,
            marker=marker,
            name=y_data,
            hoverinfo='text',
            hovertext=df.columns,
            showlegend=True,
            visible = True,
        )
    )
    
    # Add speed_calc trcae
    # fig.add_trace(
    #     go.Scatter(
    #         x=df['datetime'],
    #         y=df['speed_calc'],
    #         mode='markers',
    #         marker=dict(color=df[color_mode].map(color_discrete_map), size=5),
    #         # line=dict(color='blue', width=1),
    #         name='Speed_calc',
    #         hoverinfo='text',
    #         hovertext=df.apply(lambda row: f"Time: {row['datetime']}"
    #                                        f"<br>Speed: {round(row['speed'], 1)}"
    #                                        f"<br>Speed_calc: {round(row['speed_calc'], 1)}"
    #                                        f"<br>Motion Type: {row['motiontype']}"
    #                                        f"<br>Mode: {row['mode']}"
    #                                        f"<br>Segment: {row['segment']}"
    #                                        f"<br>os: {row['os']}"
    #                                     #    f"<br>Altitude: {round(row['altitude'], 1)}"
    #                             , axis=1),
    #         showlegend=True,
    #         visible='legendonly',
    #     )
    # )
    
        
    fig.update_layout(
        yaxis1=dict(
            title=y_data,
            # range=[0, min(df['speed'].max() + 20, 150)],
        ),
        
        # yaxis2=dict(
        #     title='Altitude (m)',
        #     overlaying='y',
        #     side='right',
        #     showgrid=False,
        # ),
        
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