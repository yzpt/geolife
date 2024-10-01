from dataclasses import dataclass
from typing import List
import pandas as pd
import os

from record import Record
from trajectory import Trajectory

@dataclass
class Trajectories:
    trajectories: List['Trajectory']

    @property
    def df(self) -> pd.DataFrame:
        """
        Return a DataFrame with all the records from all the trajectories
        """
        columns = ['user_id', 'trajectory_id', 'label', 'datetime', 'latitude', 'longitude', 'altitude', 'timestamp']
        return pd.concat([trajectory.df for trajectory in self.trajectories])[columns]

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
        cls: 'Trajectories',
        user_id: str,
        data_path: str = os.path.join(os.getenv('PROJECT_PATH'), 'data')
    ) -> 'Trajectories':
        """
        Create a Trajectories object from a user_id string
        """
        user_path = os.path.join(data_path, user_id)
        trajectories = []
        records_files_paths = [
            os.path.join(user_path, 'Trajectory', file)
            for file in os.listdir(os.path.join(user_path, 'Trajectory'))
            if file.endswith('.plt')
        ]
        records_files_paths.sort()
        for i, file in enumerate(records_files_paths):
            trajectory = Trajectory.from_file(file_path=file, user_id=user_id, id=f'{user_id}_{i}')
            trajectories.append(trajectory)
        trajectories = cls.update_trajectory_ids(trajectories)
        trajectories = cls.update_labels(trajectories, user_path)
        return cls(trajectories=trajectories)

    @staticmethod
    def update_labels(trajectories: List['Trajectory'], user_path: str) -> List['Trajectory']:
        """
        Update the labels of the trajectories
        """
        df_labels = Trajectories.extract_labels(user_path)
        for _, row in df_labels.iterrows():
            for trajectory in trajectories:
                for record in trajectory.records:
                    if row['start_datetime'] <= record.datetime <= row['end_datetime']:
                        record.label = row['mode']
        return trajectories

    @staticmethod
    def update_trajectory_ids(
        trajectories: List['Trajectory'],
    ) -> List['Trajectory']:
        """
        Update the trajectory_id of the records
        """
        for i, trajectory in enumerate(trajectories):
            for record in trajectory.records:
                record.trajectory_id = f'{trajectory.id}'
        return trajectories

    @staticmethod
    def extract_labels(user_path: str) -> pd.DataFrame:
        """
        Extract the labels from the labels.txt file, return a DataFrame
        """
        labels_file = os.path.join(user_path, 'labels.txt')
        if not os.path.exists(labels_file):
            return pd.DataFrame(columns=['start_datetime', 'end_datetime', 'mode'])

        df_labels = pd.DataFrame(columns=['start_datetime', 'end_datetime', 'mode'])
        with open(labels_file) as f:
            for line in f:
                if 'Time' in line:
                    continue
                start_datetime, end_datetime, mode = line.strip().split('\t')
                df_labels = pd.concat([df_labels, pd.DataFrame({
                    'start_datetime': [start_datetime],
                    'end_datetime': [end_datetime],
                    'mode': [mode]
                })])
        
        df_labels['start_datetime'] = pd.to_datetime(df_labels['start_datetime'])
        df_labels['end_datetime'] = pd.to_datetime(df_labels['end_datetime'])
        return df_labels