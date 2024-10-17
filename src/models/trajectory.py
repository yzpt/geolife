from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
import pandas as pd
from geopy.distance import geodesic

from src.models.record import Record
from src.utils.parsers import RecordParser


@dataclass
class Trajectory:
    """
    A class to represent a trajectory consisting of multiple records.

    Attributes:
        trajectory_id (str): The unique identifier for the trajectory.
        user_id (str): The unique identifier for the user.
        records (List[Record]): A list of Record objects representing the trajectory.
        df (pd.DataFrame): A DataFrame containing the trajectory records and computed features.

    Properties:
        count (int): The number of records in the trajectory.
        start_datetime (datetime): The earliest datetime in the trajectory records.
        end_datetime (datetime): The latest datetime in the trajectory records.
        duration (datetime): The duration of the trajectory (end_datetime - start_datetime).
        centroid (Dict): The centroid of the trajectory as the average latitude and longitude.

    Methods:
        from_file(cls, file_path: str, user_id: str, trajectory_id: str, parser: RecordParser) -> 'Trajectory':
            Create a Trajectory object from a file using a specific parser.
        compute_dataframe():
            Compute the DataFrame with the trajectory records, time differences, distance, and speed.
        _calculate_time_diffs(df: pd.DataFrame) -> List[float]:
            Calculate the time difference in seconds between consecutive records.
        _calculate_distances(df: pd.DataFrame) -> List[float]:
            Calculate the distance in meters between consecutive records using geopy.
        _calculate_speeds(df: pd.DataFrame) -> List[float]:
            Calculate the speed in meters per second between consecutive records.
        features -> Dict:
            Return a dictionary with the trajectory features.
    """
    
    trajectory_id: str
    user_id: str
    records: List[Record]
    df: pd.DataFrame = None
    
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
            df=pd.DataFrame([record.__dict__ for record in records])
        )
        return trajectory
    
    def compute_dataframe(self):
        """
        Compute the DataFrame with the trajectory records, time differences, distance, and speed
        """
        columns = ['user_id', 'trajectory_id', 'label', 'datetime', 'latitude', 'longitude', 'altitude', 'timestamp']
        df = pd.DataFrame([record.__dict__ for record in self.records])[columns]
        
        # Add time differences, distance, and speed between consecutive records
        print(f'Computing features for trajectory {self.trajectory_id}...')
        df['time_diff'] = self._calculate_time_diffs(df)
        df['distance'] = self._calculate_distances(df)
        df['speed'] = self._calculate_speeds(df)
        
        self.df = df
    
    def _calculate_time_diffs(self, df: pd.DataFrame) -> List[float]:
        """
        Calculate the time difference in seconds between consecutive records
        """
        df = df.sort_values(by='datetime')  # Ensure records are sorted by datetime
        time_diffs = df['datetime'].diff().dt.total_seconds()  # Calculate time differences in seconds
        return time_diffs.fillna(0).tolist()  # Fill NaN for the first row with 0 and return as a list
    
    def _calculate_distances(self, df: pd.DataFrame) -> List[float]:
        """
        Calculate the distance in meters between consecutive records using geopy
        """
        df = df.sort_values(by='datetime')  # Ensure records are sorted by datetime
        distances = [0]  # The first record has 0 distance
        for i in range(1, len(df)):
            coord1 = (df.iloc[i - 1]['latitude'], df.iloc[i - 1]['longitude'])
            coord2 = (df.iloc[i]['latitude'], df.iloc[i]['longitude'])
            distance = geodesic(coord1, coord2).meters  # Distance in meters
            distances.append(distance)
        return distances
    
    def _calculate_speeds(self, df: pd.DataFrame) -> List[float]:
        """
        Calculate the speed in meters per second between consecutive records
        Speed is computed as distance divided by time difference
        """
        df = df.sort_values(by='datetime')  # Ensure records are sorted by datetime
        speeds = [0]  # The first record has 0 speed
        for i in range(1, len(df)):
            time_diff = df.iloc[i]['time_diff']  # Time difference in seconds
            distance = df.iloc[i]['distance']  # Distance in meters
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
            'centroid': self.centroid,
        }
        
