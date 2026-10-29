"""デバイスクラス名に基づく共通クライアントファクトリ。"""
from .core import (
    DeviceProxy, DeviceProxyEntry, create_device_proxy,
    get_device_proxy_entry, list_device_proxies,
    register_device_proxy, unregister_device_proxy,
)
from .factories import make_async_sync_factory

__all__ = [
    "DeviceProxy", "DeviceProxyEntry", "create_device_proxy",
    "get_device_proxy_entry", "list_device_proxies",
    "register_device_proxy", "unregister_device_proxy", "make_async_sync_factory",
]
