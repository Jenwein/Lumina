import os
import shutil
import aiofiles
import logging
from .base import BaseTool, RiskLevel

logger = logging.getLogger(__name__)


def is_safe_path(path: str) -> bool:
    """
    检查路径是否安全。目前简单实现为限制在用户主目录下，
    或者当前项目目录下。后续可在 config 中配置白名单。
    """
    try:
        abs_path = os.path.abspath(path)
        user_home = os.path.expanduser("~")
        current_dir = os.getcwd()
        
        # 允许在用户主目录或当前项目目录下操作
        if abs_path.startswith(user_home) or abs_path.startswith(current_dir):
            return True
        return False
    except Exception:
        return False


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "读取指定路径文件的文本内容。适用于查看配置文件、日志等。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件的绝对路径或相对路径"}
        },
        "required": ["path"]
    }
    risk_level = RiskLevel.LOW

    async def execute(self, path: str) -> str:
        if not is_safe_path(path):
            return f"错误：路径 '{path}' 超出安全沙箱范围，拒绝访问。"
        try:
            async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                return content
        except FileNotFoundError:
            return f"错误：未找到文件 '{path}'"
        except UnicodeDecodeError:
            return f"错误：文件 '{path}' 不是有效的 UTF-8 文本文件"
        except Exception as e:
            return f"错误：读取文件 '{path}' 时发生异常：{str(e)}"


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "将内容写入指定文件。如果文件不存在则创建，存在则覆盖。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "目标文件路径"},
            "content": {"type": "string", "description": "要写入的文本内容"}
        },
        "required": ["path", "content"]
    }
    risk_level = RiskLevel.MEDIUM

    async def execute(self, path: str, content: str) -> str:
        if not is_safe_path(path):
            return f"错误：路径 '{path}' 超出安全沙箱范围，拒绝访问。"
        try:
            # 确保父目录存在
            parent_dir = os.path.dirname(os.path.abspath(path))
            os.makedirs(parent_dir, exist_ok=True)
            async with aiofiles.open(path, mode='w', encoding='utf-8') as f:
                await f.write(content)
                return f"成功写入文件 '{path}'"
        except Exception as e:
            return f"错误：写入文件 '{path}' 时发生异常：{str(e)}"


class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = "列出指定目录下的文件和子目录。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "目录路径，默认为当前目录", "default": "."}
        }
    }
    risk_level = RiskLevel.LOW

    async def execute(self, path: str = ".") -> str:
        if not is_safe_path(path):
            return f"错误：路径 '{path}' 超出安全沙箱范围，拒绝访问。"
        try:
            items = os.listdir(path)
            if not items:
                return f"目录 '{path}' 为空"
            
            result = [f"目录 '{path}' 中的内容："]
            for item in items:
                full_path = os.path.join(path, item)
                type_str = "[DIR]" if os.path.isdir(full_path) else "[FILE]"
                result.append(f"{type_str} {item}")
            
            return "\n".join(result)
        except FileNotFoundError:
            return f"错误：未找到目录 '{path}'"
        except Exception as e:
            return f"错误：列出目录 '{path}' 时发生异常：{str(e)}"


class CreateDirectoryTool(BaseTool):
    name = "create_directory"
    description = "创建目录，支持递归创建中间目录。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "目录路径"}
        },
        "required": ["path"]
    }
    risk_level = RiskLevel.LOW

    async def execute(self, path: str) -> str:
        if not is_safe_path(path):
            return f"错误：路径 '{path}' 超出安全沙箱范围，拒绝访问。"
        try:
            os.makedirs(path, exist_ok=True)
            return f"成功创建目录 '{path}'"
        except Exception as e:
            return f"错误：创建目录 '{path}' 时发生异常：{str(e)}"


class DeleteFileTool(BaseTool):
    name = "delete_file"
    description = "永久删除指定路径的文件或文件夹。此操作不可撤销。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "要删除的文件或目录路径"}
        },
        "required": ["path"]
    }
    risk_level = RiskLevel.HIGH

    async def execute(self, path: str) -> str:
        if not is_safe_path(path):
            return f"错误：路径 '{path}' 超出安全沙箱范围，拒绝访问。"
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                return f"成功删除目录 '{path}'"
            elif os.path.isfile(path):
                os.remove(path)
                return f"成功删除文件 '{path}'"
            else:
                return f"错误：未找到目标 '{path}'"
        except Exception as e:
            return f"错误：删除 '{path}' 时发生异常：{str(e)}"


class MoveFileTool(BaseTool):
    name = "move_file"
    description = "移动或重命名文件/目录。"
    parameters = {
        "type": "object",
        "properties": {
            "src": {"type": "string", "description": "源文件/目录路径"},
            "dst": {"type": "string", "description": "目标路径"}
        },
        "required": ["src", "dst"]
    }
    risk_level = RiskLevel.MEDIUM

    async def execute(self, src: str, dst: str) -> str:
        if not is_safe_path(src) or not is_safe_path(dst):
            return f"错误：路径超出安全沙箱范围，拒绝访问。"
        try:
            # 确保目标父目录存在
            parent_dir = os.path.dirname(os.path.abspath(dst))
            os.makedirs(parent_dir, exist_ok=True)
            shutil.move(src, dst)
            return f"成功将 '{src}' 移动/重命名为 '{dst}'"
        except FileNotFoundError:
            return f"错误：未找到源文件/目录 '{src}'"
        except Exception as e:
            return f"错误：移动文件时发生异常：{str(e)}"
