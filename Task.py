#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-04-17 20:24:34
# @Author  : faker (b09780978@gmail.com)
# @Version : 0.0.1

from threading import Thread
from queue import Queue

class TaskException(Exception):
	'''
		if Exception happen on execute TaskRunner,
		it will raise TaskException
	'''
	def __init__(self, error_message):
		self._error_message = error_message

	def __str__(self):
		return self._error_message

class TaskRunner(object):
	'''
		_task_queue: store 
	'''
	_task_queue = None
	_result_queue = None
	_manager = None
	_max_workers = 0

	def __new__(cls):
		if TaskRunner._manager is None:
			TaskRunner._manager =  object.__new__(cls)
			return TaskRunner._manager
		else:
			return TaskRunner._manager

	def __init__(self, max_workers=10, max_tasks=100):
		self._max_workers = max_workers
		self._max_tasks = max_tasks
		self._job_func = None

		self._result_queue = list()
		self._task_queue = Queue(self._max_tasks)

	def work(self):
		while not self._task_queue.empty():
			args = self._task_queue.get()

			if not isinstance(args, str) and hasattr(args, '__len__'):
				result = self._job_func(*args)
			else:
				result = self._job_func(args)

			self._result_queue.append(result)
			self._task_queue.task_done()

	def run(self, job_func=None, params=None):
		self._job_func = job_func
		self._result_queue = list()

		if self._job_func is None:
			raise TaskException('No target function for worker')
		if params is None:
			raise TaskException('No parameters for job function')

		for param in params:
			self._task_queue.put(param)

		self._threads = [ Thread(target=self.work, daemon=True) for _ in range(self._max_workers) ]
		for thread in self._threads:
			thread.start()

		self._task_queue.join()

		return self._result_queue