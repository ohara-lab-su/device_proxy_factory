"""通信方式に依存しない、デバイスクラス名からのクライアント生成ファクトリ。"""
from typing import Any, Callable, Dict, List, NamedTuple


class DeviceProxyEntry(NamedTuple):
    device_class: str
    creator: Callable[..., Any]


_REGISTRY: Dict[str, DeviceProxyEntry] = {}


def register_device_proxy(device_class: str, creator: Callable[..., Any]) -> None:
    """クラス名と生成処理を登録する。同名の再登録は許可しない。"""
    if not isinstance(device_class, str) or not device_class.strip() or device_class != device_class.strip():
        raise ValueError("device_class must be a nonempty, trimmed string")
    if not callable(creator):
        raise TypeError("creator must be callable")
    if device_class in _REGISTRY:
        raise ValueError("device class already registered: {}".format(device_class))
    _REGISTRY[device_class] = DeviceProxyEntry(device_class, creator)


def unregister_device_proxy(device_class: str) -> None:
    """登録を解除する。未登録の場合は KeyError。"""
    del _REGISTRY[device_class]


def get_device_proxy_entry(device_class: str) -> DeviceProxyEntry:
    """登録情報を取得する。未登録の場合は KeyError。"""
    return _REGISTRY[device_class]


def list_device_proxies() -> List[str]:
    """登録済みのデバイスクラス名を辞書順で返す。"""
    return sorted(_REGISTRY)


def DeviceProxy(device_class: str, *args: Any, **kwargs: Any) -> Any:
    """登録済み creator を呼び出す。引数は一切解釈せず転送する。"""
    return get_device_proxy_entry(device_class).creator(*args, **kwargs)


def create_device_proxy(device_class: str) -> Callable[..., Any]:
    """デバイスクラス名を固定したローカルファクトリを返す。"""
    def proxy(*args: Any, **kwargs: Any) -> Any:
        return DeviceProxy(device_class, *args, **kwargs)
    return proxy
