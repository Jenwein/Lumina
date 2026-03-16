import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock
from lumina.agent.llm_client import LLMClient, ChatMessage, LLMResponse, ToolDefinition
from lumina.agent.core import AgentCore
from lumina.agent.react_loop import ReActLoop


class TestAgent(unittest.IsolatedAsyncioTestCase):
    async def test_basic_chat(self):
        # Mock LLMClient
        llm_client = MagicMock(spec=LLMClient)
        llm_client.chat = AsyncMock()
        
        # Setup response
        mock_response = LLMResponse(
            message=ChatMessage(role="assistant", content="Hello! How can I help you?"),
            usage={"prompt_tokens": 10, "completion_tokens": 5},
            finish_reason="stop"
        )
        llm_client.chat.return_value = mock_response
        
        agent = AgentCore(
            llm_client=llm_client,
            system_prompt="You are a helpful assistant.",
            max_iterations=5,
            history_window=10
        )
        
        reply = await agent.process_message("Hi")
        
        self.assertEqual(reply, "Hello! How can I help you?")
        self.assertEqual(len(agent.history), 3) # System, User, Assistant
        self.assertEqual(agent.history[0].content, "You are a helpful assistant.")
        self.assertEqual(agent.history[1].content, "Hi")
        self.assertEqual(agent.history[2].content, "Hello! How can I help you?")

    async def test_react_loop_with_tools(self):
        llm_client = MagicMock(spec=LLMClient)
        llm_client.chat = AsyncMock()
        
        # 1st call: assistant wants to use a tool
        tool_call = {
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "Beijing"}'
            }
        }
        resp1 = LLMResponse(
            message=ChatMessage(role="assistant", content=None, tool_calls=[tool_call]),
            finish_reason="tool_calls"
        )
        
        # 2nd call: assistant gives final answer
        resp2 = LLMResponse(
            message=ChatMessage(role="assistant", content="Beijing is sunny today."),
            finish_reason="stop"
        )
        
        llm_client.chat.side_effect = [resp1, resp2]
        
        agent = AgentCore(
            llm_client=llm_client,
            system_prompt="You are Lumina.",
            max_iterations=5
        )
        
        # Define a mock tool
        weather_tool = ToolDefinition(
            name="get_weather",
            description="Get weather for a location",
            parameters={"type": "object", "properties": {"location": {"type": "string"}}}
        )
        
        async def weather_handler(location: str):
            return f"Weather in {location} is sunny."
            
        agent.register_tool(weather_tool, weather_handler)
        
        reply = await agent.process_message("What is the weather in Beijing?")
        
        self.assertEqual(reply, "Beijing is sunny today.")
        # History: System, User, Assistant (tool call), Tool (result), Assistant (final)
        self.assertEqual(len(agent.history), 5)
        self.assertEqual(agent.history[3].role, "tool")
        self.assertEqual(agent.history[3].content, "Weather in Beijing is sunny.")
        self.assertEqual(agent.history[3].tool_call_id, "call_123")

    def test_history_trimming(self):
        llm_client = MagicMock(spec=LLMClient)
        agent = AgentCore(
            llm_client=llm_client,
            system_prompt="System",
            history_window=2
        )
        
        # Initial: [System]
        self.assertEqual(len(agent.history), 1)
        
        # Add 3 more messages
        agent.history.append(ChatMessage(role="user", content="1"))
        agent.history.append(ChatMessage(role="assistant", content="2"))
        agent.history.append(ChatMessage(role="user", content="3"))
        
        # Trim
        agent._trim_history()
        
        # Should keep System + last 2 messages
        self.assertEqual(len(agent.history), 3)
        self.assertEqual(agent.history[0].content, "System")
        self.assertEqual(agent.history[1].content, "2")
        self.assertEqual(agent.history[2].content, "3")


if __name__ == "__main__":
    unittest.main()
