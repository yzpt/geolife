from dataclasses import dataclass
from typing import List
import pandas as pd
import os

from src.models.trajectory import Trajectory
from src.utils.parsers import PltRecordParser

@dataclass
class Trajectories:
    """
    The `Trajectories` class represents a collection of trajectory data and provides methods to manipulate and retrieve this data.
    Attributes:
        trajectories (List['Trajectory']): A list of `Trajectory` objects.
    Properties:
        df (pd.DataFrame): Returns a DataFrame with all the records from all the trajectories.
        features (pd.DataFrame): Returns a DataFrame with the features of all the trajectories.
    Methods:
        from_user(cls, data_path: str = os.getenv('DATA_PATH'), user_ids: List[str] = None, user_id: str = None) -> 'Trajectories':
            Creates a `Trajectories` object from a list of user IDs or a single user ID.
        load_trajectories(user_path: str, user_id: str) -> List['Trajectory']:
            Loads trajectories from files in a user's folder.
        extract_labels(self, user_path: str) -> pd.DataFrame:
            Extracts the labels from the `labels.txt` file and returns a DataFrame.
        update_labels(cls, trajectories: List['Trajectory'], user_path: str) -> List['Trajectory']:
            Updates the labels of the trajectories based on the `labels.txt` file.
        update_trajectory_ids(cls, trajectories: List['Trajectory']) -> List['Trajectory']:
            Updates the `trajectory_id` of the records using the `TrajectoryUpdater`.
    """
    trajectories: List['Trajectory']

    @property
    def df(self) -> pd.DataFrame:
        """
        Return a DataFrame with all the records from all the trajectories
        """
        columns = ['user_id', 'trajectory_id', 'label', 'datetime', 'latitude', 'longitude', 'altitude', 'timestamp']
        return pd.concat([trajectory.df for trajectory in self.trajectories])[columns]

    @property
    def average_centroid(self) -> dict:
        """
        Return the average centroid of the trajectories
        """
        latitude = sum([trajectory.centroid['latitude'] for trajectory in self.trajectories]) / self.trajectories_count
        longitude = sum([trajectory.centroid['longitude'] for trajectory in self.trajectories]) / self.trajectories_count
        return {'latitude': latitude, 'longitude': longitude}
    
    @property
    def features(self) -> pd.DataFrame:
        """
        Return a DataFrame with the features of all the trajectories
        """
        df = pd.DataFrame([trajectory.features for trajectory in self.trajectories])
        df.sort_values(by='start_datetime', inplace=True)
        return df

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
                            id=f'{user_id}_{i}',
                            parser=PltRecordParser()
                        )
            trajectories.append(trajectory)
        return trajectories
    
    def extract_labels(
        self, 
        user_path: str
    ) -> pd.DataFrame:
        """
        Extract the labels from the labels.txt file, return a DataFrame
        """
        labels_file = os.path.join(user_path, 'labels.txt')
        if not os.path.exists(labels_file):
            return pd.DataFrame(columns=['start_datetime', 'end_datetime', 'label'])

        df_labels = pd.DataFrame(columns=['start_datetime', 'end_datetime', 'label'])
        with open(labels_file) as f:
            for line in f:
                if 'Time' in line:
                    continue
                start_datetime, end_datetime, mode = line.strip().split('\t')
                df_labels = pd.concat([df_labels, pd.DataFrame({
                    'start_datetime': [start_datetime],
                    'end_datetime': [end_datetime],
                    'label': [mode]
                })])
        
        df_labels['start_datetime'] = pd.to_datetime(df_labels['start_datetime'])
        df_labels['end_datetime'] = pd.to_datetime(df_labels['end_datetime'])
        return df_labels

    def update_labels(self, user_path: str) -> None:
        """
        Optimized method to update the labels of the trajectories.
        """
        try:
            df_labels = self.extract_labels(user_path)
            if df_labels.empty:
                return  # No labels to process

            # Step 1: Convert all records into a DataFrame for easier manipulation
            records_df = pd.concat([trajectory.df for trajectory in self.trajectories])

            # Step 2: Use Pandas' merge_asof to efficiently assign labels
            df_labels = df_labels.sort_values('start_datetime')
            records_df = pd.merge_asof(
                records_df.sort_values('datetime'),
                df_labels,
                left_on='datetime',
                right_on='start_datetime',
                direction='backward',
                suffixes=('', '_label')
            )

            # Step 3: Update the 'label' column for records within the label time range
            mask = (records_df['datetime'] >= records_df['start_datetime']) & (records_df['datetime'] <= records_df['end_datetime'])
            records_df.loc[mask, 'label'] = records_df.loc[mask, 'mode']

            # Step 4: Update trajectory records based on the modified DataFrame
            for trajectory in self.trajectories:
                trajectory_df = records_df[records_df['trajectory_id'] == trajectory.id]
                for record, row in zip(trajectory.records, trajectory_df.itertuples()):
                    record.label = row.label

        except Exception as e:
            print(f'Error updating labels: {e}')

    # @classmethod
    # def update_trajectory_ids(
    #     cls, 
    #     trajectories: List['Trajectory']
    # ) -> List['Trajectory']:
    #     """
    #     Update the trajectory_id of the records using the TrajectoryUpdater
    #     """
    #     for i, trajectory in enumerate(trajectories):
    #         for record in trajectory.records:
    #             record.trajectory_id = f'{trajectory.id}'
    #     return trajectories
    
    def update_trajectory_ids(self) -> None:
        """
        Update the trajectory_id of the records
        """
        for i, trajectory in enumerate(self.trajectories):
            for record in trajectory.records:
                record.trajectory_id = f'{trajectory.id}'
    
    