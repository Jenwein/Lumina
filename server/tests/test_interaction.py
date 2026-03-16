import pytest
import asyncio
from lumina.ws.protocol import Message, MessageType
from lumina.ws.server import LuminaWSServer
from lumina.tools.interaction_tools import AskUserTool, NotifyUserTool

class MockWebsocket:
    def __init__(self):
        self.sent_messages = []
        self.closed = False
        self.remote_address = ("127.0.0.1", 12345)

    async def send(self, message):
        self.sent_messages.append(message)

    async def close(self, code=1000, reason=""):
        self.closed = True

    def __aiter__(self):
        return self

    async def __anext__(self):
        await asyncio.sleep(10) # Wait forever
        raise StopAsyncIteration

@pytest.mark.asyncio
async def test_server_request_response():
    server = LuminaWSServer()
    ws = MockWebsocket()
    server._connection = ws
    
    # Simulate a request
    req_msg = Message(type=MessageType.USER_PROMPT, payload={"question": "What is your name?"})
    
    # Start the request in a task
    request_task = asyncio.create_task(server.request(req_msg, timeout=1.0))
    
    # Wait a bit for the message to be "sent"
    await asyncio.sleep(0.1)
    assert len(ws.sent_messages) == 1
    
    # Simulate a response from the client
    resp_msg = Message(
        type=MessageType.USER_PROMPT_RESPONSE, 
        payload={"answer": "Lumina User", "reply_to": req_msg.id}
    )
    
    # Manually trigger response handling (since we are not running the full server loop)
    # Actually, let's mock the message processing
    await server._handle_response(resp_msg)
    
    result = await request_task
    assert result.payload["answer"] == "Lumina User"

# We need to add _handle_response or similar logic to server.py to make testing easier 
# OR use the internal state.

@pytest.mark.asyncio
async def test_interaction_tools():
    server = LuminaWSServer()
    ws = MockWebsocket()
    server._connection = ws
    
    ask_tool = AskUserTool(server)
    notify_tool = NotifyUserTool(server)
    
    # Test Notify
    await notify_tool.execute("Hello!")
    assert len(ws.sent_messages) == 1
    msg = Message.from_json(ws.sent_messages[0])
    assert msg.type == MessageType.PET_COMMAND
    assert msg.payload["command"] == "show_bubble"
    
    # Test Ask
    # Mocking request to avoid timeout
    async def mock_request(msg, timeout=120):
        return Message(type=MessageType.USER_PROMPT_RESPONSE, payload={"answer": "Fine", "reply_to": msg.id})
    
    server.request = mock_request
    answer = await ask_tool.execute("How are you?")
    assert answer == "Fine"
