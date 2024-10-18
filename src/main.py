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


from dotenv import load_dotenv
load_dotenv()

from layout import create_layout




# === global variables =============================================================================
mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')
gdf = []
# ==================================================================================================


# === initialize the app ==========================================================================
app = dash.Dash(__name__)
app.layout = html.P("Loading...")
# ==================================================================================================






    
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
