# AI implementation contract (normative)

This is a machine-oriented engineering contract, not a replacement for the human README. The Japanese `AGENTS.md` is authoritative. Do not redesign the system from inference.

- One shared `DeviceProxy` is **only** a factory: map a unique device-class name to a registered callable `creator`. No transport abstraction, backend registry, automatic discovery, entry points, or device database.
- The HTTP (`ese774_frame`), gRPC (`grpc_frame`), and Tango (`tango_frame`) packages remain independent. This package imports none of them at runtime.
- Device packages own their **dedicated client classes** and their `.pyi` signatures. Client-side overrides and additions must be reflected in those dedicated stubs; never substitute a generic base client's stub.
- HTTP/gRPC may have separate sync and async dedicated clients. `make_async_sync_factory` selects between them; the shared `DeviceProxy` does not interpret `async_mode`. Tango is not forced into this pair model.
- Constructor arguments, `config`, `api_spec`, and connection details belong to the device/framework. The shared factory forwards them unchanged.
- A device package may expose direct clients, its own `DeviceProxy`, and the shared `DeviceProxy`. These options coexist; their registries are not automatically merged.
- Registration must be explicit Python execution. Import-time registration is optional, not mandatory. Duplicate device-class names are rejected.
- For common `DeviceProxy` typing, maintain an **explicit** JSON map from device-class names to the **fully qualified dedicated client classes**. Run `typing_generator` to generate `src/device_proxy_factory/core.pyi`. The generator only imports class names in the stub; it does not copy or regenerate client API declarations.
- Python type checkers do not automatically merge overloads from different packages. Updating `core.pyi` and rebuilding/reinstalling the common package is required when the set of typed devices changes. Installed client packages must be available for type resolution. This is a known limitation, not a feature to conceal.
- Preserve Python 3.7 support and Japanese code comments. Never invent actual class names. Review the real HTTP/gRPC/Tango sources and existing stub generators before modifications.
- Validate runtime multi-device operation, duplicate registration, argument forwarding, and static resolution of overridden client methods. Keep README and Japanese/English Pages in sync.
