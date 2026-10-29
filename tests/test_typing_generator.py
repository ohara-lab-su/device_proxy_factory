import pytest
from device_proxy_factory.typing_generator import generate_device_proxy_pyi


def test_generates_dedicated_client_imports(tmp_path):
    dest = tmp_path / "core.pyi"
    generate_device_proxy_pyi([
        {"device_class": "Http", "async_client": "a.AsyncClient", "sync_client": "a.SyncClient"},
        {"device_class": "Grpc", "async_client": "b.AsyncClient", "sync_client": "b.SyncClient", "default_async_mode": False},
        {"device_class": "Tango", "client": "c.DeviceClient"},
    ], dest)
    result = dest.read_text()
    assert "from a import AsyncClient" in result
    assert "from b import SyncClient" in result
    assert "from c import DeviceClient" in result
    assert 'Literal[\'Http\']' in result
    assert 'Literal[\'Grpc\']' in result
    assert 'Literal[\'Tango\']' in result
    compile(result, str(dest), "exec")


def test_rejects_duplicate_and_invalid(tmp_path):
    with pytest.raises(ValueError):
        generate_device_proxy_pyi([{"device_class": "A", "client": "a.C"}, {"device_class": "A", "client": "b.C"}], tmp_path / "x.pyi")
    with pytest.raises(ValueError):
        generate_device_proxy_pyi([{"device_class": "A", "client": "invalid"}], tmp_path / "x.pyi")
