import asyncio
import logging
import sys
from lumina.config import LuminaConfig
from lumina.ws.server import LuminaWSServer
from lumina.ws.protocol import Message, MessageType

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
    
    server = LuminaWSServer(
        host=config.ws_host,
        port=config.ws_port,
        heartbeat_interval=config.heartbeat_interval,
        heartbeat_timeout=config.heartbeat_timeout
    )
    
    # Example handler to echo messages for debugging in Phase 01
    async def echo_handler(msg: Message):
        if msg.type == MessageType.USER_MESSAGE:
            logger.info(f"Received user_message: {msg.payload.get('text')}")
            # Optional echo
            # response = Message(
            #     type=MessageType.CHAT_RESPONSE,
            #     payload={"text": f"Server echo: {msg.payload.get('text')}", "streaming": False, "done": True}
            # )
            # await server.send(response)
        elif msg.type == MessageType.PET_COMMAND:
             logger.info(f"Received pet_command: {msg.payload.get('command')}")
    
    server.on_message(echo_handler)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Stopping Lumina server...")
    finally:
        await server.stop()


def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
