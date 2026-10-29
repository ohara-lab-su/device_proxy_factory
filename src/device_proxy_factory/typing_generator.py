"""明示的なデバイス型対応表から共通 DeviceProxy のスタブを生成する。

実行時レジストリや通信フレームワークには依存しない。
"""
import argparse
import json
import keyword
from pathlib import Path


def _identifier(value):
    return isinstance(value, str) and value.isidentifier() and not keyword.iskeyword(value)


def _qualified_class(value):
    if not isinstance(value, str) or "." not in value:
        raise ValueError("クライアント型は 'package.module.ClassName' 形式で指定してください")
    module, cls = value.rsplit(".", 1)
    if not all(_identifier(part) for part in module.split(".")) or not _identifier(cls):
        raise ValueError("クライアント型のモジュール名またはクラス名が不正です: " + value)
    return module, cls


def generate_device_proxy_pyi(devices, output):
    """デバイス名→専用クライアント型の対応を含む core.pyi を生成する。

    devices は明示的な辞書の配列。専用クライアントの .pyi はコピーしない。
    """
    if not isinstance(devices, list):
        raise ValueError("devices は配列で指定してください")
    names = set()
    imports = []
    definitions = []
    for device in devices:
        if not isinstance(device, dict):
            raise ValueError("各デバイスは辞書で指定してください")
        name = device.get("device_class")
        if not isinstance(name, str) or not name.strip() or name != name.strip() or name in names:
            raise ValueError("デバイスクラス名が不正または重複しています: {!r}".format(name))
        names.add(name)
        single = device.get("client")
        async_cls = device.get("async_client")
        sync_cls = device.get("sync_client")
        if (single is None) == (async_cls is None and sync_cls is None):
            raise ValueError("{}: client または async_client/sync_client を指定してください".format(name))
        key = repr(name)
        if single is not None:
            module, cls = _qualified_class(single)
            alias = "_Client_{}".format(len(imports))
            imports.append("from {} import {} as {}".format(module, cls, alias))
            definitions.append("@overload\ndef DeviceProxy(device_class: Literal[{}], *args: Any, **kwargs: Any) -> {}: ...".format(key, alias))
        else:
            default = device.get("default_async_mode", True)
            if not isinstance(default, bool):
                raise ValueError("default_async_mode は bool で指定してください")
            aliases = {}
            for mode, qualified in ((True, async_cls), (False, sync_cls)):
                if qualified is None:
                    continue
                module, cls = _qualified_class(qualified)
                alias = "_Client_{}".format(len(imports))
                imports.append("from {} import {} as {}".format(module, cls, alias))
                aliases[mode] = alias
                definitions.append("@overload\ndef DeviceProxy(device_class: Literal[{}], *args: Any, async_mode: Literal[{}], **kwargs: Any) -> {}: ...".format(key, mode, alias))
            if default in aliases:
                definitions.append("@overload\ndef DeviceProxy(device_class: Literal[{}], *args: Any, async_mode: None = None, **kwargs: Any) -> {}: ...".format(key, aliases[default]))
    lines = [
        '"""生成ファイル。専用クライアント型は各デバイスパッケージの .pyi に従う。"""',
        "from typing import Any, Callable, List, NamedTuple, Dict",
        "from typing_extensions import Literal, overload",
        *imports,
        "",
        "class DeviceProxyEntry(NamedTuple):",
        "    device_class: str",
        "    creator: Callable[..., Any]",
        "",
        "def register_device_proxy(device_class: str, creator: Callable[..., Any]) -> None: ...",
        "def unregister_device_proxy(device_class: str) -> None: ...",
        "def get_device_proxy_entry(device_class: str) -> DeviceProxyEntry: ...",
        "def list_device_proxies() -> List[str]: ...",
        "",
        *definitions,
        "@overload" if definitions else "",
        "def DeviceProxy(device_class: str, *args: Any, **kwargs: Any) -> Any: ...",
        "def create_device_proxy(device_class: str) -> Callable[..., Any]: ...",
        "",
    ]
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser(description="共通 DeviceProxy の型定義を生成")
    parser.add_argument("manifest", help="明示的なデバイス型対応 JSON")
    parser.add_argument("output", help="生成先 core.pyi")
    args = parser.parse_args()
    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    generate_device_proxy_pyi(data["devices"], args.output)


if __name__ == "__main__":
    main()
