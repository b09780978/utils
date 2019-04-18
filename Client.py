# -*- coding: utf-8 -*-
# @Date    : 2019-04-18 18:15:05
# @Author  : faker (b09780978@gmail.com)
# @Version : 0.0.1
import asyncio
from aiohttp import ClientSession

class AioSessionException(Exception):
	'''
		Exception for Client class
	'''
	def __init__(self, error_message):
		self._error_message = error_message

	def __str__(self):
		return self._error_message


class AioSessionContext(dict):
	'''
		ClientContext is used to store headers and cookies,
		since we can't direct inherit aiohttp.ClientSession.
	'''
	def __init__(self, config):
		super(AioSessionContext, self).__init__(self)
		self.update(config)

class AioSession(object):
	def __init__(self, config):
		if not isinstance(config, dict):
			raise AioSessionException('Client(config) error\nconfig must a dict')

		self._context = AioSessionContext(config)
		self._loop = asyncio.get_event_loop() if config.get('loop', None) is None else config.get('loop')

	'''
		HTTP method: GET
	'''
	def get(self, url, json=False, **kwargs):
		 return self._loop.run_until_complete(self._get(url, json, **kwargs))

	async def _get(self, url, json, **kwargs):
		async with ClientSession(**self._context) as session:
			async with session.get(url, **kwargs) as resp:
				result = await resp.text() if not json else await resp.json()
				self._context.update( { 'headers' : session._default_headers, 'cookies' : session._cookie_jar })
				return result

	'''
		HTTP method: POST
	'''
	def post(self, url, json=False, **kwargs):
		 return self._loop.run_until_complete(self._post(url, json, **kwargs))

	async def _post(self, url, json, **kwargs):
		async with ClientSession(**self._context) as session:
			async with session.post(url, **kwargs) as resp:
				result = await resp.text() if not json else await resp.json()
				self._context.update( { 'headers' : session._default_headers, 'cookies' : session._cookie_jar })
				return result

	'''
		HTTP method: HEAD
	'''
	def head(self, url, json=False, **kwargs):
		 return self._loop.run_until_complete(self._head(url, json, **kwargs))

	async def _head(self, url, json=False, **kwargs):
		async with ClientSession(**self._context) as session:
			async with session.head(url, **kwargs) as resp:
				result = await resp.text() if not json else await resp.json()
				self._context.update( { 'headers' : session._default_headers, 'cookies' : session._cookie_jar })
				return result

	'''
		HTTP method: PUT
	'''
	def put(self, url, json=False, **kwargs):
		 return self._loop.run_until_complete(self._put(url, json, **kwargs))

	async def _put(self, url, json, **kwargs):
		async with ClientSession(**self._context) as session:
			async with session.put(url, **kwargs) as resp:
				result = await resp.text() if not json else await resp.json()
				self._context.update( { 'headers' : session._default_headers, 'cookies' : session._cookie_jar })
				return result

	'''
		HTTP method: DELETE
	'''
	def delete(self, url, json=False, **kwargs):
		 return self._loop.run_until_complete(self._delete(url, json, **kwargs))

	async def _delete(self, url, json, **kwargs):
		async with ClientSession(**self._context) as session:
			async with session.delete(url, **kwargs) as resp:
				result = await resp.text() if not json else await resp.json()
				self._context.update( { 'headers' : session._default_headers, 'cookies' : session._cookie_jar })
				return result

	'''
		HTTP method: OPTIONS
	'''
	def options(self, url, json=False, **kwargs):
		 return self._loop.run_until_complete(self._options(url, json, **kwargs))

	async def _options(self, url, json, **kwargs):
		async with ClientSession(**self._context) as session:
			async with session.options(url, **kwargs) as resp:
				result = await resp.text() if not json else await resp.json()
				self._context.update( { 'headers' : session._default_headers, 'cookies' : session._cookie_jar })
				return result

	'''
		HTTP method: TRACE
	'''
	def trace(self, url, json=False, **kwargs):
		 return self._loop.run_until_complete(self._trace(url, json, **kwargs))

	async def _trace(self, url, json, **kwargs):
		async with ClientSession(**self._context) as session:
			async with session.trace(url, **kwargs) as resp:
				result = await resp.text() if not json else await resp.json()
				self._context.update( { 'headers' : session._default_headers, 'cookies' : session._cookie_jar })
				return result

	'''
		HTTP method: PATCH
	'''
	def patch(self, url, json=False, **kwargs):
		 return self._loop.run_until_complete(self._patch(url, json, **kwargs))

	async def _patch(self, url, json, **kwargs):
		async with ClientSession(**self._context) as session:
			async with session.patch(url, **kwargs) as resp:
				result = await resp.text() if not json else await resp.json()
				self._context.update( { 'headers' : session._default_headers, 'cookies' : session._cookie_jar })
				return result

class Session(AioSession):
	pass