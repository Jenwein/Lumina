import asyncio
import json
import pytest
import websockets.asyncio.client
from lumina.ws.server import LuminaWSServer
from lumina.ws.protocol import Message, MessageType

@pytest.fixture
async def server():
    # Use a random port for testing
    server = LuminaWSServer(host="localhost", port=0)
    task = asyncio.create_task(server.start())
    # Give the server a moment to start and bind to a port
    await asyncio.sleep(0.5)
    # The actual port is in server._server.sockets[0].getsockname()[1]
    # But for simplicity, we'll try to get it if possible, or just use a known test port.
    # Actually, we can just use 8766 for testing.
    yield server
    await server.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

@pytest.mark.asyncio
async def test_handshake():
    # Start server on 8766
    server = LuminaWSServer(host="localhost", port=8766)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    
    uri = "ws://localhost:8766"
    async with websockets.asyncio.client.connect(uri) as websocket:
        # Send client_ready
        client_ready = Message(
            type=MessageType.CLIENT_READY,
            payload={"version": "0.1.0"}
        )
        await websocket.send(client_ready.to_json())
        
        # Expect server_ready
        response_str = await websocket.recv()
        response = Message.from_json(response_str)
        assert response.type == MessageType.SERVER_READY
        assert response.payload["version"] == "0.1.0"
        
    await server.stop()
    server_task.cancel()

@pytest.mark.asyncio
async def test_heartbeat():
    server = LuminaWSServer(host="localhost", port=8767)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    
    uri = "ws://localhost:8767"
    async with websockets.asyncio.client.connect(uri) as websocket:
        # Send heartbeat
        hb = Message(type=MessageType.HEARTBEAT)
        await websocket.send(hb.to_json())
        
        # Expect heartbeat back
        response_str = await websocket.recv()
        response = Message.from_json(response_str)
        assert response.type == MessageType.HEARTBEAT
        
    await server.stop()
    server_task.cancel()

@pytest.mark.asyncio
async def test_only_one_client():
    server = LuminaWSServer(host="localhost", port=8768)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.2)
    
    uri = "ws://localhost:8768"
    async with websockets.asyncio.client.connect(uri) as ws1:
        # Second connection should be rejected
        with pytest.raises(websockets.exceptions.InvalidStatus) as exc:
            async with websockets.asyncio.client.connect(uri) as ws2:
                pass
        assert exc.value.response.status_code == 429
        
    await server.stop()
    server_task.cancel()
