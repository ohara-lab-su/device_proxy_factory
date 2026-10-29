# デバイスパッケージ実装契約（再現用仕様）

この文書は、今後 AI アシスタントや開発者が **同じ設計原則でデバイスパッケージを実装するための契約** です。現時点の実装範囲と未完了事項を混同しないでください。

## 必ず維持する原則

1. **単一の共通 `DeviceProxy` はファクトリ**。通信抽象化層ではない。デバイスクラス名から登録済み callable を検索し、引数をそのまま渡して結果を返す。
2. **デバイスクラス名は一意**。同名登録は拒否。`(device_class, transport)` の複合キーは採用しない。
3. **各デバイスパッケージが専用クライアントを提供**。HTTP なら `AsyncCobottaClient` / `SyncCobottaClient` のような実在クラスを使用。架空の `CobottaClient` を導入しない。
4. **ファクトリに同期・非同期の選択を任せる**。HTTP/gRPC の既存ペアには `make_async_sync_factory` を使える。Tango に同じ同期・非同期選択を強制しない。
5. **デバイス固有引数を変更しない**。`config`、`api_spec`、接続先などはデバイスパッケージの仕様。共通ファクトリが解釈・補完しない。
6. **自動探索しない**。`entry_points`、インストール済みモジュール列挙、DB、ネットワーク探索を追加しない。利用者は必要なパッケージを把握し、明示的に import / 初期化する。
7. **既存利用形態を壊さない**。単独デバイスでは専用クライアントの直接生成、パッケージ固有 `DeviceProxy`、共通 `DeviceProxy` のいずれも許容。
8. **フレームワークを相互依存させない**。共通パッケージは HTTP/gRPC/Tango を import しない。通信と動的ディスパッチは各フレームワークが担当。
9. **`.pyi` とドキュメントを無視しない**。既存の専用クライアント `.pyi` を参照する共通スタブ生成器はあるが、実デバイスへの適用と型チェッカー検証は未実施。

## 実装手順

1. 既存のデバイスクラス・専用クライアントクラス・コンストラクタを**実際のソースから確認**する。
2. デバイスパッケージ内に、専用クライアントを生成する callable を定義する。既存の同期・非同期ペアなら `make_async_sync_factory` を利用してよい。
3. パッケージの明示的な import または初期化処理で `register_device_proxy("一意なクラス名", creator)` を呼ぶ。
4. 同一プロセスから異なる二つ以上のデバイスクラスを `DeviceProxy` で生成するテストを追加する。
5. 単独利用（直接生成・パッケージ固有プロキシ）が壊れていないことを確認する。
6. 通信実機テストと `.pyi` 生成テストを別途実施し、未実施ならその旨を記録する。
7. README と Pages の日本語・英語版を同時更新する。

## 禁止する典型的な設計逸脱

- `register_backend` のような通信方式レジストリを増やすこと。
- 同じデバイスクラス名を HTTP/gRPC/Tango ごとに重複登録すること。
- 共通 `DeviceProxy` に `async_mode` や `config` の意味を固定すること。
- `pip install` しただけでデバイスクラス名を自動解決できると説明すること。
- 既存の `AsyncCobottaClient` / `SyncCobottaClient` を存在しない単一クラスに置き換えること。

## 実装済み API

`register_device_proxy(device_class, creator)`、`DeviceProxy(device_class, *args, **kwargs)`、`create_device_proxy(device_class)`、`get_device_proxy_entry(device_class)`、`list_device_proxies()`、`unregister_device_proxy(device_class)`、`make_async_sync_factory(...)`。

この仕様は **共通ファクトリの現行試作に対する契約** です。既存デバイスパッケージ側の移行と実デバイス型スタブの検証は未実施です。
