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

class HTTPResponse(dict):
	"""docstring for """
	def __init__(self, **kwargs):
		self.update(kwargs)

	def __str__(self):
		return self.get('data', 'None')

	@property
	def history(self):
		return self.get('history', list())

	@property
	def data(self):
		return self.get('data', '')

	@property
	def url(self):
		return self.get('url', '')

	@property
	def status(self):
		return self.get('status', 0)

class AioSession(object):
	def __init__(self, config):
		if not isinstance(config, dict):
			raise AioSessionException('Client(config) error\nconfig must a dict')

		self._default_config = {
			'headers' : None,
			'cookies' : None
		}
		self._context = AioSessionContext(config)
		self._loop = asyncio.get_event_loop() if config.get('loop', None) is None else config.get('loop')

	#async def _request(self, method, url, dataType, encoding, params=None, data=None, file=None, **kwargs):
	async def _request(self, method, url, dataType, encoding, **kwargs):
		print(self._context.get('headers'))
		async with ClientSession(**self._context) as session:
			method = method.upper()
			request_func = None
			result = None

			if method == 'GET':
				request_func = session.get
			elif method == 'POST':
				request_func = session.post
			elif method == 'HEAD':
				request_func = session.head
			elif method == 'PUT':
				request_func = session.put
			elif method == 'DELETE':
				request_func = session.delete
			elif method == 'OPTIONS':
				request_func = session.options
			elif method == 'TRACE':
				request_func == session.trace
			elif method == 'PATCH':
				request_func == session.patch
			else:
				raise AioSessionException('Unknow HTTP method {}'.format(method))

			response = None

			async with request_func(url, **kwargs) as resp:
				result = None
				if dataType == 'html':
					result = await resp.text(encoding=encoding)
				elif dataType == 'json':
					result = await resp.json()
				elif dataType == 'media':
					result = await resp.read()
				else:
					raise AioSessionException('Unknow request data type: {}'.format(dataType))

				self._context.update( { 'headers' : session._default_headers, 'cookies' : session._cookie_jar })
				response = HTTPResponse(data=result, url=resp.url, status=resp.status, history=resp.history)

			return response


	'''
		HTTP method: GET
	'''
	def get(self, url, dataType='html', encoding='utf-8', **kwargs):
		 return self._loop.run_until_complete(self._get(url, dataType, encoding, **kwargs))

	async def _get(self, url, dataType, encoding, **kwargs):
		return await self._request('GET', url, dataType, encoding, **kwargs)

	'''
		HTTP method: POST
	'''
	def post(self, url, dataType='html', encoding='utf-8', **kwargs):
		 return self._loop.run_until_complete(self._post(url, dataType, encoding, **kwargs))

	async def _post(self, url, dataType, encoding, **kwargs):
		return await self._request('POST', url, dataType, encoding, **kwargs)

	'''
		HTTP method: HEAD
	'''
	def head(self, url, dataType='html', encoding='utf-8', **kwargs):
		 return self._loop.run_until_complete(self._head(url, dataType, encoding, **kwargs))

	async def _head(self, url, dataType, encoding, **kwargs):
		return await self._request('HEAD', url, dataType, encoding, **kwargs)

	'''
		HTTP method: PUT
	'''
	def put(self, url, dataType='html', encoding='utf-8', **kwargs):
		 return self._loop.run_until_complete(self._put(url, dataType, encoding, **kwargs))

	async def _put(self, url, dataType, encoding, **kwargs):
		return await self._request('PUT', url, dataType, encoding, **kwargs)

	'''
		HTTP method: DELETE
	'''
	def delete(self, url, dataType='html', encoding='utf-8', **kwargs):
		 return self._loop.run_until_complete(self._delete(url, dataType, encoding, **kwargs))

	async def _delete(self, url, dataType, encoding, **kwargs):
		return await self._request('DELETE', url, dataType, encoding, **kwargs)

	'''
		HTTP method: OPTIONS
	'''
	def options(self, url, dataType='html', encoding='utf-8', **kwargs):
		 return self._loop.run_until_complete(self._options(url, dataType, encoding, **kwargs))

	async def _options(self, url, dataType, encoding, **kwargs):
		return await self._request('OPTIONS', url, dataType, encoding, **kwargs)

	'''
		HTTP method: TRACE
	'''
	def trace(self, url, dataType='html', encoding='utf-8', **kwargs):
		 return self._loop.run_until_complete(self._trace(url, dataType, encoding, **kwargs))

	async def _trace(self, url, dataType, encoding, **kwargs):
		return await self._request('TRACE', url, dataType, encoding, **kwargs)

	'''
		HTTP method: PATCH
	'''
	def patch(self, url, dataType='html', encoding='utf-8', **kwargs):
		 return self._loop.run_until_complete(self._patch(url, dataType, encoding, **kwargs))

	async def _patch(self, url, dataType, encoding, **kwargs):
		return await self._request('PATCH', url, dataType, encoding, **kwargs)

	def close(self):
		# Prevent tls close too quickly
		self._loop.run_until_complete(asyncio.sleep(0.25))
		self._loop.close()

# Alias name
Session = AioSession