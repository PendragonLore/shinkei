from shinkei.client import CacheManager


def test_cache_manager():
    manager = CacheManager()

    manager.add({"a": "b"})

    assert manager._internal == {"a": "b"}

    manager.add({"b": "a"})

    assert manager._internal == {"a": "b", "b": "a"}

    manager.add({"b": 123})

    assert manager._internal == {"a": "b", "b": 123}

    clared = manager.pop_all()

    assert manager._internal == {}
    assert clared == {"a": "b", "b": 123}
