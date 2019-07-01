# -*- coding: utf-8 -*-

import json
import logging

import aiohttp
from yarl import URL

from .exceptions import ShinkeiHTTPException
from .objects import Version

log = logging.getLogger(__name__)


class APIClient:
    def __init__(self):
        self.headers = {}
        self.session = None

    @classmethod
    async def create(cls, url, *, session, auth, loop):
        self = cls()

        self.session = session or aiohttp.ClientSession(loop=loop)
        self.url = URL(url) / "api"
        self.auth = auth

        if self.auth:
            self.headers["Authorization"] = auth

        self.version = Version(await self._fetch_version())

        self.url = self.url / self.version.api

        return self

    async def request(self, method, url, **kwargs):
        async with self.session.request(method, url, headers=self.headers, **kwargs) as response:
            log.debug("%s %s with %s returned %d status code",
                      method, url.human_repr(), kwargs.get("data"), response.status)

            data = await response.json()
            if not response.status == 200:
                raise ShinkeiHTTPException(
                    response, response.status, "{0.status} {0.reason} {1}".format(response, data.get("error"))
                )

            return data

    async def _fetch_version(self):
        return await self.request("GET", self.url / "version")

    async def discovery_tags(self, tags):
        if not isinstance(tags, list):
            raise TypeError("Expected type list, got {0}".format(tags.__class__.__name__))
        tags = json.dumps(tags)
        url = (self.url / "discovery" / "tags").with_query(f"q={tags}")

        return await self.request("GET", url)

    async def proxy(self, method, route, application, target):
        payload = {
            "method": method,
            "route": route,
            "query": {
                "application": application,
                "ops": target.to_json()
            }
        }

        return await self.request("POST", self.url / "proxy", data=payload)
