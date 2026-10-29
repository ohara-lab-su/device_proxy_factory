# 仕様

## 目的と非目的

共通 `DeviceProxy` は、異なる通信フレームワークで実装された複数のデバイスクラスを、単一のクライアントプログラムで生成するためのファクトリです。通信の抽象化、デバイス探索、データベース、接続管理、動的メソッド生成は担当しません。既存のデバイス固有クライアントを置き換えません。

## 登録・生成

`register_device_proxy(device_class: str, creator: Callable)` はプロセス内の単一レジストリに登録します。空名、前後に空白がある名前、同名登録は拒否します。クラス名の一意性は**プロセス内レジストリ**で検証します。異なるプロセスやインストール済みパッケージ全体を走査して重複を調べるものではありません。

`DeviceProxy(device_class, *args, **kwargs)` は、対応する `creator(*args, **kwargs)` の結果を返します。`async_mode` も `config` もコアでは解釈しません。未登録名は `KeyError`。`get_device_proxy_entry` は登録内容を返し、`list_device_proxies` はソート済みの名前を返します。`unregister_device_proxy` は該当名を削除し、未登録の場合は `KeyError`。

`create_device_proxy(device_class)` はデバイスクラス名を固定した callable を返します。クライアントクラスの型を静的に保証する仕組みではありません。

## 同期・非同期補助ファクトリ

`make_async_sync_factory(async_client_cls=..., sync_client_cls=..., default_async_mode=True)` は任意の補助関数です。生成された callable が `async_mode=True/False/None` を解釈します。未指定 (`None`) は登録時の既定値を使用します。指定されたモードのクライアントがない場合は `ValueError` です。別モードへ黙ってフォールバックしません。Tango にこの補助ファクトリの使用を強制しません。

## 依存関係・互換性

Python >=3.7。実行時の外部依存なし。HTTP/gRPC/Tango のクライアントは、それぞれのデバイスパッケージで生成・管理します。既存フレームワークのレジストリは自動的に共有されません。
