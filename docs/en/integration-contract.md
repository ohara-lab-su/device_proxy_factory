# Device-package integration contract (reproducibility specification)

This document is a contract for future developers and AI assistants to reproduce the **same architecture**, without inventing requirements or claiming unimplemented integration work is complete.

## Invariants

1. The **single common `DeviceProxy` is a factory**, not a transport abstraction. It looks up a callable by device-class name and forwards all arguments unchanged.
2. Device-class names are unique. Reject duplicates; never use `(device_class, transport)` composite keys.
3. Each device package provides dedicated clients. Use actual classes such as `AsyncCobottaClient` and `SyncCobottaClient`; do not invent a `CobottaClient` class.
4. Async/sync selection belongs in a registered factory. `make_async_sync_factory` is an optional helper for HTTP/gRPC pairs. Do not force Tango to use it.
5. Preserve device-specific constructor arguments. The common factory must not interpret or fill `config`, `api_spec`, addresses, etc.
6. No auto-discovery: no `entry_points`, package enumeration, database, or network discovery. Users explicitly import/initialize known device packages.
7. Preserve existing single-device usage: direct client instantiation, package-local proxy, and common proxy are all valid.
8. Keep transport frameworks independent. The common package must not import HTTP/gRPC/Tango; transport and dispatch stay in their frameworks.
9. Do not claim `.pyi` integration is complete. It remains open work.

## Implementation procedure

1. Inspect the **actual source** to identify device class, dedicated client classes, and constructor signatures.
2. Define a callable to instantiate dedicated clients. Existing async/sync pairs may use `make_async_sync_factory`.
3. Register with `register_device_proxy("UniqueDeviceClass", creator)` during explicit package import or initialization.
4. Test creating at least two distinct device classes in the same process via the common `DeviceProxy`.
5. Verify existing direct-client and package-local proxy usage still works.
6. Separately test real transport integration and `.pyi` generation; record untested items explicitly.
7. Update Japanese and English README/Pages documentation together.

## Prohibited deviations

- Adding a `register_backend` transport registry.
- Registering one device-class name separately per transport.
- Giving the common `DeviceProxy` built-in semantics for `async_mode` or `config`.
- Claiming that `pip install` alone automatically resolves device names.
- Replacing existing async/sync client classes with an invented unified class.

## Implemented API

`register_device_proxy(device_class, creator)`, `DeviceProxy(device_class, *args, **kwargs)`, `create_device_proxy(device_class)`, `get_device_proxy_entry(device_class)`, `list_device_proxies()`, `unregister_device_proxy(device_class)`, `make_async_sync_factory(...)`.

This contract covers the **current common-factory prototype**. Migration of existing device packages and integration of type-stub generation remain undecided.
