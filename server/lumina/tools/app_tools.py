import asyncio
import psutil
import logging
from typing import List, Optional
from .base import BaseTool, RiskLevel

logger = logging.getLogger(__name__)


class LaunchAppTool(BaseTool):
    name = "launch_app"
    description = "启动一个应用程序或执行一个命令。"
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "要启动的可执行文件路径或命令"},
            "args": {"type": "array", "items": {"type": "string"}, "description": "传递给程序的参数列表", "default": []}
        },
        "required": ["command"]
    }
    risk_level = RiskLevel.MEDIUM

    async def execute(self, command: str, args: Optional[List[str]] = None) -> str:
        try:
            if args is None:
                args = []
            
            # 使用 asyncio.create_subprocess_exec 启动进程
            # 注意：在 Windows 上，如果是 shell 命令，可能需要使用 create_subprocess_shell
            process = await asyncio.create_subprocess_exec(
                command,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            return f"成功启动应用 '{command}'，PID: {process.pid}"
        except FileNotFoundError:
            # 尝试作为 shell 命令执行
            try:
                full_command = f"{command} {' '.join(args) if args else ''}"
                process = await asyncio.create_subprocess_shell(
                    full_command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                return f"已通过 Shell 启动命令 '{full_command}'，PID: {process.pid}"
            except Exception as e:
                return f"错误：无法启动应用 '{command}'：{str(e)}"
        except Exception as e:
            return f"错误：启动应用时发生异常：{str(e)}"


class CloseAppTool(BaseTool):
    name = "close_app"
    description = "关闭指定名称的应用程序进程。"
    parameters = {
        "type": "object",
        "properties": {
            "process_name": {"type": "string", "description": "要关闭的进程名称（如 notepad.exe）"}
        },
        "required": ["process_name"]
    }
    risk_level = RiskLevel.MEDIUM

    async def execute(self, process_name: str) -> str:
        try:
            count = 0
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                    proc.terminate()
                    count += 1
            
            if count > 0:
                return f"成功关闭了 {count} 个名为 '{process_name}' 的进程"
            else:
                return f"未找到名为 '{process_name}' 的运行中进程"
        except Exception as e:
            return f"错误：关闭应用 '{process_name}' 时发生异常：{str(e)}"
