import importlib
import pkgutil
import sys
import os

def get_most_frequent(elements):
	freqs = dict()
	for element in elements:
		freqs[element] = freqs.get(element, 0) + 1
	if len(freqs.keys()) == 0:
		return None
	else:
		return max(freqs, key=freqs.get)

class NVersionProgramming():

	def __init__(self, components, silent=True):
		self.components = components
		self.silent = silent

	def read(self, filename):
		states = []
		for idx, component in enumerate(self.components):
			try:
				state = component.read(filename)
				states.append(state)
			except Exception as e:
				if not self.silent:
					print("Component %i failed reading\n%s" % (idx+1, e))
		return get_most_frequent(states)

	# Spaghetti zone
	def write(self, filename, grain_state):
		lengths = []
		for idx, component in enumerate(self.components):
			try:
				length = component.write(filename, grain_state)
				lengths.append(length)
			except Exception as e:
				if not self.silent:
					print("Component %i failed writing\n%s" % (idx+1, e))
		return get_most_frequent(lengths)

	def clear(self, filename):
		for idx, component in enumerate(self.components):
			try:
				component.clear(filename)
			except Exception as e:
				if not self.silent:
					print("Component %i failed clearing\n%s" % (idx+1, e))


class RecoveryBlock():

	def __init__(self, components, silent=True):
		self.components = components
		self.silent = silent

	def read(self, filename):
		for component_idx, component in enumerate(self.components):
			try:
				result = component.read(filename)
				return result
			except Exception as e:
				if not self.silent:
					print("Component %d failed: %s" % (component_idx+1, e))
		# If all components fail
		return None

	def write(self, filename, grain_state):
		for component_idx, component in enumerate(self.components):
			try:
				result = component.write(filename, grain_state)
				return result
			except Exception as e:
				if not self.silent:
					print("Component %d failed: %s" % (component_idx+1, e))
		# If all components fail
		return None

	def clear(self, filename):
		for component_idx, component in enumerate(self.components):
			try:
				component.clear(filename)
			except Exception as e:
				if not self.silent:
					print("Component %d failed: %s" % (component_idx+1, e))


class Baseline():

	def __init__(self, component, silent=True):
		self.component = component
		self.silent = silent

	def read(self, filename):
		try:
			result = self.component.read(filename)
			return result
		except Exception as e:
			if not self.silent:
				print(e)
			return None

	def write(self, filename, grain_state):
		try:
			self.component.write(filename, grain_state)
		except Exception as e:
			if not self.silent:
				print(e)
			return None

	def clear(self, filename):
		try:
			self.component.clear(filename)
		except Exception as e:
			if not self.silent:
				print(e)