import asyncio
import json
import logging
from lumina.ws.server import LuminaWSServer
from lumina.ws.protocol import Message, MessageType

# Configure logging to see server activity
logging.basicConfig(level=logging.INFO)

async def manual_test():
    # Use default port 8765, explicitly on 127.0.0.1
    server = LuminaWSServer(host="127.0.0.1", port=8765)
    
    async def handler(msg: Message):
        print(f"Server RECEIVED: {msg.type} - {msg.payload}")
        
    server.on_message(handler)
    
    print("Starting server on ws://127.0.0.1:8765...")
    server_task = asyncio.create_task(server.start())
    
    # Wait for client to connect
    print("Waiting for Godot client to connect...")
    while server._connection is None:
        await asyncio.sleep(0.5)
    
    print(f"Godot client connected from {server._connection.remote_address}!")
    
    # Wait for handshake (client sends client_ready, server sends server_ready)
    await asyncio.sleep(2)
    
    # Test 1: move_to (100, 100)
    print("Sending move_to(100, 100)...")
    move_msg = Message(
        type=MessageType.PET_COMMAND,
        payload={
            "command": "move_to",
            "data": {"x": 100, "y": 100, "speed": 150}
        }
    )
    await server.send(move_msg)
    
    await asyncio.sleep(5)
    
    # Test 2: set_state "thinking"
    print("Sending set_state('thinking')...")
    think_msg = Message(
        type=MessageType.PET_COMMAND,
        payload={
            "command": "set_state",
            "data": {"state": "thinking"}
        }
    )
    await server.send(think_msg)
    
    await asyncio.sleep(3)
    
    # Test 3: move_to (250, 150)
    print("Sending move_to(250, 150)...")
    move_msg2 = Message(
        type=MessageType.PET_COMMAND,
        payload={
            "command": "move_to",
            "data": {"x": 250, "y": 150, "speed": 100}
        }
    )
    await server.send(move_msg2)
    
    await asyncio.sleep(5)
    
    # Test 4: quit
    print("Sending quit command...")
    quit_msg = Message(
        type=MessageType.PET_COMMAND,
        payload={"command": "quit"}
    )
    await server.send(quit_msg)
    
    await asyncio.sleep(2)
    
    print("Test complete. Stopping server...")
    await server.stop()
    await server_task

if __name__ == "__main__":
    asyncio.run(manual_test())
