from shinkei import VersionMetadata
from shinkei.gateway import WSClient


def test_packet():
    actual = {
        "a": {"value": "abc", "type": "string"},
        "b": {"value": 123, "type": "integer"},
        "c": {"value": 1.1, "type": "float"},
        "d": {"value": "1.0.0", "type": "version"},
        "e": {"value": ["abc"], "type": "list"},
    }

    generated = WSClient._make_metadata_packet(
        {
            "a": "abc",
            "b": 123,
            "c": 1.1,
            "d": VersionMetadata("1.0.0"),
            "e": ["abc"]
        }
    )

    assert generated == actual
