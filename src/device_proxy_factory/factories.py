"""HTTP/gRPC の既存同期・非同期クライアント対に使える補助ファクトリ。"""
from typing import Any, Callable, Optional, Type


def make_async_sync_factory(
    *,
    async_client_cls: Optional[Type[Any]] = None,
    sync_client_cls: Optional[Type[Any]] = None,
    default_async_mode: bool = True,
) -> Callable[..., Any]:
    """async_mode を解釈する creator を作成する。共通 DeviceProxy は解釈しない。"""
    if async_client_cls is None and sync_client_cls is None:
        raise ValueError("at least one client class is required")
    if async_client_cls is not None and not callable(async_client_cls):
        raise TypeError("async_client_cls must be callable")
    if sync_client_cls is not None and not callable(sync_client_cls):
        raise TypeError("sync_client_cls must be callable")

    def creator(*args: Any, async_mode: Optional[bool] = None, **kwargs: Any) -> Any:
        selected = default_async_mode if async_mode is None else async_mode
        if not isinstance(selected, bool):
            raise TypeError("async_mode must be bool or None")
        cls = async_client_cls if selected else sync_client_cls
        if cls is None:
            raise ValueError("{} client is not registered".format("async" if selected else "sync"))
        return cls(*args, **kwargs)

    return creator
