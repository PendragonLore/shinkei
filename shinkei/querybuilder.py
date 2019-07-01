# -*- coding: utf-8 -*-


class QueryBuilder:
    __slots__ = ("_ops", "application", "restricted", "optional", "key")

    def __init__(self, **kwargs):
        self._ops = []

        self.application = kwargs.get("application")
        self.key = kwargs.get("key")
        self.restricted = kwargs.get("restricted", True)
        self.optional = kwargs.get("optional", False)

    def config(self, **kwargs):
        try:
            self.application = kwargs["application"]
            self.key = kwargs["key"]
        except KeyError:
            if not self.application and not self.key:
                raise TypeError("Both key and application_id must be passed in a config call.")
        self.restricted = kwargs.get("restricted", self.restricted)
        self.optional = kwargs.get("optional", self.optional)

        return self

    def _single_strategy(self, op, key, value):
        self._ops.append({key: {f"${op}": value}})

        return self

    def _multiple_stategy(self, op, key, builder):
        if not isinstance(builder, Node):
            raise TypeError("builder must be of type Node (got {0})", type(builder).__name__)
        if not builder._ops:
            raise TypeError("Node provided doesn't have any OPs.")

        self._ops.append({key: {f"${op}": builder.to_json()}})

        return self

    def eq(self, key, value):
        return self._single_strategy("eq", key, value)

    def ne(self, key, value):
        return self._single_strategy("ne", key, value)

    def gt(self, key, value):
        return self._single_strategy("gt", key, value)

    def gte(self, key, value):
        return self._single_strategy("gte", key, value)

    def lt(self, key, value):
        return self._single_strategy("lt", key, value)

    def lte(self, key, value):
        return self._single_strategy("lte", key, value)

    def inside(self, key, value):
        return self._single_strategy("in", key, value)

    def ninside(self, key, value):
        return self._single_strategy("nin", key, value)

    def contains(self, key, value):
        return self._single_strategy("contains", key, value)

    def ncontains(self, key, value):
        return self._single_strategy("ncontains", key, value)

    def also(self, key, node):
        return self._multiple_stategy("and", key, node)

    def either(self, key, node):
        return self._multiple_stategy("or", key, node)

    def neither(self, key, node):
        return self._multiple_stategy("nor", key, node)

    def to_json(self):
        return {"ops": self._ops, "key": self.key,
                "application": self.application, "optional": self.optional, "restricted": self.restricted}


class Node:
    __slots__ = ("_ops",)

    def __init__(self):
        self._ops = []

    def _single_strategy(self, op, value):
        self._ops.append({f"${op}": value})

        return self

    def eq(self, value):
        return self._single_strategy("eq", value)

    def ne(self, value):
        return self._single_strategy("ne", value)

    def gt(self, value):
        return self._single_strategy("gt", value)

    def gte(self, value):
        return self._single_strategy("gte", value)

    def lt(self, value):
        return self._single_strategy("lt", value)

    def lte(self, value):
        return self._single_strategy("lte", value)

    def inside(self, value):
        return self._single_strategy("in", value)

    def ninside(self, value):
        return self._single_strategy("nin", value)

    def contains(self, value):
        return self._single_strategy("contains", value)

    def ncontains(self, value):
        return self._single_strategy("ncontains", value)

    def to_json(self):
        return self._ops
