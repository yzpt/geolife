from dataclasses import dataclass
from typing import List
import pandas as pd
import os

from src.models.trajectory import Trajectory
from src.models.trajectory_updater import TrajectoryUpdater
from src.models.label_extractor import LabelExtractor

from src.utils.parsers import PltRecordParser

@dataclass
class Trajectories:
    trajectories: List['Trajectory']

    def __post_init__(self):
        self.updater = TrajectoryUpdater()
        self.label_extractor = LabelExtractor()

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

    @classmethod
    def update_labels(cls, trajectories: List['Trajectory'], user_path: str) -> List['Trajectory']:
        """
        Update the labels of the trajectories using the LabelExtractor
        """
        label_extractor = LabelExtractor()
        df_labels = label_extractor.extract_labels(user_path)
        updater = TrajectoryUpdater()
        return updater.update_labels(trajectories, df_labels)

    @classmethod
    def update_trajectory_ids(cls, trajectories: List['Trajectory']) -> List['Trajectory']:
        """
        Update the trajectory_id of the records using the TrajectoryUpdater
        """
        updater = TrajectoryUpdater()
        return updater.update_trajectory_ids(trajectories)
