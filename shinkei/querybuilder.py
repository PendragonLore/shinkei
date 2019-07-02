# -*- coding: utf-8 -*-


class QueryBuilder:
    """A utility to build queries which routes clients based on their metadata.

    Used mostly in :meth:`Client.send` and :meth:`Client.broadcast`

    Example using key-value queries:

    .. code-block:: python3

        # this will target every client part of "my-cool-app" where "special_value" is greater then 5
        shinkei.QueryBuilder(application="my-cool-app", key="uniquekey").gt("special_value", 5)

    Example using :class:`Node` based query:

    .. code-block:: python3

        # this will target every client part of "my-cool-app" where "special_value" is greater then 5 or is equal to 10
        shinkei.QueryBuilder(application="my-cool-app", key="uniquekey").either(
            "special_value", shinkei.Node().eq(10).gt(5)
        )

    Parameters
    ----------
    application: :class:`str`
        The id of the target application.
    key: :class:`str`
        The key used for consistent-hashing when choosing a client from the output.
    restricted: Optional[:class:`bool`]
        Whether or not if restricted clients should be included.
        Defaults to ``False``.
    optional: Optional[:class:`bool`]
        Whether or not to return a result even if the query fails.
        Defaults to ``False``."""

    __slots__ = (
        "_ops",
        "application",
        "restricted",
        "optional",
        "key"
    )

    def __init__(self, application, key, **kwargs):
        self._ops = []

        self.application = application
        self.key = key
        self.restricted = kwargs.get("restricted", False)
        self.optional = kwargs.get("optional", False)

    def _single_strategy(self, op, key, value):
        self._ops.append({key: {f"${op}": value}})

        return self

    def _multiple_stategy(self, op, key, builder):
        if not isinstance(builder, Node):
            raise TypeError("builder must be of type Node, got {0}", type(builder).__name__)
        if not builder._ops:
            raise TypeError("Node provided doesn't have any OPs.")

        self._ops.append({key: {f"${op}": builder.to_json()}})

        return self

    def eq(self, key, value):
        """Matches if the value of ``key`` equals to ``value``"""
        return self._single_strategy("eq", key, value)

    def ne(self, key, value):
        """Matches if the value of ``key`` is not equal to ``value``"""
        return self._single_strategy("ne", key, value)

    def gt(self, key, value):
        """Matches if the value of ``key`` is greater then ``value``"""
        return self._single_strategy("gt", key, value)

    def gte(self, key, value):
        """Matches if the value of ``key`` is equal to or greater then ``value``"""
        return self._single_strategy("gte", key, value)

    def lt(self, key, value):
        """Matches if the value of ``key`` is lower then ``value``"""
        return self._single_strategy("lt", key, value)

    def lte(self, key, value):
        """Matches if the value of ``key`` is equal to or lower then ``value``"""
        return self._single_strategy("lte", key, value)

    def inside(self, key, value):
        """Matches if the value of ``key`` is inside ``value``.

        ``value`` must be a :class:`list`."""
        return self._single_strategy("in", key, value)

    def ninside(self, key, value):
        """Matches if the value of ``key`` is not inside ``value``.

        ``value`` must be a :class:`list`."""
        return self._single_strategy("nin", key, value)

    def contains(self, key, value):
        """Matches if ``value`` is inside the value of ``key``.

        The value of ``key`` must be a :class:`list`."""
        return self._single_strategy("contains", key, value)

    def ncontains(self, key, value):
        """Matches if ``value`` is not inside the value of ``key``.

        The value of ``key`` must be a :class:`list`."""
        return self._single_strategy("ncontains", key, value)

    def also(self, key, node):
        """Matches if all the predicates in ``node`` succeed.

        ``node`` must be an instance of :class:`Node`."""
        return self._multiple_stategy("and", key, node)

    def either(self, key, node):
        """Matches if any of the predicates in ``node`` succeed.

        ``node`` must be an instance of :class:`Node`."""
        return self._multiple_stategy("or", key, node)

    def neither(self, key, node):
        """Matches if no predicates in ``node`` succeed.

        ``node`` must be an instance of :class:`Node`."""
        return self._multiple_stategy("nor", key, node)

    def to_json(self):
        return {"ops": self._ops, "key": self.key,
                "application": self.application, "optional": self.optional, "restricted": self.restricted}


class Node:
    """Similar to :class:`QueryBuilder`, but used only for
    predicates inside :meth:`~QueryBuilder.also`, :meth:`~QueryBuilder.either` and :meth:`~QueryBuilder.neither`."""
    __slots__ = ("_ops",)

    def __init__(self):
        self._ops = []

    def _single_strategy(self, op, value):
        self._ops.append({f"${op}": value})

        return self

    def eq(self, value):
        """Equals to :meth:`QueryBuilder.eq`, but only takes a value."""
        return self._single_strategy("eq", value)

    def ne(self, value):
        """Equals to :meth:`QueryBuilder.ne`, but only takes a value."""
        return self._single_strategy("ne", value)

    def gt(self, value):
        """Equals to :meth:`QueryBuilder.gt`, but only takes a value."""
        return self._single_strategy("gt", value)

    def gte(self, value):
        """Equals to :meth:`QueryBuilder.gte`, but only takes a value."""
        return self._single_strategy("gte", value)

    def lt(self, value):
        """Equals to :meth:`QueryBuilder.lt`, but only takes a value."""
        return self._single_strategy("lt", value)

    def lte(self, value):
        """Equals to :meth:`QueryBuilder.lte`, but only takes a value."""
        return self._single_strategy("lte", value)

    def inside(self, value):
        """Equals to :meth:`QueryBuilder.inside`, but only takes a value."""
        return self._single_strategy("in", value)

    def ninside(self, value):
        """Equals to :meth:`QueryBuilder.ninside`, but only takes a value."""
        return self._single_strategy("nin", value)

    def contains(self, value):
        """Equals to :meth:`QueryBuilder.contains`, but only takes a value."""
        return self._single_strategy("contains", value)

    def ncontains(self, value):
        """Equals to :meth:`QueryBuilder.ncontains`, but only takes a value."""
        return self._single_strategy("ncontains", value)

    def to_json(self):
        return self._ops
