import platform
import psutil
import logging
from typing import Optional
from .base import BaseTool, RiskLevel

logger = logging.getLogger(__name__)


class GetSystemInfoTool(BaseTool):
    name = "get_system_info"
    description = "获取当前系统信息，包括操作系统、CPU、内存、磁盘等。"
    parameters = {
        "type": "object",
        "properties": {}
    }
    risk_level = RiskLevel.LOW

    async def execute(self) -> str:
        try:
            # 操作系统信息
            os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
            
            # CPU 信息
            cpu_count = psutil.cpu_count(logical=False)
            logical_cpu_count = psutil.cpu_count(logical=True)
            cpu_usage = psutil.cpu_percent(interval=0.1)
            
            # 内存信息
            mem = psutil.virtual_memory()
            mem_total = mem.total / (1024**3)
            mem_available = mem.available / (1024**3)
            mem_usage = mem.percent
            
            # 磁盘信息
            disk = psutil.disk_usage('/')
            disk_total = disk.total / (1024**3)
            disk_free = disk.free / (1024**3)
            disk_usage = disk.percent
            
            result = [
                "### 当前系统状态 ###",
                f"操作系统: {os_info}",
                f"CPU: {cpu_count} 核心 ({logical_cpu_count} 线程), 使用率: {cpu_usage}%",
                f"内存: 总计 {mem_total:.1f}GB, 可用 {mem_available:.1f}GB, 使用率: {mem_usage}%",
                f"磁盘 (/): 总计 {disk_total:.1f}GB, 剩余 {disk_free:.1f}GB, 使用率: {disk_usage}%"
            ]
            
            return "\n".join(result)
        except Exception as e:
            return f"错误：获取系统信息时发生异常：{str(e)}"


class GetRunningProcessesTool(BaseTool):
    name = "get_running_processes"
    description = "获取当前运行的前 20 个进程列表（按内存占用排序），可选按名称过滤。"
    parameters = {
        "type": "object",
        "properties": {
            "filter": {"type": "string", "description": "按名称过滤进程", "default": None}
        }
    }
    risk_level = RiskLevel.LOW

    async def execute(self, filter: Optional[str] = None) -> str:
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    name = proc.info['name']
                    if filter and filter.lower() not in name.lower():
                        continue
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # 按内存占用排序
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            # 限制数量，防止输出过大
            limit = 20
            top_processes = processes[:limit]
            
            if not top_processes:
                return "未找到匹配的进程。"
            
            result = [f"当前运行的进程 (前 {len(top_processes)} 个，按内存排序)："]
            for p in top_processes:
                result.append(f"PID: {p['pid']}, Name: {p['name']}, Memory: {p['memory_percent']:.1f}%")
            
            if len(processes) > limit:
                result.append(f"... 还有 {len(processes) - limit} 个进程未列出。")
            
            return "\n".join(result)
        except Exception as e:
            return f"错误：获取进程列表时发生异常：{str(e)}"
