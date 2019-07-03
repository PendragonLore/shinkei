# shinkei

A client library for [singyeong](https://github.com/queer/singyeong), a fully-dynamic, metadata-oriented service mesh.

For more info on how to configure and run a singyeong server visit the official repository previously linked.

The binaries are available on [docker](https://hub.docker.com/r/queer/singyeong).

### Credits

Special thanks to [amy (queer)](https://github.com/queer/) for creating and helping me understand singyeong.

## Installation

The library is available on PyPi so it can be installed through pip:

```bash
pip install shinkei -U
```

This library is compatible only with Python 3.6+ and has two main dependencies, [websockets](https://github.com/aaugustin/websockets)
and [aiohttp](https://github.com/aio-libs/aiohttp).

It's also recommended to install [ujson](https://github.com/esnme/ultrajson) for faster JSON encoding/decoding.

The library can be installed with this extra dependency through this command:

```bash
pip install shinkei[ujson] -U
```

## Documentation

The documentation is available at [read the docs](https://shinkei.rtfd.io).
