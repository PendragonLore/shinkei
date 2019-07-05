# -*- coding: utf-8 -*-

import inspect


class HandlerMeta(type):
    # noinspection PyUnresolvedReferences
    """A metaclass used to implement the main functionality of the handlers.

        Not really to be used directly but rather to implement more complex custom handler classes.

        Note
        ----
        The name kwarg are meant to be passed in the type constructor, like this:

        .. code-block:: python3

            class MyHandler(shinkei.Handler, name=\"My Handler\"):
                pass

        Arguments
        ----------
        name: Optional[:class:`str`]
            The name of the handler, used to determine if it has already been registered or not.
            Defaults to the class's name."""
    def __new__(mcs, *args, **kwargs):
        name, bases, attrs = args

        actual_name = kwargs.pop("name", None)

        if actual_name is not None and not isinstance(actual_name, str):
            raise TypeError("name must be of type str, got {0.__class__.__name__}".format(actual_name))

        handlers = {}

        # noinspection PyArgumentList
        new_cls = super().__new__(mcs, name, bases, attrs, **kwargs)
        for base in reversed(new_cls.__mro__):
            for elem, value in base.__dict__.items():
                if elem in handlers:
                    del handlers[elem]

                if isinstance(value, staticmethod):
                    value = value.__func__

                if inspect.iscoroutinefunction(value):
                    try:
                        getattr(value, "__shinkei_listens_to__")
                    except AttributeError:
                        pass
                    else:
                        handlers[elem] = value

        handlers_list = [(handler.__shinkei_listens_to__, handler.__name__) for handler in handlers.values()]

        new_cls.__shinkei_handlers__ = handlers_list
        new_cls.__shinkei_handler_name__ = actual_name

        return new_cls


def listens_to(name):
    """A decorator to register a method of a :class:`Handler` as a listener.

    The method must be a coroutine.

    Arguments
    ---------
    name: :class:`str`
        The name of the event to listen to.

    Raises
    ------
    TypeError
        The name was not a string or the method was not a coroutine."""
    if not isinstance(name, str):
        raise TypeError("Name must be str, got {0.__class__.__name__} instead.".format(name))

    def wrapper(func):
        actual = func
        if isinstance(actual, staticmethod):
            actual = func.__func__

        if not inspect.iscoroutinefunction(actual):
            raise TypeError("Callback must be a coroutine.")

        actual.__shinkei_listens_to__ = name

        return func

    return wrapper


class Handler(metaclass=HandlerMeta):
    """The base class for event handlers.

    This class is made only for subclassing."""
    @property
    def qualified_name(self):
        """:class:`str`: returns the name passed in the type constructor, else the class name."""
        return self.__shinkei_handler_name__ if self.__shinkei_handler_name__ is not None else self.__class__.__name__
