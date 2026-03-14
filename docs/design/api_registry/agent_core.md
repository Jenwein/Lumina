# API Registry — Agent 决策引擎

> 本文档记录 Agent 决策引擎的核心接口，包括 LLM 客户端、ReAct 循环和 Agent 核心。

| Interface | File Path | Origin Phase (Link) | Usage Note |
|-----------|-----------|---------------------|------------|
| `ChatMessage` | `server/lumina/agent/llm_client.py` | [Phase 03](../phases/phase_03_agent_engine.md) | 对话消息数据类。`role` 取值: system/user/assistant/tool |
| `ToolDefinition` | `server/lumina/agent/llm_client.py` | [Phase 03](../phases/phase_03_agent_engine.md) | 工具定义（name + description + JSON Schema parameters） |
| `LLMResponse` | `server/lumina/agent/llm_client.py` | [Phase 03](../phases/phase_03_agent_engine.md) | LLM 响应封装，含 finish_reason 和 usage 信息 |
| `LLMClient` | `server/lumina/agent/llm_client.py` | [Phase 03](../phases/phase_03_agent_engine.md) | OpenAI 兼容 API 客户端。`chat()` 方法支持 Function Calling |
| `ReActLoop` | `server/lumina/agent/react_loop.py` | [Phase 03](../phases/phase_03_agent_engine.md) | 单次请求的推理循环。`run()` 执行直到最终回复或达到 max_iterations |
| `AgentCore` | `server/lumina/agent/core.py` | [Phase 03](../phases/phase_03_agent_engine.md) | 顶层 Agent 入口。`process_message()` 是主调用点 |
| `AgentCore.register_tool` | `server/lumina/agent/core.py` | [Phase 03](../phases/phase_03_agent_engine.md) | 注册工具供 ReAct 循环使用。需传入 ToolDefinition + async handler |
| `AgentCore.set_system_prompt` | `server/lumina/agent/core.py` | [Phase 03](../phases/phase_03_agent_engine.md) | 运行时更新角色人设/系统提示词 |
| `ModelConfig` | `server/lumina/config.py` | [Phase 03](../phases/phase_03_agent_engine.md) | 模型配置（api_base, api_key_env, model, max_tokens, temperature） |
| `AgentConfig` | `server/lumina/config.py` | [Phase 03](../phases/phase_03_agent_engine.md) | Agent 配置（system_prompt, max_react_iterations, history_window） |

## 调用模式

```
# 典型使用流程
llm_client = LLMClient(api_base=..., api_key=..., model=...)
agent = AgentCore(llm_client, system_prompt="你是 Lumina...")

# 注册工具 (Phase 04+)
agent.register_tool(tool.to_tool_definition(), tool.execute)

# 处理用户消息
reply = await agent.process_message("帮我列出桌面文件")
```

## LLM 兼容性

使用 OpenAI Chat Completions 格式，已验证兼容：

| 提供商 | 模型 | api_base |
|--------|------|----------|
| 智谱 AI | glm-4-flash | `https://open.bigmodel.cn/api/paas/v4/` |
| OpenAI | gpt-4 | `https://api.openai.com/v1/` |
| DeepSeek | deepseek-chat | `https://api.deepseek.com/v1/` |
| Ollama (本地) | 任意 | `http://localhost:11434/v1/` |
