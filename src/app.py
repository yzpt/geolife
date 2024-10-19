from dash import dash, dcc, html, Input, Output, State, dash_table, ctx
import pandas as pd
from plotly import graph_objects as go
import plotly.express as px
import json
from datetime import datetime, date
from typing import List, Dict, Tuple, Any
import os
import geopandas as gpd
from shapely.geometry import box

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from models.trajectory import Trajectory
from models.trajectories import Trajectories
from utils.trackmap import plot_map
from utils.timeline import plot_timeline

from layout import create_layout

import pickle
with open(os.path.join(os.getenv('OUTPUT_PATH'), 'trajectories_user_001.pkl'), 'rb') as f:
    trajectories = pickle.load(f)

import random
random_colors_list = [f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 1)' for i in range(500)]
color_scale = px.colors.cyclical.HSV
color_scale = px.colors.sample_colorscale(px.colors.cyclical.HSV, [i/300 for i in range(100)])


print(trajectories.features.head())


app = dash.Dash(__name__)
print('app created')
app.layout = create_layout(trajectories)




@app.callback(
    [
        Output('map-graph', 'figure'),
        Output('timeline-graph', 'figure')
    ],
    [
        Input('user-dropdown', 'value'),
        Input('trajectory-dropdown', 'value')
    ]
)
def update_graphs(user_id: str, trajectory_ids: List[str]) -> Tuple[go.Figure, go.Figure]:
    if trajectory_ids is None:
        trajectory_ids = []
    if not isinstance(trajectory_ids, list):
        trajectory_ids = [trajectory_ids]
    color_scale = px.colors.sample_colorscale(px.colors.cyclical.HSV, [i/len(trajectory_ids) for i in range(len(trajectory_ids))])
    trajectories_subset = Trajectories([trajectory for trajectory in trajectories.trajectories if trajectory.trajectory_id in trajectory_ids])
    
    
    print(trajectories_subset.features.head())
    print(trajectories_subset.trajectories[0].gdf.head())
    
    
    
    map_fig = plot_map(
        trajectories=trajectories_subset, 
        colors_list=color_scale,
        marker_size=5)
    
    timeline_fig = plot_timeline(
        trajectories=trajectories_subset, 
        colors_list=color_scale,
    )
    
    return map_fig, timeline_fig

    
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)



# =============================================================================
# import pandas as pd
# import plotly.graph_objects as go
# from dash import html, dcc, dash_table
# import geopandas as gpd

# from src.models.trajectories import Trajectories

# def create_layout(
#     trajectories: Trajectories
# ) -> html.Div:
#     return html.Div(
#         className='container',
#         children=[
#             html.Div(
#                 className='left-column',
#                 children=[
#                     html.Div([
#                         html.H3('GeoLife Dashboard'),
#                         dcc.Dropdown(
#                             id='user-dropdown',
#                             options=trajectories.user_ids_list,
#                             value=trajectories.user_ids_list[0],
#                         ),
#                         dcc.Dropdown(
#                             id='trajectory-dropdown',
#                             options=trajectories.trajectory_ids_list,
#                             value=trajectories.trajectory_ids_list[0],
#                             multi=True,
#                         )],
#                     ),
#                     html.Div(
#                         dash_table.DataTable(
#                             id='trajectories-table',
#                             columns=[{"name": col, "id": col} for col in trajectories.features.columns],
#                             data=trajectories.features.to_dict('records'),
#                             filter_action='native',
#                             sort_action='native',
#                             style_filter=dict(color='white', backgroundColor='#777'),
#                             fixed_rows={'headers': True},
#                             style_table={'overflowY': 'auto', 'height': '300px'},
#                             style_cell=dict(color='white', backgroundColor='rgb(50, 50, 50)'),
#                         ),
#                     )
#                 ]
#             ),
#             # Right column with graphs
#             html.Div(
#                 className='right-column',
#                 children=[
#                     html.Div(
#                         className='map-graph-container',
#                         children=[
#                             dcc.Graph(
#                                 id='map-graph',
#                                 className='map-graph',
#                                 config=dict(scrollZoom=True),
#                                 figure=go.Figure().update_layout(template='plotly_dark'),
#                                 style={"height": "100%"},
#                             ),
#                         ]
#                     ),
#                     html.Div(
#                         className='timeline-graph-container',
#                         children=[
#                             dcc.Graph(
#                                 id='timeline-graph',
#                                 className='timeline-graph',
#                                 config=dict(scrollZoom=True),
#                                 figure=go.Figure().update_layout(template='plotly_dark'),
#                                 style={"height": "100%"},
#                             ),
#                         ]
#                     ),
#                 ]
#             ),
#         ]
#     )