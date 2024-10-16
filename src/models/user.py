from dataclasses import dataclass
from typing import List

from src.models.trajectory import Trajectory

@dataclass
class User:
    id: str
    trajectories: List[Trajectory]
    
    @property
    def trajectories_count(self) -> int:
        return len(self.trajectories)
    
    @property
    def records_count(self) -> int:
        return sum([trajectory.count for trajectory in self.trajectories])
    
    @property
    def average_centroid(self) -> dict:
        """
        Return the average centroid of the user trajectories
        """
        latitude = sum([trajectory.centroid['latitude'] for trajectory in self.trajectories]) / self.trajectories_count
        longitude = sum([trajectory.centroid['longitude'] for trajectory in self.trajectories]) / self.trajectories_count
        return {'latitude': latitude, 'longitude': longitude}
    
    @property
    def features(self) -> dict:
        """
        Return a dictionary with the user features
        """
        return {
            'id': self.id,
            'trajectories_count': self.trajectories_count,
            'records_count': self.records_count,
            'average_centroid': self.average_centroid
        }
        
    
    
