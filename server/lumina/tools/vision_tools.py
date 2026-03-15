import asyncio
import logging
from typing import List, Optional, Dict, Any
from .base import BaseTool, RiskLevel
from ..vision.perceiver import WindowPerceiver
from ..vision.interaction import PhysicalInteraction
from ..vision.coordinates import RatioPoint
from ..ws.server import LuminaWSServer
from ..ws.protocol import Message, MessageType

logger = logging.getLogger(__name__)


class InspectWindowTool(BaseTool):
    name = "inspect_window"
    description = (
        "感知目标应用窗口的 UI 元素信息。"
        "自动激活窗口并扫描其 UI 控件和文字，返回可交互元素列表及其位置(比例坐标)。"
        "若不指定窗口则感知当前活动窗口。"
        "返回的信息包含元素名称、类型和比例坐标，可用于后续的 click_at 等操作。"
    )
    parameters = {
        "type": "object",
        "properties": {
            "window": {
                "type": "string",
                "description": "目标窗口的标题关键字或进程名，不指定则使用当前活动窗口"
            },
            "force_tier": {
                "type": "integer",
                "enum": [1, 2, 3],
                "description": "强制使用指定识别层级: 1=UIA, 2=OCR, 3=AI视觉。通常无需指定。"
            }
        },
        "required": []
    }
    risk_level = RiskLevel.LOW

    def __init__(self, perceiver: WindowPerceiver, ws_server: LuminaWSServer):
        self.perceiver = perceiver
        self.ws_server = ws_server

    async def execute(self, window: Optional[str] = None, force_tier: Optional[int] = None) -> str:
        # 通知桌宠进入观察状态
        await self.ws_server.send(Message(
            type=MessageType.PET_COMMAND,
            payload={"command": "set_state", "state": "observing"}
        ))
        
        result = await self.perceiver.inspect(target_window=window, force_tier=force_tier)
        
        # 恢复状态
        await self.ws_server.send(Message(
            type=MessageType.PET_COMMAND,
            payload={"command": "set_state", "state": "idle"}
        ))

        if not result:
            return "错误：未能识别到窗口或其内容。"
        
        return result.elements_text


class VisualLocateTool(BaseTool):
    name = "visual_locate"
    description = (
        "当 inspect_window 返回的文字信息不足以定位目标时使用。"
        "将活动窗口截图发送给 AI 进行视觉分析，定位图标、无标签按钮等非文字元素。"
        "注意: 此工具需要当前模型支持图像理解。"
    )
    parameters = {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": "要定位的元素描述，如 '设置齿轮图标'、'红色关闭按钮'"
            },
            "window": {
                "type": "string",
                "description": "目标窗口，不指定则使用当前活动窗口"
            }
        },
        "required": ["description"]
    }
    risk_level = RiskLevel.LOW

    def __init__(self, perceiver: WindowPerceiver, ws_server: LuminaWSServer):
        self.perceiver = perceiver
        self.ws_server = ws_server

    async def execute(self, description: str, window: Optional[str] = None) -> str:
        # 1. 获取窗口截图和 OCR 上下文
        # 我们先 inspect 获得当前上下文
        perception = await self.perceiver.inspect(target_window=window)
        if not perception or not perception.screenshot:
            return "错误：无法获取窗口截图进行视觉分析。"

        # 2. 调用 AI 视觉分析
        await self.ws_server.send(Message(
            type=MessageType.PET_COMMAND,
            payload={"command": "set_state", "state": "thinking"}
        ))
        
        ratio_point = await self.perceiver.ai_analyzer.locate_element(
            image=perception.screenshot,
            description=description,
            ocr_context=perception.elements_text
        )
        
        await self.ws_server.send(Message(
            type=MessageType.PET_COMMAND,
            payload={"command": "set_state", "state": "idle"}
        ))

        if not ratio_point:
            return f"AI 视觉分析未能定位到 '{description}'。请尝试更详细的描述或手动操作。"
        
        return f"成功定位到 '{description}'，比例坐标为: ({ratio_point.rx:.2f}, {ratio_point.ry:.2f})"


