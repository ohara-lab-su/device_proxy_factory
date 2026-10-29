# device-proxy-factory

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/device-proxy-factory/en/index.html) [![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://ohara-lab-su.github.io/device-proxy-factory/ja/index.html)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fdevice--proxy--factory-181717?logo=github)](https://github.com/ohara-lab-su/device-proxy-factory/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/device-proxy-factory/ja/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/index.html)

[日本語](README.md) | [English](README.en.md)

デバイスクラス名から、登録済みのクライアント生成処理（ファクトリ）を呼び出す小さな Python パッケージです。HTTP (`ese774_frame`)、gRPC (`grpc_frame`)、Tango (`tango_frame`) の**通信を抽象化しません**。それぞれのデバイスパッケージが提供するクライアントを、単一の `DeviceProxy` から生成することが目的です。

**状態:** 0.2.0 試作実装。既存フレームワークのコードは変更していません。配布名は仮称です。実機接続テストは未実施です。

## インストール

リポジトリのルートで `python -m pip install .` を実行してください。開発時は `python -m pip install -e .` を使用できます。Python 3.7 以降が必要です。共通パッケージ自体は HTTP/gRPC/Tango を依存関係に持ちません。必要な通信フレームワークとデバイスパッケージは、用途に応じて別途インストールしてください。`pip install` だけでデバイスを自動発見・登録することはありません。

## 基本仕様

- レジストリのキーは一意のデバイスクラス名（文字列）。同名の再登録は `ValueError`。
- 値は callable (`creator`)。クライアントクラス自体も登録可能。
- `DeviceProxy(device_class, *args, **kwargs)` は `creator(*args, **kwargs)` を呼ぶだけ。通信方式、`async_mode`、`config`、`api_spec` を解釈しません。
- `make_async_sync_factory` は HTTP/gRPC などの同期・非同期クライアント対を扱う**任意の補助関数**。`async_mode` はこの補助ファクトリが処理します。
- デバイスの自動探索、`entry_points`、DB、通信プロトコル切替はありません。
- 単独デバイスの場合は専用クライアントの直接生成、デバイスパッケージ内の `DeviceProxy`、共通 `DeviceProxy` のいずれも選べます。

## 使い方：デバイスパッケージ側

デバイスパッケージの `__init__.py` 等、利用者が明示的にインポートする場所で登録します。以下のクラス名は説明用です。実在する COBOTTA クライアントは `AsyncCobottaClient` / `SyncCobottaClient` です。

```python
from device_proxy_factory import register_device_proxy, make_async_sync_factory
from .clients import AsyncCobottaClient, SyncCobottaClient

register_device_proxy(
    "CobottaCtrl",
    make_async_sync_factory(
        async_client_cls=AsyncCobottaClient,
        sync_client_cls=SyncCobottaClient,
        default_async_mode=True,
    ),
)
```

Tango のように単一の専用クライアントクラスを生成する場合は、クラスを直接登録できます。

```python
from device_proxy_factory import register_device_proxy
from .device_client import DeviceClient

register_device_proxy("TangoDevice", DeviceClient)
```

同一プロセス内で同じクラス名を二重登録すると例外になります。パッケージのインポート時登録は一例であり、初期化関数から明示登録する構成も可能です。

## 使い方：利用者側

```python
from device_proxy_factory import DeviceProxy
import cobotta_device  # 利用するパッケージが共通レジストリに登録
import tango_device

cobotta = DeviceProxy("CobottaCtrl", server_ip="127.0.0.1", async_mode=False)
tango = DeviceProxy("TangoDevice", "tango://127.0.0.1:10000/test/tango/device#dbase=no")
```

上記の `cobotta_device` / `tango_device` はパッケージ配置を説明する**仮の import 名**です。実際の import パスとコンストラクタ引数は各デバイスパッケージの仕様に従ってください。共通ファクトリは引数を変更しません。`async_mode` は登録された creator が受け付ける場合のみ利用できます。

## 公開 API

`DeviceProxy`、`DeviceProxyEntry`、`register_device_proxy`、`unregister_device_proxy`、`get_device_proxy_entry`、`list_device_proxies`、`create_device_proxy`、`make_async_sync_factory`。

## テスト

`python -m pip install pytest` の後、`python -m pytest -q`。実機不要のユニットテストを含みます。

## Pages ドキュメント

`docs/ja/`（日本語）と `docs/en/`（英語）に、仕様、How-to、制約、デバイスパッケージ実装者向けの再現可能な設計契約を収録しています。`docs/` は Sphinx + MyST + Read the Docs theme による日英共通構成です。`bash docs/build.sh` で `/`（英語）、`/en/`、`/ja/` を生成します。GitHub Actions は `.github/workflows/pages.yml` を使用します。

## 注意事項

既存の `ese774_frame` / `grpc_frame` の `DeviceProxy` は、それぞれ固有のレジストリを持ちます。このパッケージをインストールしても既存レジストリは自動統合されません。既存パッケージ側で共通レジストリへの登録を明示的に追加する必要があります。専用クライアント型を参照する共通スタブ生成機能は追加済みですが、実在するデバイスパッケージへの適用・型チェッカーによる検証は未実施です。詳細は `docs/ja/limitations.md` を参照してください。

ライセンス: Apache-2.0（既存コードを流用せず新規作成した試作。正式公開前に組織の著作権・配布条件を確認してください）。

## 専用クライアントの .pyi を共通 DeviceProxy で利用する（0.2.0）

**型情報の正本は各デバイスパッケージの専用クライアントクラスの `.pyi` です。** `ese774_frame` / `grpc_frame` で生成した専用クライアントの型情報（クライアント側の追加・オーバーライドを含む）を使い、共通 `DeviceProxy` はデバイス名に応じてそのクラスを戻り型として宣言します。汎用ベースクライアントの `.pyi` には置き換えません。

デバイス追加時は、`examples/device-types.example.json` を参考に、実際の専用クライアントの完全修飾名を `examples/device-types.json` に記述し、次を実行します。**同梱 JSON のクラス名は説明用であり、実在するパッケージではありません。**

```bash
python -m device_proxy_factory.typing_generator \
    examples/device-types.json src/device_proxy_factory/core.pyi
python -m pip install -e .
```

生成される `core.pyi` は各デバイスの専用クライアントを import して参照します。型補完の環境には該当デバイスパッケージが必要です。共通ファクトリは実行時にそれらを import しません。**インストール済みの共通パッケージの `.pyi` が自動更新されるわけではありません。** デバイス追加時に対応 JSON を更新し、共通パッケージのスタブを再生成・再インストールする手順です。型情報の登録と、実行時 `register_device_proxy()` による登録は別です。

再設計や新規デバイスパッケージ作成時は、AI 向け規範仕様 [`AGENTS.md`](AGENTS.md) と [`docs/ja/agent-contract.md`](docs/ja/agent-contract.md) を必ず参照してください。ここには `DeviceClass` 名の一意性、専用クライアント、登録方法、型情報、禁止事項、検証手順をまとめています。
