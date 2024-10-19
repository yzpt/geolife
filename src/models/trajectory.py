from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple
import geopandas as gpd
from geopy.distance import geodesic

from models.record import Record
from utils.parsers import RecordParser


@dataclass
class Trajectory:
    """
    A class to represent a trajectory of records with various properties and methods to compute
    geospatial and temporal features.
    Attributes
    ----------
    trajectory_id : str
        Unique identifier for the trajectory.
    user_id : str
        Identifier for the user associated with the trajectory.
    records : List[Record]
        List of records that make up the trajectory.
    gdf : gpd.GeoDataFrame, optional
        GeoDataFrame containing the trajectory records (default is None).
    Properties
    ----------
    count : int
        Number of records in the trajectory.
    start_datetime : datetime
        The earliest datetime in the trajectory records.
    end_datetime : datetime
        The latest datetime in the trajectory records.
    duration : datetime
        The duration of the trajectory (end_datetime - start_datetime).
    centroid : Dict
        The centroid of the trajectory as the average latitude and longitude.
    features : Dict
        A dictionary with the trajectory features.
    Methods
    -------
    from_file(cls, file_path: str, user_id: str, trajectory_id: str, parser: RecordParser) -> 'Trajectory'
        Create a Trajectory object from file using a specific parser.
    compute_geodataframe() -> gpd.GeoDataFrame
        Compute the GeoDataFrame with the trajectory records, time differences, distance, and speed.
    _calculate_time_diffs(gdf: gpd.GeoDataFrame) -> List[float]
        Calculate the time difference in seconds between consecutive records.
    _calculate_distances(gdf: gpd.GeoDataFrame) -> List[float]
        Calculate the distance in meters between consecutive records using geopy.
    _calculate_speeds(gdf: gpd.GeoDataFrame) -> List[float]
        Calculate the speed in meters per second between consecutive records.
    """
    
    trajectory_id: str
    user_id: str
    records: List[Record]
    gdf: gpd.GeoDataFrame = None
    
    def __post_init__(self):
        if self.gdf is None:
            self.gdf = gpd.GeoDataFrame([record.__dict__ for record in self.records])
    
    @property
    def count(self) -> int:
        return len(self.records)
    
    @property
    def start_datetime(self) -> datetime:
        return min([record.datetime for record in self.records])
    
    @property
    def end_datetime(self) -> datetime:
        return max([record.datetime for record in self.records])
    
    @property
    def duration(self) -> datetime:
        return self.end_datetime - self.start_datetime
    
    @property
    def centroid(self) -> Dict:
        """
        Return the centroid of the trajectory as the average latitude and longitude
        """
        latitude = sum([record.latitude for record in self.records]) / self.count
        longitude = sum([record.longitude for record in self.records]) / self.count
        return {'latitude': latitude, 'longitude': longitude}
    
    @classmethod
    def from_file(
        cls: 'Trajectory',
        file_path: str,
        user_id: str,
        trajectory_id: str,
        parser: RecordParser
    ) -> 'Trajectory':
        """
        Create a Trajectory object from file using a specific parser
        """
        records = parser.parse(
            file_path=file_path, 
            user_id=user_id,
            trajectory_id=trajectory_id
        )
        trajectory = cls(
            trajectory_id=trajectory_id, 
            user_id=user_id, 
            records=records, 
            gdf=gpd.GeoDataFrame([record.__dict__ for record in records])
        )
        return trajectory
    
    def compute_geodataframe(self):
        """
        Compute the GeoDataFrame with the trajectory records, time differences, distance, and speed
        """
        columns = ['user_id', 'trajectory_id', 'label', 'datetime', 'latitude', 'longitude', 'altitude', 'timestamp']
        geometry = gpd.points_from_xy(self.gdf['longitude'], self.gdf['latitude'])
        print(f'Computing GeoDataFrame for trajectory {self.trajectory_id} with {self.count} records')
        self.gdf['time_diff'] = self._calculate_time_diffs(self.gdf)
        self.gdf['distance'] = self._calculate_distances(self.gdf)
        self.gdf['speed'] = self._calculate_speeds(self.gdf)

    
    def _calculate_time_diffs(self, gdf: gpd.GeoDataFrame) -> List[float]:
        """
        Calculate the time difference in seconds between consecutive records
        """
        gdf = gdf.sort_values(by='datetime')  # Ensure records are sorted by datetime
        time_diffs = gdf['datetime'].diff().dt.total_seconds()  # Calculate time differences in seconds
        return time_diffs.fillna(0).tolist()  # Fill NaN for the first row with 0 and return as a list
    
    def _calculate_distances(self, gdf: gpd.GeoDataFrame) -> List[float]:
        """
        Calculate the distance in meters between consecutive records using geopy
        """
        gdf = gdf.sort_values(by='datetime')  # Ensure records are sorted by datetime
        distances = [0]  # The first record has 0 distance
        for i in range(1, len(gdf)):
            coord1 = (gdf.iloc[i - 1]['latitude'], gdf.iloc[i - 1]['longitude'])
            coord2 = (gdf.iloc[i]['latitude'], gdf.iloc[i]['longitude'])
            distance = geodesic(coord1, coord2).meters  # Distance in meters
            distances.append(distance)
        return distances
    
    def _calculate_speeds(self, gdf: gpd.GeoDataFrame) -> List[float]:
        """
        Calculate the speed in meters per second between consecutive records
        Speed is computed as distance divided by time difference
        """
        gdf = gdf.sort_values(by='datetime')  # Ensure records are sorted by datetime
        speeds = [0]  # The first record has 0 speed
        for i in range(1, len(gdf)):
            time_diff = gdf.iloc[i]['time_diff']  # Time difference in seconds
            distance = gdf.iloc[i]['distance']  # Distance in meters
            speed = distance / time_diff if time_diff > 0 else 0  # Speed in m/s
            speeds.append(speed)
        return speeds
    
    @property
    def features(self) -> Dict:
        """
        Return a dictionary with the trajectory features
        """
        return {
            'trajectory_id': self.trajectory_id,
            'user_id': self.user_id,
            'count': self.count,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'duration': self.duration,
            # 'centroid': self.centroid,
        }
        
    def filter_by_datetimerange(
        self, 
        datetime_range: Tuple[datetime, datetime]
    ) -> 'Trajectory':
        """
        Filter the trajectory records by a specific time range
        """
        records = [record for record in self.records if datetime_range[0] <= record.datetime <= datetime_range[1]]
        self.records = records
        return self
        