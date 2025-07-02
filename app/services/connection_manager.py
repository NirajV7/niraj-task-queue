# In app/services/connection_manager.py

from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # A list to hold all active WebSocket connections
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepts a new connection and adds it to the list."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Removes a connection from the list."""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """Sends a message to all connected clients."""
        for connection in self.active_connections:
            await connection.send_text(message)

# Create a single, global instance of the manager that our entire app can use
manager = ConnectionManager()