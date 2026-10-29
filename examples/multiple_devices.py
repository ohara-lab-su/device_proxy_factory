"""実機・通信フレームワークを必要としない動作例。"""
from device_proxy_factory import DeviceProxy, register_device_proxy, make_async_sync_factory


class SyncExampleClient:
    def __init__(self, address):
        self.address = address


class AsyncExampleClient(SyncExampleClient):
    pass


class TangoExampleClient:
    def __init__(self, url):
        self.url = url


register_device_proxy("ExampleHttp", make_async_sync_factory(
    async_client_cls=AsyncExampleClient,
    sync_client_cls=SyncExampleClient,
))
register_device_proxy("ExampleTango", TangoExampleClient)

http = DeviceProxy("ExampleHttp", "127.0.0.1", async_mode=False)
tango = DeviceProxy("ExampleTango", "tango://example")
print(type(http).__name__, type(tango).__name__)
