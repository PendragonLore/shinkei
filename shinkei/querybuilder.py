# -*- coding: utf-8 -*-

class QueryBuilder:
    __slots__ = ("_ops", "application_id", "restricted", "optional", "key")

    def __init__(self, **kwargs):
        self._ops = []

        self.application_id = kwargs.get("application_id")
        self.key = kwargs.get("key")
        self.restricted = kwargs.get("restricted", True)
        self.optional = kwargs.get("optional", False)

    def config(self, **kwargs):
        try:
            self.application_id = kwargs["application_id"]
            self.key = kwargs["key"]
        except KeyError:
            if not self.application_id and not self.key:
                raise TypeError("Both key and application_id must be passed in a config call.")
        self.restricted = kwargs.get("restricted", self.restricted)
        self.optional = kwargs.get("optional", self.optional)

        return self

    def _single_strategy(self, op, key, value):
        self._ops.append({key: {f"${op}": value}})

        return self

    def _multiple_stategy(self, op, key, builder):
        if not builder._ops:
            raise TypeError("QueryBuilder provided doesn't have any OPs.")

        self._ops.append({key: {op: builder.to_json()}})

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

    def to_json(self):
        return {"ops": self._ops, "key": self.key,
                "application": self.application_id, "optional": self.optional, "restricted": self.restricted}
