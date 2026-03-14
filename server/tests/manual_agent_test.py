import asyncio
import os
import logging
from lumina.agent.llm_client import LLMClient, ChatMessage
from lumina.agent.core import AgentCore

logging.basicConfig(level=logging.INFO)

async def test_real_llm():
    # Read API key from file if not in env
    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        api_key = "7be31b820c0c4e8ead1d57540c0b3bf9.jCzmWck280apjW49"
    
    llm_client = LLMClient(
        api_base="https://open.bigmodel.cn/api/paas/v4/",
        api_key=api_key,
        model="glm-4-flash"
    )
    
    agent = AgentCore(
        llm_client=llm_client,
        system_prompt="你是一个可爱的桌宠助手，名叫 Lumina。说话要俏皮一点，多用表情符号。"
    )
    
    from lumina.agent.llm_client import ToolDefinition
    
    # 注册一个模拟工具
    time_tool = ToolDefinition(
        name="get_current_time",
        description="获取当前系统时间",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
    
    async def time_handler():
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[Tool Execution] get_current_time invoked. Result: {now}")
        return f"当前系统时间是：{now}"
    
    agent.register_tool(time_tool, time_handler)
    
    # 测试工具调用流程
    print("\nUser: 现在几点了？")
    reply = await agent.process_message("现在几点了？")
    print(f"Lumina: {reply}")

if __name__ == "__main__":
    asyncio.run(test_real_llm())
