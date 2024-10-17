from typing import List
import pandas as pd
from abc import ABC, abstractmethod
from typing import List

from src.models.record import Record

class RecordParser(ABC):
    @abstractmethod
    def parse(
        self, 
        file_path: str, 
        user_id: str,
        trajectory_id: str
    ) -> List[Record]:
        """
        Parse the file and return a list of Record objects
        """
        pass

class PltRecordParser(RecordParser):
    def parse(
        self, 
        file_path: str, 
        user_id: str,
        trajectory_id: str
    ) -> List[Record]:
        """
        Parse a .plt file and return a list of Record objects
        """
        plt_files_columns = ['latitude', 'longitude', 'zero', 'altitude', 'days', 'date', 'time']
        df = pd.read_csv(file_path, skiprows=6, header=None, names=plt_files_columns)
        df.drop(columns=['zero', 'days'], inplace=True)
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        df['timestamp'] = df['datetime'].apply(lambda x: x.timestamp())
        df.drop(columns=['date', 'time'], inplace=True)
        df['user_id'] = user_id
        df['trajectory_id'] = trajectory_id
        return [Record(**record) for record in df.to_dict(orient='records')]
