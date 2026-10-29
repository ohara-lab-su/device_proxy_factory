import pytest
from device_proxy_factory import (
    DeviceProxy, create_device_proxy, get_device_proxy_entry,
    list_device_proxies, make_async_sync_factory,
    register_device_proxy, unregister_device_proxy,
)


class SyncClient:
    def __init__(self, value, **kwargs):
        self.value = value
        self.kwargs = kwargs


class AsyncClient(SyncClient):
    pass


def test_multiple_device_classes_and_factory():
    register_device_proxy("TestHttp", make_async_sync_factory(
        async_client_cls=AsyncClient, sync_client_cls=SyncClient))
    register_device_proxy("TestTango", SyncClient)
    try:
        assert isinstance(DeviceProxy("TestHttp", 3), AsyncClient)
        assert isinstance(DeviceProxy("TestHttp", 4, async_mode=False), SyncClient)
        assert type(DeviceProxy("TestTango", 5)) is SyncClient
        assert create_device_proxy("TestTango")(6).value == 6
        assert get_device_proxy_entry("TestHttp").device_class == "TestHttp"
        assert "TestTango" in list_device_proxies()
    finally:
        unregister_device_proxy("TestHttp")
        unregister_device_proxy("TestTango")


def test_duplicate_and_missing():
    register_device_proxy("Unique", SyncClient)
    try:
        with pytest.raises(ValueError):
            register_device_proxy("Unique", AsyncClient)
        with pytest.raises(KeyError):
            DeviceProxy("Unknown")
    finally:
        unregister_device_proxy("Unique")


def test_arguments_untouched_and_sync_choice():
    register_device_proxy("Forward", make_async_sync_factory(
        async_client_cls=AsyncClient, sync_client_cls=SyncClient))
    try:
        client = DeviceProxy("Forward", 7, async_mode=False, config={"x": 1})
        assert client.kwargs == {"config": {"x": 1}}
        with pytest.raises(TypeError):
            DeviceProxy("Forward", 1, async_mode="yes")
    finally:
        unregister_device_proxy("Forward")


def test_missing_mode_raises_not_fallback():
    factory = make_async_sync_factory(sync_client_cls=SyncClient, default_async_mode=False)
    assert isinstance(factory(1), SyncClient)
    with pytest.raises(ValueError):
        factory(1, async_mode=True)
