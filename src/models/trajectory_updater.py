from typing import List
from src.models.trajectory import Trajectory
import pandas as pd

class TrajectoryUpdater:
    def update_labels(self, trajectories: List['Trajectory'], df_labels: pd.DataFrame) -> List['Trajectory']:
        """
        Update the labels of the trajectories
        """
        for _, row in df_labels.iterrows():
            for trajectory in trajectories:
                for record in trajectory.records:
                    if row['start_datetime'] <= record.datetime <= row['end_datetime']:
                        record.label = row['mode']
        return trajectories

    def update_trajectory_ids(self, trajectories: List['Trajectory']) -> List['Trajectory']:
        """
        Update the trajectory_id of the records
        """
        for i, trajectory in enumerate(trajectories):
            for record in trajectory.records:
                record.trajectory_id = f'{trajectory.id}'
        return trajectories
