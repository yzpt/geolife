import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, dash_table
import geopandas as gpd

from src.models.trajectories import Trajectories

def create_layout(
    trajectories: Trajectories
) -> html.Div:
    return html.Div(
        className='container',
        children=[
            html.Div(
                className='left-column',
                children=[
                    html.Div([
                        html.H3('GeoLife Dashboard'),
                        dcc.Dropdown(
                            id='user-dropdown',
                            options=trajectories.user_ids_list,
                            value=trajectories.user_ids_list[0],
                        ),
                        dcc.Dropdown(
                            id='trajectory-dropdown',
                            options=trajectories.trajectory_ids_list,
                            value=trajectories.trajectory_ids_list[0],
                            multi=True,
                        )],
                    ),
                    html.Div(
                        dash_table.DataTable(
                            id='trajectories-table',
                            columns=[{"name": col, "id": col} for col in trajectories.features.columns],
                            data=trajectories.features.to_dict('records'),
                            filter_action='native',
                            sort_action='native',
                            style_filter=dict(color='white', backgroundColor='#777'),
                            fixed_rows={'headers': True},
                            style_table={'overflowY': 'auto', 'height': '300px'},
                            style_cell=dict(color='white', backgroundColor='rgb(50, 50, 50)'),
                        ),
                    )
                ]
            ),
            # Right column with graphs
            html.Div(
                className='right-column',
                children=[
                    html.Div(
                        className='map-graph-container',
                        children=[
                            dcc.Graph(
                                id='map-graph',
                                className='map-graph',
                                config=dict(scrollZoom=True),
                                figure=go.Figure().update_layout(template='plotly_dark'),
                                style={"height": "100%"},
                            ),
                        ]
                    ),
                    html.Div(
                        className='timeline-graph-container',
                        children=[
                            dcc.Graph(
                                id='timeline-graph',
                                className='timeline-graph',
                                config=dict(scrollZoom=True),
                                figure=go.Figure().update_layout(template='plotly_dark'),
                                style={"height": "100%"},
                            ),
                        ]
                    ),
                ]
            ),
        ]
    )