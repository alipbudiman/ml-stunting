import asyncio
import logging
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from lib.prediction import  ZScoreCalculator
from lib.prediction import parse_tanggal_lahir, parser_usia_bulan, parser_gender, parser_usia_tahun
from lib.main import HealthResponse
from lib.prediction import PredictionInput, PredictionOutput, Prediction, PredictionOutputWithMessage, DataAnakInput
from lib.main import ConnectionManager
from lib.main import DataFromIOT, ResponseMessage

# Create FastAPI app instance
app = FastAPI(
    title="ML Stunting API",
    description="Simple FastAPI template for ML Stunting predictions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

prediction = Prediction()
calculator = ZScoreCalculator()


manager = ConnectionManager()
    
data_devices = {}
device_register = ['IOT_001']


# Health check endpoint
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        message="ML Stunting API is running successfully"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="API is working properly"
    )

# Reset data in data_devices by did
@app.post("/reset/{did}", response_model=ResponseMessage)
async def reset_data(did: str):
    if did in data_devices:
        del data_devices[did]
        return ResponseMessage(
            status=200,
            message="Data reset successfully"
        )
    else:
        return ResponseMessage(
            status=404,
            message="Device not found"
        )

# trigger IOT for start collecting data
@app.post("/trigger/{did}", response_model=ResponseMessage)
async def trigger_iot(did: str):
    """
    Trigger IOT device to start collecting data
    """
    if did in data_devices:
        data_devices[did]["triggered"] = True
        return ResponseMessage(
            status=200,
            message=f"Device {did} triggered to start collecting data"
        )
    else:
        return ResponseMessage(
            status=404,
            message=f"Device {did} not found"
        )

# Data Received from IOT device
# receiving tb and bb data from IOT device
@app.post(
    "/recive",
    response_model=ResponseMessage,
    summary="Receive data from IOT device",
    description="Receive height (tb) and weight (bb) data from IOT device for further processing",
    responses={
        200: {
            "description": "Data received successfully",
            "model": ResponseMessage
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid input data"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            }
        }
    }
)
async def recive_form_device(data: DataFromIOT):
    """Receive data (bb/tb) from IOT device"""
    data_devices[data.did] = {
        "tb": data.tb,
        "bb": data.bb,
        "status": "updated",
        "last_updated": asyncio.get_event_loop().time(),
        "triggered": False  # Set to False initially, can be updated later
    }
    
    # Broadcast updated data to clients connected to this specific device
    if manager.active_connections:
        broadcast_data = {
            "did": data.did,
            "tb": data.tb,
            "bb": data.bb,
            "timestamp": asyncio.get_event_loop().time(),
            "status": "updated",
            "source": "iot_device"
        }
        await manager.broadcast_to_device(data.did, broadcast_data)
    
    return ResponseMessage(
        status=200,
        message=f"Data received successfully for device {data.did}"
    )

