"""
Pydantic models for CR310 datalogger data validation
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Any


class CR310Reading(BaseModel):
    """Model for CR310 datalogger reading"""
    equipo: str = Field(..., description="Equipment identifier")
    SO2_ppb: float = Field(..., ge=0, description="SO2 concentration in ppb")
    H2S_ppb: float = Field(..., ge=0, description="H2S concentration in ppb")
    Reaction_Temp: float = Field(..., description="Reaction temperature in °C")
    IZS_Temp: float = Field(..., description="IZS temperature in °C")
    PMT_Temp: float = Field(..., description="PMT temperature in °C")
    SampleFlow: float = Field(..., ge=0, description="Sample flow")
    Pressure: float = Field(..., description="System pressure")
    UVLampIntensity: float = Field(..., ge=0, description="UV lamp intensity")
    Box_Temp: float = Field(..., description="Box temperature in °C")
    HVPS_V: float = Field(..., ge=0, description="HVPS voltage")
    Conv_Temp: float = Field(..., description="Converter temperature in °C")
    Ozone_flow: float = Field(..., ge=0, description="Ozone flow")
    timestamp: str = Field(..., description="Timestamp of the reading")

    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Validate timestamp format"""
        try:
            # Parse timestamp to ensure it's valid
            datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
            return v
        except ValueError:
            raise ValueError('timestamp must be in format: YYYY-MM-DD HH:MM:SS')

    @validator('equipo')
    def validate_equipo(cls, v):
        """Validate equipment identifier"""
        if not v or len(v.strip()) == 0:
            raise ValueError('equipo cannot be empty')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "equipo": "T101",
                "SO2_ppb": 25.43,
                "H2S_ppb": 2.18,
                "Reaction_Temp": 35.0,
                "IZS_Temp": 34.2,
                "PMT_Temp": 36.1,
                "SampleFlow": 452.3,
                "Pressure": 29.76,
                "UVLampIntensity": 403.5,
                "Box_Temp": 33.7,
                "HVPS_V": 671.2,
                "Conv_Temp": 35.9,
                "Ozone_flow": 480.5,
                "timestamp": "2025-10-27 18:30:00"
            }
        }


class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: str
    code: int = 200
    timestamp: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReadingsListResponse(BaseModel):
    """Response for list of readings"""
    success: bool
    message: str
    count: int
    total: int
    data: List[Any]
    timestamp: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

