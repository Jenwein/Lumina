import asyncio
import logging
import sys
import os
from lumina.config import LuminaConfig, ModelConfig
from lumina.ws.server import LuminaWSServer
from lumina.ws.protocol import Message, MessageType
from lumina.agent.llm_client import LLMClient
from lumina.agent.core import AgentCore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("lumina")


async def async_main():
    config = LuminaConfig.load()
    
    # Initialize LLM Client
    active_model_config = next(
        (m for m in config.models if m.name == config.active_model), 
        None
    )
    
    if not active_model_config:
        # Fallback if no models configured or active model not found
        logger.warning(f"Active model '{config.active_model}' not found in config. Using defaults.")
        active_model_config = ModelConfig(
            name="glm-4-flash",
            api_base="https://open.bigmodel.cn/api/paas/v4/",
            api_key_env="GLM_API_KEY",
            model="glm-4-flash"
        )
    
    api_key = os.getenv(active_model_config.api_key_env)
    if not api_key:
        logger.error(f"API Key not found in environment variable: {active_model_config.api_key_env}")
        # sys.exit(1) # Don't exit, maybe it will be provided later or just fail on use
    
    llm_client = LLMClient(
        api_base=active_model_config.api_base,
        api_key=api_key or "",
        model=active_model_config.model,
        max_tokens=active_model_config.max_tokens,
        temperature=active_model_config.temperature
    )
    
    from lumina.tools import (
        ToolRegistry, ReadFileTool, WriteFileTool, DeleteFileTool,
        ListDirectoryTool, CreateDirectoryTool, MoveFileTool,
        LaunchAppTool, CloseAppTool, GetSystemInfoTool, GetRunningProcessesTool,
        AskUserTool, NotifyUserTool,
        InspectWindowTool, VisualLocateTool, ClickAtTool, TypeTextTool, HotkeyTool
    )
    from lumina.vision.window_info import WindowManager
    from lumina.vision.ui_automation import UIAutomationScanner
    from lumina.vision.capture import ScreenCapture
    from lumina.vision.ocr import OcrEngine
    from lumina.vision.ai_visual import AIVisualAnalyzer
    from lumina.vision.perceiver import WindowPerceiver
    from lumina.vision.interaction import PhysicalInteraction
    
    server = LuminaWSServer(
        host=config.ws_host,
        port=config.ws_port,
        heartbeat_interval=config.heartbeat_interval,
        heartbeat_timeout=config.heartbeat_timeout
    )

    # Initialize Vision components
    window_mgr = WindowManager()
    uia_scanner = UIAutomationScanner()
    capture = ScreenCapture()
    ocr_engine = OcrEngine()
    ai_analyzer = AIVisualAnalyzer(llm_client)
    perceiver = WindowPerceiver(window_mgr, uia_scanner, capture, ocr_engine, ai_analyzer)
    interaction = PhysicalInteraction()

    # Initialize Tool Registry
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(DeleteFileTool())
    registry.register(ListDirectoryTool())
    registry.register(CreateDirectoryTool())
    registry.register(MoveFileTool())
    registry.register(LaunchAppTool())
    registry.register(CloseAppTool())
    registry.register(GetSystemInfoTool())
    registry.register(GetRunningProcessesTool())
    registry.register(AskUserTool(server))
    registry.register(NotifyUserTool(server))
    
    # Register Vision Tools
    registry.register(InspectWindowTool(perceiver, server))
    registry.register(VisualLocateTool(perceiver, server))
    registry.register(ClickAtTool(perceiver, interaction, server))
    registry.register(TypeTextTool(interaction))
    registry.register(HotkeyTool(interaction))

    agent = AgentCore(
        llm_client=llm_client,
        system_prompt=config.agent.system_prompt,
        max_iterations=config.agent.max_react_iterations,
        history_window=config.agent.history_window
    )
    
    # Register tools to agent
    for tool in registry.tools.values():
        agent.register_tool(
            tool.to_tool_definition(),
            tool.execute
        )
    
    # Status callback for Agent
    async def on_agent_status(status: str, message: str):
        status_msg = Message(
            type=MessageType.AGENT_STATUS,
            payload={"status": status, "message": message}
        )
        await server.send(status_msg)
        
        # Also update pet state if it's thinking
        if status == "thinking":
            pet_cmd = Message(
                type=MessageType.PET_COMMAND,
                payload={"command": "set_state", "data": {"state": "thinking"}}
            )
            await server.send(pet_cmd)

    agent.set_status_callback(on_agent_status)
    
    # Message handler
    async def message_handler(msg: Message):
        if msg.type == MessageType.USER_MESSAGE:
            user_text = msg.payload.get('text')
            if not user_text:
                return
                
            logger.info(f"Processing user_message: {user_text}")
            
            # Start thinking
            await on_agent_status("thinking", "正在思考...")
            
            try:
                reply = await agent.process_message(user_text)
                
                # Send chat response
                response = Message(
                    type=MessageType.CHAT_RESPONSE,
                    payload={"text": reply, "streaming": False, "done": True}
                )
                await server.send(response)
            except Exception as e:
                logger.exception("Error processing message with agent")
                error_resp = Message(
                    type=MessageType.ERROR,
                    payload={"code": 500, "message": f"Agent error: {str(e)}"}
                )
                await server.send(error_resp)
            finally:
                # Back to idle
                pet_cmd = Message(
                    type=MessageType.PET_COMMAND,
                    payload={"command": "set_state", "data": {"state": "idle"}}
                )
                await server.send(pet_cmd)
                
        elif msg.type == MessageType.PET_COMMAND:
             logger.info(f"Received pet_command: {msg.payload.get('command')}")
    
    server.on_message(message_handler)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Stopping Lumina server...")
    except Exception as e:
        logger.exception("Server error")
    finally:
        await server.stop()


def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
