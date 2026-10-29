# Limitations and open work

1. **No existing framework modified.** Existing `ese774_frame` and `grpc_frame` proxies retain separate registries. Device packages must explicitly register into this common package. Tango implementation remains unchanged.
2. **No automatic registration.** `pip install` alone does not register devices. Explicit import or initialization is required by design.
3. **Collisions.** Duplicate names in the same process raise `ValueError`; aliases are not implemented.
4. **`.pyi` declarations not populated for real devices.** A generator for `core.pyi` referencing dedicated client types exists, but real device mappings and static type-checker verification remain outstanding. The shipped generic stub returns `Any`.
5. **No hardware tests.** HTTP/gRPC/Tango connection and device lifecycle have not been integration-tested. Unit tests use dummy clients.
6. **Arguments unchanged.** The core does not transform constructor arguments. `async_mode` is supported only by factories that explicitly implement it.
7. **Process/thread behavior.** Registry is process-local and not shared across processes. Strict synchronization between registration, removal, and construction is not provided.
8. **Naming/migration.** Distribution name is provisional. No existing proxy replacement, re-export, device-package migration, or release has occurred.
9. **Python 3.7.** Source uses 3.7-compatible syntax, but has not been executed under a Python 3.7 interpreter here.

These items must be validated during migration, not assumed complete.

## 静的型情報 / Static typing

各デバイスの `.pyi` は自動的に共通 `DeviceProxy` の overload に合成されない。明示的な型対応 JSON と共通 `core.pyi` の再生成が必要。インストール済みのパッケージを自動探索しない。専用クライアント `.pyi` の内容（クライアント側の override を含む）はデバイスパッケージ側の責任。/ Type checkers do not merge overloads across packages; an explicit mapping and regeneration are required. Device-specific overrides belong in dedicated client stubs.
