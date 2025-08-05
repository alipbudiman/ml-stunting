from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from typing import List, Dict
import json


class ConnectionManager:
    """Manager for WebSocket connections"""
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # {device_id: [websockets]}
        self.connection_devices: Dict[WebSocket, str] = {}  # {websocket: device_id}

    async def connect(self, websocket: WebSocket, device_id: str):
        await websocket.accept()
        
        if device_id not in self.active_connections:
            self.active_connections[device_id] = []
        
        self.active_connections[device_id].append(websocket)
        self.connection_devices[websocket] = device_id
        print(f"Client connected to device {device_id}. Total connections: {len(self.active_connections[device_id])}")

    def disconnect(self, websocket: WebSocket):
        device_id = self.connection_devices.get(websocket)
        if device_id and device_id in self.active_connections:
            self.active_connections[device_id].remove(websocket)
            if not self.active_connections[device_id]:  # Remove empty device list
                del self.active_connections[device_id]
        
        if websocket in self.connection_devices:
            del self.connection_devices[websocket]
        
        print(f"Client disconnected from device {device_id}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            # Check if websocket is still open before sending
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending personal message: {e}")
            # Auto-disconnect if websocket is closed
            self.disconnect(websocket)

    async def broadcast_to_device(self, device_id: str, message: dict):
        """Broadcast message to all clients connected to specific device"""
        if device_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[device_id]:
                try:
                    # Check if websocket is still connected before sending
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await websocket.send_text(json.dumps(message))
                    else:
                        disconnected.append(websocket)
                except Exception as e:
                    print(f"Error broadcasting to device {device_id}: {e}")
                    disconnected.append(websocket)
            
            # Remove disconnected websockets
            for ws in disconnected:
                self.disconnect(ws)

    async def broadcast_all(self, message: dict):
        """Broadcast message to all connected clients"""
        for device_id in self.active_connections:
            await self.broadcast_to_device(device_id, message)