from dataclasses import dataclass
from typing import List, Tuple
import geopandas as gpd
import pandas as pd
import os
from datetime import datetime


from models.trajectory import Trajectory
from utils.parsers import PltRecordParser

@dataclass
class Trajectories:
    """
    The `Trajectories` class represents a collection of trajectory data and provides various methods to manipulate and analyze this data.
    Attributes:
        trajectories (List['Trajectory']): A list of `Trajectory` objects.
    Properties:
        user_ids_list (List[str]): Returns a sorted list of unique user IDs from the trajectories.
        trajectory_ids_list (List[str]): Returns a sorted list of unique trajectory IDs from the trajectories.
        gdf (gpd.GeoDataFrame): Returns a GeoDataFrame containing all records from all trajectories.
        average_centroid (dict): Returns the average centroid (latitude and longitude) of the trajectories.
        features (gpd.GeoDataFrame): Returns a GeoDataFrame with the features of all the trajectories.
    Methods:
        from_user(cls, data_path: str = os.getenv('DATA_PATH'), user_ids: List[str] = None, user_id: str = None) -> 'Trajectories':
            Creates a `Trajectories` object from a list of user IDs or a single user ID.
        load_trajectories(user_path: str, user_id: str) -> List['Trajectory']:
            Loads trajectories from files in a user's folder.
        extract_labels(user_path: str) -> gpd.GeoDataFrame:
            Extracts labels from the `labels.txt` file and returns a GeoDataFrame.
        ugpdate_labels(user_path: str) -> None:
            Updates the `Record.labels` values and the DataFrame with labels for each trajectory.
        compute_trajectories_geodataframes() -> None:
            Computes the GeoDataFrame with the trajectory records, time differences, distance, and speed.
    """
    
    trajectories: List['Trajectory']

    @property
    def user_ids_list(self) -> List[str]:
        """
        Return the list of user IDs
        """
        user_ids_list = list(set([trajectory.user_id for trajectory in self.trajectories]))
        user_ids_list.sort()
        return user_ids_list
    
    @property
    def trajectory_ids_list(self) -> List[str]:
        """
        Return the list of trajectory IDs
        """
        trajectory_ids_list = list(set([trajectory.trajectory_id for trajectory in self.trajectories]))
        trajectory_ids_list.sort()
        return trajectory_ids_list

    @property
    def gdf(self) -> gpd.GeoDataFrame:
        """
        Return a GeoDataFrame with all the records from all the trajectories
        """
        # columns = ['user_id', 'trajectory_id', 'label', 'datetime', 'latitude', 'longitude', 'altitude', 'timestamp']
        # return gpd.concat([trajectory.gdf for trajectory in self.trajectories])[columns]
        return gpd.GeoDataFrame(pd.concat([trajectory.gdf for trajectory in self.trajectories]))

    @property
    def average_centroid(self) -> dict:
        """
        Return the average centroid of the trajectories
        """
        latitude = sum([trajectory.centroid['latitude'] for trajectory in self.trajectories]) / self.trajectories_count
        longitude = sum([trajectory.centroid['longitude'] for trajectory in self.trajectories]) / self.trajectories_count
        return {'latitude': latitude, 'longitude': longitude}
    
    @property
    def features(self) -> gpd.GeoDataFrame:
        """
        Return a GeoDataFrame with the features of all the trajectories
        """
        gdf = gpd.GeoDataFrame([trajectory.features for trajectory in self.trajectories])
        gdf.sort_values(by='start_datetime', inplace=True)
        return gdf

    @classmethod
    def from_user(
        cls, 
        data_path: str = os.getenv('DATA_PATH'),
        user_ids: List[str] = None,
        user_id: str = None
    ) -> 'Trajectories':
        """
        Create a Trajectories object from a user_ids list
        """
        if (user_id and user_ids
            or not user_ids and not user_id):
            raise ValueError('Provide either user_id:str or user_ids:List[str]')
        user_ids = [user_id] if user_id else user_ids
        trajectories = []
        for user_id in user_ids:
            user_path = os.path.join(data_path, user_id)
            trajectories += cls.load_trajectories(user_path, user_id)
        return cls(trajectories)

    @staticmethod
    def load_trajectories(
        user_path: str, 
        user_id: str
    ) -> List['Trajectory']:
        """
        Load trajectories from files in a user's folder
        """
        records_files_paths = [
            os.path.join(user_path, 'Trajectory', file)
            for file in os.listdir(os.path.join(user_path, 'Trajectory'))
            if file.endswith('.plt')
        ]
        records_files_paths.sort()
        trajectories = []
        for i, file in enumerate(records_files_paths):
            trajectory = Trajectory.from_file(
                            file_path=file, 
                            user_id=user_id, 
                            trajectory_id=f'{user_id}_{i}',
                            parser=PltRecordParser()
                        )
            print(f'Loaded trajectory {trajectory.trajectory_id} with {trajectory.count} records')
            trajectories.append(trajectory)
        return trajectories
    
    def extract_labels(
        self, 
        user_path: str
    ) -> pd.DataFrame:
        """
        Extract the labels from the labels.txt file, return a GeoDataFrame
        """
        labels_file = os.path.join(user_path, 'labels.txt')
        if not os.path.exists(labels_file):
            return gpd.GeoDataFrame(columns=['start_datetime', 'end_datetime', 'label'])

        df_labels = pd.DataFrame(columns=['start_datetime', 'end_datetime', 'label'])
        with open(labels_file) as f:
            for line in f:
                if 'Time' in line:
                    continue
                start_datetime, end_datetime, mode = line.strip().split('\t')
                df_labels = pd.concat([df_labels, gpd.GeoDataFrame({
                    'start_datetime': [start_datetime],
                    'end_datetime': [end_datetime],
                    'label': [mode]
                })])
        
        df_labels['start_datetime'] = pd.to_datetime(df_labels['start_datetime'])
        df_labels['end_datetime'] = pd.to_datetime(df_labels['end_datetime'])
        return df_labels
    
    def ugpdate_labels(
        self,
        user_path: str
    ) -> None:
        """
        Ugpdate the Record.labels values & the gdf with labels for each trajectory
        """
        df_labels = self.extract_labels(user_path)
        df_labels.sort_values('start_datetime', inplace=True)
        if df_labels.empty:
            return
        df_records = pd.concat([trajectory.gdf for trajectory in self.trajectories])
        df_records.drop(columns=['label'], inplace=True)
        df_records = pd.merge_asof(
            df_records.sort_values('datetime'),
            df_labels,
            left_on='datetime',
            right_on='start_datetime',
            direction='backward',
            suffixes=('', '_label'),
            # add only the label column from right GeoDataFrame
        ).drop(columns=['start_datetime', 'end_datetime'])
        # ugpdate the Record values & the gdf for each trajectory
        for trajectory in self.trajectories:
            trajectory_gdf = df_records[df_records['trajectory_id'] == trajectory.trajectory_id]
            trajectory.gdf = trajectory_gdf
            for record, row in zip(trajectory.records, trajectory_gdf.itertuples()):
                record.label = row.label
    
    def compute_trajectories_speed(
        self,
    ) -> None:
        """
        Compute the GeoDataFrame with the trajectory records, time differences, distance, and speed
        """
        for trajectory in self.trajectories:
            trajectory.compute_speed()
            
    def filter_trajectories(self, datetime_range: Tuple[datetime, datetime]) -> 'Trajectories':
        """
        Filter the trajectories by start_datetime and end_datetime without recomputing speed.
        """
        filtered_trajectories = Trajectories(
            [
                trajectory.filter_by_datetimerange(datetime_range)
                for trajectory in self.trajectories
                if trajectory.filter_by_datetimerange(datetime_range).gdf.shape[0] > 0
            ]
        )
        return filtered_trajectories