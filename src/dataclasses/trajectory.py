from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
import pandas as pd

from record import Record

@dataclass
class Trajectory:
    id: str
    user_id: str
    records: List[Record]
    
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
    
    @classmethod
    def from_file(
        cls: 'Trajectory',
        file_path: str,
        user_id: str,
        id: str
    ) -> 'Trajectory':
        """
        Create a Trajectory object from a .plt file
        """
        plt_files_columns = ['latitude', 'longitude', 'zero', 'altitude', 'days', 'date', 'time']
        df = pd.read_csv(file_path, skiprows=6, header=None, names=plt_files_columns)
        df.drop(columns=['zero', 'days'], inplace=True)
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        df['timestamp'] = df['datetime'].apply(lambda x: x.timestamp())
        df.drop(columns=['date', 'time'], inplace=True)
        df['user_id'] = user_id
        records = [Record(**record) for record in df.to_dict(orient='records')]
        return cls(user_id=user_id, records=records, id=id)
    
    @property
    def df(self) -> pd.DataFrame:
        """
        Return a DataFrame with the trajectory records
        """
        columns = ['user_id', 'trajectory_id', 'label', 'datetime', 'latitude', 'longitude', 'altitude', 'timestamp']
        return pd.DataFrame([record.__dict__ for record in self.records])[columns]
    
    @property
    def features(self) -> Dict:
        """
        Return a dictionary with the trajectory features
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'count': self.count,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'duration': self.duration,
        }
