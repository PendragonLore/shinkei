# -*- coding: utf-8 -*-

import pathlib
import re

from setuptools import setup

ROOT = pathlib.Path(__file__).parent

with open(ROOT / "requirements.txt") as f:
    requirements = f.read().splitlines()

with open(ROOT / "shinkei" / "__init__.py") as f:
    version = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError("Version is not set.")

if version.endswith(("a", "b", "rc")):
    # noinspection PyBroadException
    try:
        import subprocess

        p = subprocess.Popen(["git", "rev-list", "--count", "HEAD"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode("utf-8").strip()
        p = subprocess.Popen(["git", "rev-parse", "--short", "HEAD"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += "+g" + out.decode("utf-8").strip()
    except Exception:
        pass

with open(ROOT / "README.md") as f:
    readme = f.read()

extras = {
    "docs": [
        "sphinx",
        "sphinxcontrib_trio"
    ],
    "ujson": [
        "ujson"
    ]
}
setup(
    name="shinkei",
    author="Lorenzo",
    url="https://github.com/PendragonLore/shinkei",
    license="MIT",
    description="An asynchronous client for singyeong",
    long_description=readme,
    long_description_content_type="text/markdown",
    project_urls={
        "Code": "https://github.com/PendragonLore/shinkei",
        "Issue tracker": "https://github.com/PendragonLore/shinkei/issues",
        "Documentation": "https://shinkei.rtfd.io"
    },
    version=version,
    packages=["shinkei", "shinkei.ext"],
    platforms=["any"],
    python_requires=">=3.6.0",
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras,
    keywords="ipc, asyncio, singyeong",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Framework :: AsyncIO",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Utilities",
        "Topic :: System :: Networking",
        "Topic :: Software Development :: Libraries",
    ]
)
