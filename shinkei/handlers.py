# -*- coding: utf-8 -*-

import inspect


class HandlerMeta(type):
    def __new__(mcs, *args, **kwargs):
        name, bases, attrs = args

        attrs["__shinkei_handler_name__"] = kwargs.pop("name", mcs.__name__)

        handlers = {}

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

        return new_cls


def listens_to(name):
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
    @property
    def qualified_name(self):
        return self.__shinkei_handler_name__
