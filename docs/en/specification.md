# Specification

## Purpose and non-goals

The common `DeviceProxy` is a factory for instantiating clients from multiple device classes, including classes implemented over different transport frameworks, in one process. It does not abstract transport, discover devices, maintain a database, manage connections, or implement dynamic method dispatch. It does not replace existing device-specific clients.

## Registration and construction

`register_device_proxy(device_class: str, creator: Callable)` registers into one process-local registry. Empty, whitespace-padded, and duplicate names are rejected. Uniqueness is enforced **within this process**, not by scanning other processes or installed packages.

`DeviceProxy(device_class, *args, **kwargs)` returns `creator(*args, **kwargs)` without interpreting `async_mode`, `config`, or transport. Unknown names raise `KeyError`. `get_device_proxy_entry` returns an entry, `list_device_proxies` returns sorted names, and `unregister_device_proxy` removes an entry (unknown names raise `KeyError`). `create_device_proxy` binds a device-class name and returns a callable; it does not provide static return typing.

## Optional async/sync helper

`make_async_sync_factory(async_client_cls=..., sync_client_cls=..., default_async_mode=True)` creates a factory that interprets `async_mode=True/False/None`. `None` uses the configured default. Missing requested modes raise `ValueError` rather than silently falling back. Tango clients are not required to use this helper.

## Compatibility

Python >=3.7, no runtime third-party dependencies. Existing transport frameworks retain responsibility for communication and client behavior. Their existing registries are not automatically merged.
