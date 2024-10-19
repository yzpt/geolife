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
# Get OUTPUT_PATH from environment variables with a fallback
output_path = os.getenv('OUTPUT_PATH', 'data')
print(f'output_path: {output_path}')

# Open the pickle file
with open(os.path.join(output_path, 'trajectories_001.pkl'), 'rb') as f:
    trajectories: Trajectories = pickle.load(f)
    
color_scale = px.colors.sample_colorscale(px.colors.cyclical.HSV, [i/len(trajectories.trajectory_ids_list) for i in range(len(trajectories.trajectory_ids_list))])
# shuffle color_scale
import random
random.shuffle(color_scale)

[setattr(traj, 'color', color_scale[i]) for i, traj in enumerate(trajectories.trajectories)]    

trajectories_subset = Trajectories([trajectories.trajectories[0]])

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
        Input('trajectories-dropdown', 'value'),
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
    print(f'ctx.triggered_id: {ctx.triggered_id}')
    
    if ctx.triggered_id == 'trajectories-dropdown':
        print(f'trajectory_ids: {trajectory_ids}')
        trajectories_subset = Trajectories([traj for traj in trajectories.trajectories if traj.trajectory_id in trajectory_ids])

    
    if relayoutData and 'xaxis.range[0]' in relayoutData.keys():
        print('---relayoutData---')
        if 'xaxis.range[0]' in relayoutData.keys():
            print(relayoutData)
            start_datetime = pd.to_datetime(relayoutData['xaxis.range[0]'].split('.')[0])
            end_datetime = pd.to_datetime(relayoutData['xaxis.range[1]'].split('.')[0])
            datetime_range = [start_datetime, end_datetime]
            
            trajectories_subset_filtered = trajectories_subset.filter_trajectories(datetime_range=datetime_range)
            print(f'Filtered trajectories: {len(trajectories_subset_filtered.trajectories)}')
            print(f'trajectories_subset_filtered.gdf: {trajectories_subset_filtered.gdf}')
            map_fig = plot_map(
                trajectories=trajectories_subset_filtered, 
                colors_list=color_scale,
                marker_size=5)
            timeline_fig = plot_timeline(
                trajectories=trajectories_subset_filtered,
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
    app.run_server(debug=False, host='0.0.0.0', port=8050)
