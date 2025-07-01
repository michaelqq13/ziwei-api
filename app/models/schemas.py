from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class BirthInfoSchema(BaseModel):
    year: int = Field(..., description="西元年")
    month: int = Field(..., ge=1, le=12, description="西元月")
    day: int = Field(..., ge=1, le=31, description="西元日")
    hour: int = Field(..., ge=0, le=23, description="西元時")
    minute: int = Field(..., ge=0, le=59, description="西元分")
    gender: str = Field(..., pattern="^(M|F)$", description="性別 (M:男, F:女)")
    longitude: float = Field(..., description="出生地經度")
    latitude: float = Field(..., description="出生地緯度")

class ChartRequestWithCustomStem(BaseModel):
    birth_data: BirthInfoSchema
    custom_stem: str = Field(..., description="自定義天干")

class PalaceSchema(BaseModel):
    stars: List[str]
    element: str
    stem: str
    branch: str
    body_palace: Optional[bool] = Field(default=False, description="是否為身宮")

class LunarDataSchema(BaseModel):
    year: str
    month: str
    day: str
    year_gan_zhi: str
    month_gan_zhi: str
    day_gan_zhi: str
    hour_gan_zhi: str

class PurpleStarChartSchema(BaseModel):
    birth_info: BirthInfoSchema
    lunar_data: LunarDataSchema
    palaces: Dict[str, PalaceSchema]
