from dataclasses import dataclass
from datetime import datetime

@dataclass
class Record:
    user_id: str
    latitude: float
    longitude: float
    altitude: float
    datetime: datetime
    timestamp: float
    label: str = None
    trajectory_id: str = None