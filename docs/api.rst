.. currentmodule:: shinkei

API Reference
=============

This sections outlines the shinkei API.


Client
------

.. autofunction:: connect

.. autoclass:: Client()
    :members:


Query Builder
-------------

.. autoclass:: QueryBuilder
    :members:

.. autoclass:: Node
    :members:


Data Classes
------------

.. autoclass:: Version()

.. autoclass:: MetadataPayload()


Exceptions
----------

.. autoclass:: ShinkeiException()

.. autoclass:: ShinkeiHTTPException()

.. autoclass:: ShinkeiWSException()

.. autoclass:: ShinkeiResumeWS()

.. autoclass:: ShinkeiWSClosed()