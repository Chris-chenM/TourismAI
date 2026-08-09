"""工具基类（为后续 Sprint 3 爬虫插件预留扩展接口）"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ToolResult:
    """工具调用结果"""
    success: bool
    data: dict | list | str
    error: str = ""


class BaseTool(ABC):
    """工具基类，后续 Sprint 3 爬虫插件将继承此接口"""

    @abstractmethod
    def name(self) -> str:
        """返回工具名称"""
        ...
