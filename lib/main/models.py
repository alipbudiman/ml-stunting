from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    message: str

class DataFromIOT(BaseModel):
    """
    Input model for data received from IOT device
    Parameters:
    - tb: Tinggi Badan dalam cm
    - bb: Berat Badan dalam kg
    """
    did: str
    tb: float
    bb: float

class ResponseMessage(BaseModel):
    """
    Response model for API messages
    """
    status: int
    message: str