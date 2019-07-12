import pytest

from shinkei import Node, QueryBuilder


@pytest.mark.parametrize("thing,key,value", [
    ("eq", "a", "b"),
    ("ne", "a", "b"),
    ("lte", "a", "b"),
    ("contains", "a", "a"),
    ("ncontains", "a", "a"),
    ("gt", "a", "b"),
    ("gte", "a", "b"),
])
def test_normal_query(thing, key, value):
    actual = {
        "application": "test",
        "restricted": True,
        "optional": True,
        "key": "123",
        "ops": [
            {
                key: {
                    f"${thing}": value
                }
            }
        ]
    }

    builder = QueryBuilder(application="test", restricted=True, optional=True, key="123")

    getattr(builder, thing)(key, value)

    assert builder.to_json() == actual


def test_query_in():
    actual = {
        "application": "test",
        "restricted": True,
        "optional": True,
        "key": "123",
        "ops": [
            {
                "a": {
                    f"$in": ["b"]
                }
            }
        ]
    }

    builder = QueryBuilder(application="test", restricted=True, optional=True, key="123")

    builder.inside("a", ["b"])

    assert builder.to_json() == actual


def test_query_nin():
    actual = {
        "application": "test",
        "restricted": True,
        "optional": True,
        "key": "123",
        "ops": [
            {
                "a": {
                    f"$nin": ["b"]
                }
            }
        ]
    }

    builder = QueryBuilder(application="test", restricted=True, optional=True, key="123")

    builder.ninside("a", ["b"])

    assert builder.to_json() == actual


def test_node_also():
    actual = {
        "application": "test",
        "restricted": True,
        "optional": True,
        "key": "123",
        "ops": [
            {
                "a": {"$and": [{"$eq": "a"}, {"$eq": "b"}]}
            }
        ]
    }

    builder = QueryBuilder(application="test", restricted=True, optional=True, key="123")

    builder.also("a", Node().eq("a").eq("b"))

    assert builder.to_json() == actual


def test_node_or():
    actual = {
        "application": "test",
        "restricted": True,
        "optional": True,
        "key": "123",
        "ops": [
            {
                "a": {"$or": [{"$eq": "a"}, {"$eq": "b"}]}
            }
        ]
    }

    builder = QueryBuilder(application="test", restricted=True, optional=True, key="123")

    builder.either("a", Node().eq("a").eq("b"))

    assert builder.to_json() == actual


def test_node_nor():
    actual = {
        "application": "test",
        "restricted": True,
        "optional": True,
        "key": "123",
        "ops": [
            {
                "a": {"$nor": [{"$eq": "a"}, {"$eq": "b"}]}
            }
        ]
    }

    builder = QueryBuilder(application="test", restricted=True, optional=True, key="123")

    builder.neither("a", Node().eq("a").eq("b"))

    assert builder.to_json() == actual
