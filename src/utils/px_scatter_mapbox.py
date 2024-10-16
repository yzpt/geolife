import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_map(
    df: pd.DataFrame,
    lat: str = 'latitude',
    lon: str = 'longitude',
    color_mode: str = 'motiontype',
    zoom_init: float = 13,
    zoom_m: float = 20,
    height: int = 400,
    size_max: int = 15,
) -> px.scatter_mapbox:
 
    df = df.copy()

    # Calculate the center of the map
    center_lat = df[lat].mean()
    center_lon = df[lon].mean()
    
    # Calculate the zoom level, exclude outliers
    lat_range = df[lat].quantile(0.95) - df[lat].quantile(0.05)
    lon_range = df[lon].quantile(0.95) - df[lon].quantile(0.05)
    zoom = zoom_init - max(lat_range, lon_range) * zoom_m  # Adjust the multiplier as needed
    
    # Add text info for each point
    # df['text'] = df['datetime'].dt.strftime('%H:%M')
    
    fig = px.scatter_mapbox(
        df, 
        lat=lat, 
        lon=lon, 
        hover_data=df.columns,
        zoom=zoom,
        center={"lat": center_lat, "lon": center_lon},
        template='plotly_dark',
        size_max=size_max,
    )      
    
    if 'datetime' in df.columns:  
        fig.update_traces(
            text=df['datetime'].dt.strftime('%H:%M'),
        )
        
    fig.update_layout(
        title=dict(
            text=f"titre"
                #  f"<br>{df['os'].iloc[0]}"
                #  f"<br>",
                ,
            x=0.05,
            y=0.95,
            xanchor='left',
            yanchor='top',
            font=dict(size=12)
        ),
        showlegend=True,
        mapbox_style='carto-darkmatter',
        margin={"r":0,"t":0,"l":0,"b":0},
        legend=dict(
            title=color_mode,
            orientation='h',
            yanchor='bottom',
            xanchor='right',
            x=.95,
            y=0,
        ),
        height=height,
    )
    if 'datetime' in df.columns:
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=list([
                        dict(
                            args=[{"text": [None]}],
                            label="-",
                            method="restyle",
                        ),
                        dict(
                            args=[{"text": [df['datetime'].dt.strftime('%H:%M')]}],
                            label="hh:mm",
                            method="restyle"
                        )
                    ]),
                    pad={"r": 10, "t": 10},
                    showactive=False,
                    active=0,
                    x=0,
                    xanchor="left",
                    y=0,
                    yanchor="bottom",
                    bgcolor='#333333',
                    bordercolor='white',
                    font=dict(color='white'),
                    
                ),
            ],
        )
    return fig

