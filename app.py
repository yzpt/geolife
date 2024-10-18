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

from src.models.trajectory import Trajectory
from src.models.trajectories import Trajectories
from src.utils.trackmap import plot_map
from src.utils.timeline import plot_timeline

from src.layout import create_layout


import pickle
with open(os.path.join(os.getenv('OUTPUT_PATH'), 'trajectories_user_001.pkl'), 'rb') as f:
    trajectories = pickle.load(f)


# print(trajectories.features.head())


app = dash.Dash(__name__)
app.layout = create_layout(trajectories)






    
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
