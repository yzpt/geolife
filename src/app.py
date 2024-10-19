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
    trajectories: Trajectories = pickle.load(f)

import random
random_colors_list = [f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 1)' for i in range(500)]
color_scale = px.colors.cyclical.HSV
color_scale = px.colors.sample_colorscale(px.colors.cyclical.HSV, [i/300 for i in range(100)])


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
        Input('trajectory-dropdown', 'value'),
        Input('timeline-graph', 'relayoutData')
    ]
)
def update_graphs(
    # Inputs
    user_id: str, 
    trajectory_ids: List[str],
    relayoutData: Dict[str, Any],
) -> Tuple[go.Figure, go.Figure]:
    
    global trajectories
    global trajectories_subset
    
    if trajectory_ids is None:
        trajectory_ids = []
    if not isinstance(trajectory_ids, list):
        trajectory_ids = [trajectory_ids]
    color_scale = px.colors.sample_colorscale(px.colors.cyclical.HSV, [i/len(trajectory_ids) for i in range(len(trajectory_ids))])
    
    trajectories_subset = Trajectories([traj for traj in trajectories.trajectories if traj.trajectory_id in trajectory_ids])
    print(f'len(trajectories_subset.trajectories): {len(trajectories_subset.gdf)}')
    
    
    if relayoutData and 'xaxis.range[0]' in relayoutData.keys():
        print(relayoutData)
        if 'xaxis.range[0]' in relayoutData.keys():
            start_datetime = pd.to_datetime(relayoutData['xaxis.range[0]'])
            end_datetime = pd.to_datetime(relayoutData['xaxis.range[1]'])
            datetime_range = [start_datetime, end_datetime]
            print(f'len(trajectories_subset.trajectories): {len(trajectories_subset.gdf)}')
            trajectories_subset.filter_trajectories(datetime_range=datetime_range)
            print(f'len(trajectories_subset.trajectories): {len(trajectories_subset.gdf)}')
            
            map_fig = plot_map(
                trajectories=trajectories_subset, 
                colors_list=color_scale,
                marker_size=5)
            timeline_fig = plot_timeline(
                trajectories=trajectories_subset, 
                colors_list=color_scale,
            )
            return map_fig, timeline_fig
            
    
    
    map_fig = plot_map(
        trajectories=trajectories_subset, 
        colors_list=color_scale,
        marker_size=5)
    
    timeline_fig = plot_timeline(
        trajectories=trajectories_subset, 
        colors_list=color_scale,
    )
    print('---bottom---')   
    return map_fig, timeline_fig

    
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
