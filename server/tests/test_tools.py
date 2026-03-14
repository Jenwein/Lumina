import os
import pytest
import asyncio
import shutil
from lumina.tools import (
    ReadFileTool, WriteFileTool, DeleteFileTool,
    ListDirectoryTool, CreateDirectoryTool, MoveFileTool,
    GetSystemInfoTool, GetRunningProcessesTool,
    ToolRegistry, RiskLevel
)

@pytest.mark.asyncio
async def test_tool_registry():
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(GetSystemInfoTool())
    
    definitions = registry.list_definitions()
    assert len(definitions) == 2
    assert definitions[0].name in ["read_file", "get_system_info"]
    
    # Test execution through registry
    result = await registry.execute("get_system_info", {})
    assert "操作系统" in result
    
    # Test missing tool
    result = await registry.execute("non_existent", {})
    assert "错误" in result

@pytest.fixture
def temp_dir():
    path = "test_temp_dir"
    os.makedirs(path, exist_ok=True)
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)

@pytest.mark.asyncio
async def test_file_tools(temp_dir):
    test_file = os.path.join(temp_dir, "test.txt")
    content = "Hello, Lumina!"
    
    # Test Write
    write_tool = WriteFileTool()
    result = await write_tool.execute(path=test_file, content=content)
    assert "成功" in result
    assert os.path.exists(test_file)
    
    # Test Read
    read_tool = ReadFileTool()
    result = await read_tool.execute(path=test_file)
    assert result == content
    
    # Test List
    list_tool = ListDirectoryTool()
    result = await list_tool.execute(path=temp_dir)
    assert "test.txt" in result
    
    # Test Move/Rename
    move_tool = MoveFileTool()
    new_file = os.path.join(temp_dir, "test_moved.txt")
    result = await move_tool.execute(src=test_file, dst=new_file)
    assert "成功" in result
    assert not os.path.exists(test_file)
    assert os.path.exists(new_file)
    
    # Test Delete
    delete_tool = DeleteFileTool()
    result = await delete_tool.execute(path=new_file)
    assert "成功" in result
    assert not os.path.exists(new_file)

@pytest.mark.asyncio
async def test_directory_tools(temp_dir):
    new_dir = os.path.join(temp_dir, "subdir")
    
    # Test Create
    create_tool = CreateDirectoryTool()
    result = await create_tool.execute(path=new_dir)
    assert "成功" in result
    assert os.path.isdir(new_dir)
    
    # Test List
    list_tool = ListDirectoryTool()
    result = await list_tool.execute(path=temp_dir)
    assert "[DIR] subdir" in result
    
    # Test Delete Dir
    delete_tool = DeleteFileTool()
    result = await delete_tool.execute(path=new_dir)
    assert "成功" in result
    assert not os.path.exists(new_dir)

@pytest.mark.asyncio
async def test_system_tools():
    # Test System Info
    sys_info_tool = GetSystemInfoTool()
    result = await sys_info_tool.execute()
    assert "操作系统" in result
    assert "CPU" in result
    assert "内存" in result
    
    # Test Processes
    proc_tool = GetRunningProcessesTool()
    result = await proc_tool.execute()
    assert "当前运行的进程" in result
    # On Windows, at least some common process should be there
    assert "PID" in result

@pytest.mark.asyncio
async def test_read_non_existent():
    read_tool = ReadFileTool()
    result = await read_tool.execute(path="non_existent_file_xyz.txt")
    assert "错误" in result
