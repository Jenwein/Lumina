import asyncio
import logging
import json
from typing import Awaitable, Callable, Optional, Set
from websockets.asyncio.server import serve, ServerConnection
from websockets.exceptions import ConnectionClosed

from lumina.ws.protocol import Message, MessageType

logger = logging.getLogger(__name__)

class LuminaWSServer:
    def __init__(self, host: str = "localhost", port: int = 8765, heartbeat_interval: float = 30.0, heartbeat_timeout: float = 90.0) -> None:
        self.host = host
        self.port = port
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self._server = None
        self._connection: Optional[ServerConnection] = None
        self._handlers: Set[Callable[[Message], Awaitable[None]]] = set()
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        async with serve(
            self._handle_connection, 
            self.host, 
            self.port,
            process_request=self._process_request,
            ping_interval=self.heartbeat_interval,
            ping_timeout=self.heartbeat_timeout
        ) as server:
            self._server = server
            logger.info(f"Lumina WS Server listening on ws://{self.host}:{self.port}")
            await self._stop_event.wait()

    async def _process_request(self, connection, request):
        if self._connection is not None:
            logger.warning("Second connection attempt rejected during handshake.")
            # Return a response that is NOT None to reject the handshake.
            # 429 Too Many Requests or 403 Forbidden.
            return connection.respond(429, "Only one client allowed\r\n")
        return None

    async def stop(self) -> None:
        self._stop_event.set()
        if self._connection:
            await self._connection.close()
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    def on_message(self, handler: Callable[[Message], Awaitable[None]]) -> None:
        self._handlers.add(handler)

    async def send(self, message: Message) -> None:
        if self._connection:
            try:
                await self._connection.send(message.to_json())
            except ConnectionClosed:
                logger.warning("Attempted to send message to closed connection.")
                self._connection = None
        else:
            logger.warning("No active connection to send message.")

    async def _handle_connection(self, websocket: ServerConnection) -> None:
        if self._connection is not None:
            logger.warning("Second connection attempt rejected. Lumina supports only one client.")
            await websocket.close(code=4000, reason="Only one client allowed")
            return

        self._connection = websocket
        logger.info("Client connected")
        
        try:
            async for message_str in websocket:
                try:
                    msg = Message.from_json(message_str)
                    
                    if msg.type == MessageType.CLIENT_READY:
                        logger.info(f"Received client_ready: {msg.payload}")
                        ready_resp = Message(
                            type=MessageType.SERVER_READY,
                            payload={"version": "0.1.0", "capabilities": ["base"]}
                        )
                        await self.send(ready_resp)
                    elif msg.type == MessageType.HEARTBEAT:
                        # Respond with heartbeat back? Protocol says bidirectional.
                        # Usually websockets handles pings/pongs, but explicit heartbeat is in spec.
                        await self.send(Message(type=MessageType.HEARTBEAT))
                    
                    # Dispatch to registered handlers
                    for handler in self._handlers:
                        await handler(msg)
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    error_msg = Message(
                        type=MessageType.ERROR,
                        payload={"code": 500, "message": str(e)}
                    )
                    await self.send(error_msg)
        except ConnectionClosed:
            logger.info("Client disconnected")
        finally:
            if self._connection == websocket:
                self._connection = None
