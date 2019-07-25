# -*- coding: utf-8 -*-

import pytest

from shinkei import MetadataPayload, Version, VersionMetadata


def test_version():
    obj = Version({"api": "v1", "singyeong": "1.2.3"})

    assert obj.api == "v1"
    assert obj.singyeong == "1.2.3"


def test_metadata_payload():
    obj = MetadataPayload({"nonce": None, "payload": 123, "sender": "12345"})

    assert obj.nonce is None
    assert obj.payload == 123
    assert obj.sender == "12345"


def test_version_metadata():
    with pytest.raises(ValueError):
        VersionMetadata("abc")
        VersionMetadata("NotAVersion1.0.0")

    v1 = VersionMetadata("1.0.1")
    v2 = VersionMetadata("1.0.2")

    assert v1 < v2
    assert v1 == v1

    v3 = VersionMetadata("1.0.3")

    assert v3 > v2 > v1

    valpha = VersionMetadata("1.0.3-alpha")

    assert valpha != v3
    assert valpha != v2
    assert valpha != v1

    vplus = VersionMetadata("1.0.3+abc123")

    assert vplus > v3

    assert not v3 == 1
    assert v3 != 1

    with pytest.raises(TypeError):
        assert v3 > 1
        assert v3 >= 1
        assert v3 <= 1
        assert v3 < 1
