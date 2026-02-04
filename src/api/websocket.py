from datetime import datetime
from typing import Dict, Set
import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger

from src.api.middleware.auth import verify_token


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.broadcast_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket, user_id: int | None = None):
        try:
            await websocket.accept()
        except Exception as e:
            logger.error(f"Error accepting WebSocket: {e}")
            return
        
        if user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
            logger.info(f"WebSocket connected for user {user_id}")
        else:
            self.broadcast_connections.add(websocket)
            logger.info("Anonymous WebSocket connected for broadcasts")
    
    def disconnect(self, websocket: WebSocket, user_id: int | None = None):
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"WebSocket disconnected for user {user_id}")
        else:
            self.broadcast_connections.discard(websocket)
            logger.info("Anonymous WebSocket disconnected")
    
    async def send_personal(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.add(connection)
            
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    async def broadcast(self, message: dict):
        all_connections = set()
        for connections in self.active_connections.values():
            all_connections.update(connections)
        all_connections.update(self.broadcast_connections)
        
        disconnected = set()
        for connection in all_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                disconnected.add(connection)
        
        for conn in disconnected:
            self.broadcast_connections.discard(conn)
            for user_id, conns in self.active_connections.items():
                conns.discard(conn)
    
    async def broadcast_price_update(self, prices: list[dict]):
        message = {
            "type": "price_update",
            "data": prices,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast(message)
    
    async def send_alert_triggered(self, user_id: int, alert: dict):
        message = {
            "type": "alert_triggered",
            "data": alert,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.send_personal(user_id, message)
    
    def get_connection_count(self) -> int:
        count = len(self.broadcast_connections)
        for connections in self.active_connections.values():
            count += len(connections)
        return count


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    user_id = None
    
    try:
        # Accept the connection first
        await manager.connect(websocket)
        
        try:
            # Wait for auth message
            auth_message = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
            auth_data = json.loads(auth_message)
            
            if auth_data.get("type") == "auth" and auth_data.get("token"):
                try:
                    payload = verify_token(auth_data["token"])
                    user_id = payload.get("telegram_id")
                    
                    if user_id not in manager.active_connections:
                        manager.active_connections[user_id] = set()
                    
                    # Move from broadcast to active
                    manager.broadcast_connections.discard(websocket)
                    manager.active_connections[user_id].add(websocket)
                    
                    await websocket.send_json({
                        "type": "auth_success",
                        "message": "Authenticated successfully",
                    })
                    logger.info(f"WebSocket authenticated for user {user_id}")
                except Exception as e:
                    await websocket.send_json({
                        "type": "auth_error",
                        "message": str(e),
                    })
                    logger.warning(f"WebSocket auth failed: {e}")
                    manager.broadcast_connections.add(websocket)
            else:
                manager.broadcast_connections.add(websocket)
                await websocket.send_json({
                    "type": "connected",
                    "message": "Connected as anonymous user",
                })
        except asyncio.TimeoutError:
            manager.broadcast_connections.add(websocket)
            await websocket.send_json({
                "type": "connected",
                "message": "Connected as anonymous user (auth timeout)",
            })
        
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message.get("type") == "subscribe":
                    await websocket.send_json({
                        "type": "subscribed",
                        "channel": message.get("channel"),
                    })
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected (user_id={user_id})")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        manager.disconnect(websocket, user_id)