class ClickAtTool(BaseTool):
    name = "click_at"
    description = (
        "在活动窗口中点击指定比例位置。"
        "桌宠会跑到目标位置，播放点击动画，然后触发真实的鼠标点击。"
        "坐标为相对活动窗口的比例值 (0.0~1.0)。"
    )
    parameters = {
        "type": "object",
        "properties": {
            "rx": {"type": "number", "description": "水平比例坐标 (0.0=最左, 1.0=最右)"},
            "ry": {"type": "number", "description": "垂直比例坐标 (0.0=最上, 1.0=最下)"},
            "click_type": {
                "type": "string",
                "enum": ["single", "double", "right"],
                "description": "点击类型，默认 single"
            }
        },
        "required": ["rx", "ry"]
    }
    risk_level = RiskLevel.MEDIUM

    def __init__(self, perceiver: WindowPerceiver, interaction: PhysicalInteraction, ws_server: LuminaWSServer):
        self.perceiver = perceiver
        self.interaction = interaction
        self.ws_server = ws_server
        self._click_event = asyncio.Event()

    async def execute(self, rx: float, ry: float, click_type: str = "single") -> str:
        # 1. 获取当前活动窗口以换算坐标
        window_info = self.perceiver.window_manager.get_foreground_window()
        if not window_info:
            return "错误：找不到活动窗口，无法执行点击。"
        
        screen_pt = self.perceiver.locate_and_convert(RatioPoint(rx, ry), window_info.rect)
        
        # 2. 驱动桌宠移动并点击
        # 我们需要监听 Godot 的 click_ready 事件
        # 这里可以使用一个临时的 handler
        self._click_event.clear()
        
        async def pet_event_handler(msg: Message):
            if msg.type == MessageType.PET_EVENT:
                event = msg.payload.get("event")
                if event == "click_ready":
                    self._click_event.set()
        
        self.ws_server.on_message(pet_event_handler)
        
        try:
            # 发送指令给桌宠：移动并点击
            await self.ws_server.send(Message(
                type=MessageType.PET_COMMAND,
                payload={
                    "command": "perform_click",
                    "position": {"x": screen_pt.x, "y": screen_pt.y}
                }
            ))
            
            # 等待桌宠准备就绪 (超时设置)
            try:
                await asyncio.wait_for(self._click_event.wait(), timeout=10.0)
            except asyncio.TimeoutError:
                return f"等待桌宠到达目标超时。物理点击已取消。"
            
            # 3. 执行物理点击
            if click_type == "double":
                await self.interaction.double_click(screen_pt.x, screen_pt.y)
            elif click_type == "right":
                await self.interaction.right_click(screen_pt.x, screen_pt.y)
            else:
                await self.interaction.click(screen_pt.x, screen_pt.y)
                
            return f"成功在屏幕坐标 ({screen_pt.x}, {screen_pt.y}) 执行了 {click_type} 点击。"
        
        finally:
            # 移除 handler
            if pet_event_handler in self.ws_server._handlers:
                self.ws_server._handlers.remove(pet_event_handler)


class TypeTextTool(BaseTool):
    name = "type_text"
    description = "在当前焦点位置输入文字。通常需先用 click_at 点击目标输入框。"
    parameters = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "要输入的文字"}
        },
        "required": ["text"]
    }
    risk_level = RiskLevel.LOW

    def __init__(self, interaction: PhysicalInteraction):
        self.interaction = interaction

    async def execute(self, text: str) -> str:
        await self.interaction.type_text(text)
        return f"成功输入文本: '{text}'"


class HotkeyTool(BaseTool):
    name = "hotkey"
    description = "执行键盘快捷键组合，如 Ctrl+C、Alt+F4 等。"
    parameters = {
        "type": "object",
        "properties": {
            "keys": {
                "type": "array",
                "items": {"type": "string"},
                "description": "按键序列，如 ['ctrl', 'c']"
            }
        },
        "required": ["keys"]
    }
    risk_level = RiskLevel.MEDIUM

    def __init__(self, interaction: PhysicalInteraction):
        self.interaction = interaction

    async def execute(self, keys: List[str]) -> str:
        await self.interaction.hotkey(*keys)
        return f"成功执行快捷键: {'+'.join(keys)}"
