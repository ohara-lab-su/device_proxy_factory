# 実装・再設計担当 AI 向け仕様（必読）

この文書は説明用 README ではなく、将来の変更時に既存合意を再現するための**拘束条件と確認手順**である。推測で設計を変更しない。日本語版の正本は `docs/ja/agent-contract.md`、英語版は `docs/en/agent-contract.md`。

## 目的と変更禁止条件

- **単一の共通 `DeviceProxy` は、デバイスクラス名から登録済み `creator` を呼び出すファクトリ**。通信方式の抽象化、デバイスの共通インターフェイス、RPC の統一、サーバー探索ではない。
- デバイスクラス名はプロセス内で一意。重複登録はエラー。同名クラスを transport 名で区別しない。
- HTTP (`ese774_frame`)、gRPC (`grpc_frame`)、Tango (`tango_frame`) は独立。共通モジュールはそれらを import しない。
- **各デバイスパッケージの専用クライアントクラスが型情報の正本**。汎用ベースクライアントの `.pyi` で代用しない。継承・追加・オーバーライドされたメソッドの署名は専用クライアント `.pyi` に従う。
- HTTP/gRPC の同期・非同期選択は登録された `creator` の責務。共通 `DeviceProxy` は `async_mode` を解釈せず `**kwargs` を転送する。Tango に async/sync ペアを強制しない。
- `config`、`api_spec`、接続引数はデバイス・フレームワーク固有。共通側は解析しない。
- 自動探索、entry_points、ネットワーク探索、デバイス DB を導入しない。登録は明示的な Python 実行による。
- 直接クライアント利用、デバイスパッケージ固有の `DeviceProxy`、共通 `DeviceProxy` のいずれも妨げない。
- 将来 DDS/MQTT を想定して RPC 型 API や `async_mode` を共通仕様にしない。現時点で実装されていると主張しない。
- デバイスパッケージ名、実在クラス名、コンストラクタは必ず実際のソースで確認する。`CobottaClient` のような架空クラスを作らない。

## デバイスパッケージの最小契約

1. 実際に生成される**専用クライアントクラス**を提供する。HTTP/gRPC では例えば `AsyncCobottaClient` と `SyncCobottaClient` のような実在のクラス。専用クラスは基本クラスを継承するだけでもよい。
2. デバイスクラス名を決め、重複しないようにする。登録 `register_device_proxy(name, creator)` はユーザーが明示的に実行できる位置に配置する。import 時登録は選択肢であり必須ではない。
3. 同期・非同期の組があるなら `make_async_sync_factory(async_client_cls=..., sync_client_cls=..., default_async_mode=...)` を利用できる。専用クラスが一つならクラスを直接 creator として渡せる。
4. クライアント固有の `.pyi` をデバイスパッケージ側で管理する。サーバー API の自動公開分だけでなく、クライアント側で追加・オーバーライドしたメソッドの署名を含める。
5. 共通 `DeviceProxy` の型補完が必要なら、デバイス名と**専用クライアントの完全修飾名**を型対応 JSON に記述し、共通 `core.pyi` を再生成する。クライアント API の内容をコピーしない。
6. 各パッケージ固有の `DeviceProxy` と共通 `DeviceProxy` は**別のレジストリ**である。両者を利用する場合は、それぞれへの登録が必要。既存ファクトリを無断で共通レジストリへ移さない。

## 型生成の厳密な制約

- `typing_generator.generate_device_proxy_pyi` は、明示的な型対応 JSON から `core.pyi` を生成する。**実行時の登録を自動検出しない**。生成時にデバイスモジュールを import しない。
- 生成する型宣言は `Literal[device_class]` と専用クライアント型の import だけ。各専用クライアントの `.pyi` を型チェッカーが解決する。
- Python の静的型チェッカーは、別モジュールの同名 `DeviceProxy` の overload を自動合成しない。**共通の `DeviceProxy` の戻り型を自動補完するには共通 `core.pyi` に対応を列挙する必要がある**。単なるインポート時登録だけでは実現しない。
- 生成先は**このパッケージの `src/device_proxy_factory/core.pyi`**。更新後、共通パッケージを再ビルド・再インストールする。インストール済み site-packages を書き換えることを標準手順にしない。
- 型対応 JSON に列挙した専用クライアントパッケージは、その型を利用する環境にインストールされている必要がある。共通パッケージの**ランタイム依存**には追加しない。
- 追加デバイスに応じて共通 `core.pyi` を再生成する手動工程は残る。全デバイスの自動発見は行わない。これは仕様上の制約であり隠さない。

## 変更前チェック

- `/mnt/data` 等で提供された HTTP/gRPC/Tango の実コードと既存生成器を読む。
- `DeviceProxy` が引数をそのまま creator に渡すこと、重複登録エラー、複数デバイス共存をテストする。
- 専用クライアントの override が型スタブで保持されることを静的型チェッカーで検証する（ユニットテストだけでは静的型検査は確認できない）。
- README.md/README.ja.md、docs/ja/docs/en、AGENTS.md の契約を同期する。
- ユーザーの承認なしにパッケージ名、登録方式、同期・非同期仕様を変更しない。

## 配布名・インポート名・README リンク（変更禁止）

- PyPI 配布名およびリポジトリ名（現パッケージ名）: `device-proxy-factory`。
- Python インポート名: `device_proxy`。`device_proxy_factory` に戻さない。
- `src/device_proxy_factory/`、`[tool.setuptools.package-data].device_proxy`、Sphinx の apidoc 対象、全テスト・使用例を一致させる。
- 英語 README: `README.md`、日本語 README: `README.ja.md`。README 間の切替は同じリポジトリ内の相対リンク `README.md` / `README.ja.md` を使用する。
- README と Pages の言語切替を混同しない。README 本文はリンク修正のために書き直さない。


## 固定された配布名・インポート名（変更禁止）
- PyPI 配布名: `device-proxy-factory`
- Python import 名: `device_proxy_factory`
- Python ソース: `src/device_proxy_factory/`
- `from device_proxy_factory import DeviceProxy`
- `device_proxy` への改名は禁止。利用者が明示しない限り README 本文を再作成しない。
