from fastapi import HTTPException


def not_implemented(feature: str) -> None:
    """骨架阶段的统一占位响应，模块开发时替换为真实实现。"""
    raise HTTPException(status_code=501, detail=f"{feature} 尚未实现")
