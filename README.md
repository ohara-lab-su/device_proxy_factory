# device-proxy-factory

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/device-proxy-factory/en/index.html)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://ohara-lab-su.github.io/device-proxy-factory/ja/index.html)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Fdevice--proxy--factory-181717?logo=github)](https://github.com/ohara-lab-su/device-proxy-factory/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/device-proxy-factory/en/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/index.en.html)

A small Python package that maps unique device-class names to callable client factories. It does **not** abstract HTTP
(`ese774_frame`), gRPC (`grpc_frame`), or Tango (`tango_frame`) transport. Its purpose is to instantiate device-specific
clients through one common `DeviceProxy`.

**Status:** 0.2.0 prototype. No existing framework has been modified; the distribution name is provisional. No hardware
integration tests have been performed.

## Installation

Run `python -m pip install .` from the project root, or `python -m pip install -e .` for development. Requires Python
3.7+. Transport frameworks and device packages must be installed separately as needed. Installing this package does
**not** discover or register device packages automatically.

## Contract

- Registry key: unique device-class name; duplicate registration raises `ValueError`.
- Registry value: callable `creator`, including a client class directly.
- `DeviceProxy(device_class, *args, **kwargs)` forwards arguments unchanged to `creator` and does not interpret
  `async_mode`, `config`, `api_spec`, or transport.
- Optional `make_async_sync_factory` handles an async/sync client pair and interprets `async_mode` inside that factory.
- No discovery, entry points, database, or protocol selector.
- Single-device users may instantiate a client directly, use a package-local proxy, or use this common proxy.

## Device package registration

```python
from device_proxy_factory import register_device_proxy, make_async_sync_factory
from .clients import AsyncCobottaClient, SyncCobottaClient

register_device_proxy("CobottaCtrl", make_async_sync_factory(
    async_client_cls=AsyncCobottaClient,
    sync_client_cls=SyncCobottaClient,
    default_async_mode=True,
))
```

The import path `.clients` above is illustrative; use the actual device-package layout. For Tango-style packages with
one dedicated client:

```python
from device_proxy_factory import register_device_proxy
from .device_client import DeviceClient

register_device_proxy("TangoDevice", DeviceClient)
```

Registration can occur during an explicit module import or via an explicit initialization function. Re-registering a
class name in the same process raises an error.

## Client use

```python
from device_proxy_factory import DeviceProxy
import cobotta_device  # illustrative package name; registers CobottaCtrl
import tango_device  # illustrative package name; registers TangoDevice

cobotta = DeviceProxy("CobottaCtrl", server_ip="127.0.0.1", async_mode=False)
tango = DeviceProxy("TangoDevice", "tango://127.0.0.1:10000/test/tango/device#dbase=no")
```

Use the real import paths and constructor arguments of your device packages. `async_mode` is only valid for creators
that support it.

## Public API and testing

`DeviceProxy`, `DeviceProxyEntry`, `register_device_proxy`, `unregister_device_proxy`, `get_device_proxy_entry`,
`list_device_proxies`, `create_device_proxy`, `make_async_sync_factory`.

Install `pytest` and run `python -m pytest -q`. The tests do not require hardware.

## Documentation and limitations

Japanese Pages sources: `docs/ja/`; English: `docs/en/`. Build with `bash docs/build.sh` using Sphinx, MyST Parser, and
sphinx-rtd-theme. GitHub Pages uses `.github/workflows/pages.yml` and publishes the root (English), `/en/`, and `/ja/`.

Existing `ese774_frame` and `grpc_frame` proxies have their **own** registries. Installing this package does not merge
them. Device packages must explicitly register into the common registry; device-specific `.pyi` files are reused through
explicitly generated common overload declarations; integration with real device packages and static type-checker
validation remain outstanding. See `docs/en/limitations.md`.

License: Apache-2.0 (prototype; confirm organizational publication requirements before release).

## Reusing device-specific client `.pyi` (0.2.0)

**Each device package's dedicated client stub is authoritative**, including client-side method additions and overrides.
The shared `DeviceProxy` stub only maps a device-class name to that dedicated client type; it does not copy client API
declarations or use generic base-client stubs.

Create `examples/device-types.json` containing actual fully qualified dedicated client class names, using
`examples/device-types.example.json` as a format reference, then run:

```bash
python -m device_proxy_factory.typing_generator \
    examples/device-types.json src/device_proxy_factory/core.pyi
python -m pip install -e .
```

This explicitly regenerates the shared package's `core.pyi`. Device packages must be installed for static type
resolution. Runtime registration remains separate. Adding a device does **not** automatically update an installed shared
stub. Read the normative AI-oriented engineering contract in [`AGENTS.md`](AGENTS.md) and the English Pages document [
`docs/en/agent-contract.md`](docs/en/agent-contract.md).
