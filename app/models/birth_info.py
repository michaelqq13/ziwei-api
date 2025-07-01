from dataclasses import dataclass

@dataclass
class BirthInfo:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    gender: str  # 'M' for male, 'F' for female
    longitude: float  # 經度
    latitude: float   # 緯度 