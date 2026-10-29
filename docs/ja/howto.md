# How-to

## インストールと確認

```bash
python -m pip install .
python -m pip install pytest
python -m pytest -q
python examples/multiple_devices.py
```

## デバイスパッケージでの登録

HTTP/gRPC の同期・非同期クライアント対は次のように登録します。

```python
from device_proxy_factory import register_device_proxy, make_async_sync_factory

register_device_proxy("CobottaCtrl", make_async_sync_factory(
    async_client_cls=AsyncCobottaClient,
    sync_client_cls=SyncCobottaClient,
    default_async_mode=True,
))
```

この例の `AsyncCobottaClient` / `SyncCobottaClient` は、デバイスパッケージ内で定義された実クラスを import してください。共通モジュールはこれらを import しません。

Tango テスト実装のように `DeviceClient` が一つなら、`register_device_proxy("TangoDevice", DeviceClient)` とします。

## 一つのプログラムで複数のデバイス

利用者は**自分が使用するデバイスパッケージを明示的に import** します。登録処理はデバイスパッケージが実行します。`DeviceProxy("CobottaCtrl", ..., async_mode=False)` と `DeviceProxy("TangoDevice", ...)` は同じ共通モジュールから呼べます。`...` の引数は各デバイスのコンストラクタ仕様に合わせてください。

## 単独デバイス

専用クライアントクラスの直接利用、デバイスパッケージ固有の `DeviceProxy`、共通 `DeviceProxy` のいずれも可能です。共通化は強制ではありません。

## ドキュメント生成

```bash
python -m pip install sphinx myst-parser sphinx-rtd-theme linkify-it-py
bash docs/build.sh
```

## 専用クライアント型を共通 DeviceProxy に反映する

既存の専用クライアント `.pyi` を正本として維持し、デバイスクラス名と完全修飾クライアント型を `examples/device-types.example.json` の形式で列挙する。`python -m device_proxy_factory.typing_generator examples/device-types.json src/device_proxy_factory/core.pyi` を実行する。実行時の登録は別途必要。生成された `core.pyi` は共通パッケージのビルド時に同梱する。/ Keep dedicated client `.pyi` authoritative, explicitly map device names to qualified classes in JSON, and generate the shared `core.pyi`. Runtime registration is separate.
