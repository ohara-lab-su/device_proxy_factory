# How-to

## Install and test

```bash
python -m pip install .
python -m pip install pytest
python -m pytest -q
python examples/multiple_devices.py
```

## Register in a device package

```python
from device_proxy_factory import register_device_proxy, make_async_sync_factory
register_device_proxy("CobottaCtrl", make_async_sync_factory(
    async_client_cls=AsyncCobottaClient,
    sync_client_cls=SyncCobottaClient,
    default_async_mode=True,
))
```

Import the actual `AsyncCobottaClient` and `SyncCobottaClient` classes from the device package. The common module does not import them. For a Tango-style `DeviceClient`, use `register_device_proxy("TangoDevice", DeviceClient)`.

## Multiple devices in one process

Explicitly import the device packages you use so their registration code executes. Then use the same common `DeviceProxy` to create `DeviceProxy("CobottaCtrl", ..., async_mode=False)` and `DeviceProxy("TangoDevice", ...)`. Constructor arguments are device-specific.

## One device

Direct client construction, a package-local proxy, and the common proxy are all valid. Using the common proxy is optional.

## Build Pages

```bash
python -m pip install sphinx myst-parser sphinx-rtd-theme linkify-it-py
bash docs/build.sh
```

## Reuse dedicated client typing

Each device package owns the authoritative `.pyi` for its dedicated client classes, including client-side overrides. Copy `examples/device-types.example.json` to `examples/device-types.json` and replace illustrative qualified class names with the real ones. Then run:

```bash
python -m device_proxy_factory.typing_generator examples/device-types.json src/device_proxy_factory/core.pyi
```

The common stub refers to the dedicated client classes; it does not copy their APIs. Runtime factory registration remains separate. Rebuild the common package to ship the updated stub. This is a manual operation; installed packages are not scanned.