# Prediction endpoint
# used for calculating Z-score and predicting stunting status
@app.post("/predict", 
          response_model=PredictionOutputWithMessage,
          summary="Predict stunting status",
          description="Predict stunting status based on child's data including birth weight, current weight, height, and other parameters",
          responses={
                200: {
                    "description": "Successful prediction",
                    "model": PredictionOutputWithMessage
                },
                400: {
                    "description": "Invalid input data",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Invalid input data"}
                        }
                    }
                },
                500: {
                    "description": "Internal server error",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Internal server error"}
                        }
                    }
                }
          }
)
async def predict_stunting(request: DataAnakInput):
    """
    Predict stunting based on input features
    - **tanggal_lahir**: Child's birth date (YYYY-MM-DD format)
    - **jenis_kelamin**: Gender (L for male, P for female)
    - **bb_lahir**: Birth weight in kg
    - **tb_lahir**: Birth height in cm
    - **berat**: Current weight in kg
    - **tinggi**: Current height in cm  
    Returns prediction result with stunting status and confidence score.
    """
    try:
        # Convert request to PredictionInput
        data_anak = parse_tanggal_lahir(request.tanggal_lahir)
        age_in_months = parser_usia_bulan(data_anak.tahun, data_anak.bulan)
        age = parser_usia_tahun(data_anak.tahun, data_anak.bulan, data_anak.hari)
        gender = parser_gender(request.jenis_kelamin)
        zscore_result = calculator.calculate_zscore(
            age_months=age_in_months,
            weight_kg=request.berat,
            height_cm=request.tinggi,
            sex=gender
        )
        
        if not zscore_result.calculated:
            raise HTTPException(status_code=400, detail="Error calculating Z-scores")
        
        data_anak = PredictionInput(
            usia=age,
            jenis_kelamin=request.jenis_kelamin,
            bb_lahir=request.bb_lahir,
            tb_lahir=request.tb_lahir,
            tanggal_lahir=request.tanggal_lahir,
            berat=request.berat,
            tinggi=request.tinggi,
            zs_bbu=zscore_result.bbu,
            zs_tbu=zscore_result.tbu,
            zs_bbtb=zscore_result.bbtb
        )

        # Perform prediction
        result = prediction.predict(data_anak)
        logger.info(f"Prediction result: {result}")
        
        msg = prediction.penangana_gejalan(
            result.bbu,
            result.tbu,
            result.bbtb
        )
        
        return PredictionOutputWithMessage(
            data=result,
            message=msg
        )
         
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# Get model info
@app.get("/model/info")
async def get_model_info():
    """Get information about the ML model"""
    return {
        "model_name": "XGBoost Stunting Predictor",
        "version": "1.0.0",
        "features": ["feature1", "feature2", "feature3"],
        "description": "Model for predicting stunting in children"
    }

# Get WebSocket connection status
@app.get("/ws/status")
async def get_websocket_status():
    """Get current WebSocket connection status for all devices"""
    total_connections = sum(len(connections) for connections in manager.active_connections.values()) if hasattr(manager.active_connections, 'values') else len(manager.active_connections)
    
    devices_status = {}
    for device_id, device_data in data_devices.items():
        devices_status[device_id] = {
            "data": device_data,
            "connections": len(manager.active_connections.get(device_id, [])) if hasattr(manager.active_connections, 'get') else 0
        }
    
    return {
        "total_connections": total_connections,
        "devices": devices_status,
        "total_devices": len(data_devices),
        "status": "active" if total_connections > 0 else "no_connections"
    }

@app.get("/devices")
async def get_all_devices():
    """Get all registered devices"""
    return {
        "devices": data_devices,
        "total_devices": len(data_devices)
    }

@app.get("/devices/{device_id}")
async def get_device_data(device_id: str):
    """Get specific device data"""
    device_data = data_devices.get(device_id)
    if device_data and device_id in device_register:
        return {
            "device_id": device_id,
            "data": device_data,
            "connections": len(manager.active_connections.get(device_id, [])) if hasattr(manager.active_connections, 'get') else 0
        }
    else:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

# fetch data from IOT device (data_device) using websocket
@app.websocket("/ws/data/{device_id}")
async def websocket_data(websocket: WebSocket, device_id: str):
    """WebSocket endpoint to fetch data from specific IOT device"""
    await manager.connect(websocket, device_id)
    try:
        while True:
            
            # Check if websocket is still connected
            if websocket.client_state != WebSocketState.CONNECTED:
                break
                
            # Send current device data if exists
            if device_id in data_devices:
                device_data = data_devices[device_id]
                data_with_timestamp = {
                    "did": device_id,
                    "tb": device_data["tb"],
                    "bb": device_data["bb"],
                    "timestamp": asyncio.get_event_loop().time(),
                    "status": device_data["status"],
                    "last_updated": device_data["last_updated"]
                }
            else:
                data_with_timestamp = {
                    "did": device_id,
                    "tb": 0,
                    "bb": 0,
                    "timestamp": asyncio.get_event_loop().time(),
                    "status": "no_data",
                    "message": f"No data available for device {device_id}"
                }
            
            await manager.send_personal_message(data_with_timestamp, websocket)
            await asyncio.sleep(5)  # Send every 5 seconds
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client disconnected from device {device_id}")
    except Exception as e:
        logger.error(f"WebSocket error for device {device_id}: {e}")
        manager.disconnect(websocket)

# Run the app
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Allow access from all network interfaces
        port=5000,
        reload=False,
        workers=1,  # Number of worker processes
        access_log=True,  # Enable access logging
        log_level="info"  # Set log level
    )