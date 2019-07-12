from shinkei import MetadataPayload, Version


def test_version():
    obj = Version({"api": "v1", "singyeong": "1.2.3"})

    assert obj.api == "v1"
    assert obj.singyeong == "1.2.3"


def test_metadata_payload():
    obj = MetadataPayload({"nonce": None, "payload": 123, "sender": "12345"})

    assert obj.nonce is None
    assert obj.payload == 123
    assert obj.sender == "12345"
