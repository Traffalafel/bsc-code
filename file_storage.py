import importlib
import pkgutil
import sys
import os

class NVPStrategy():

	def __init__(self, silent=True):
		self.silent = silent

	def read(self, components, filename):
		values = []
		for idx, component in enumerate(components):

			try:
				value = component.read(filename)
				values.append(value)
			except Exception as e:
				if not self.silent:
					print("Component %i failed reading\n%s" % (idx+1, e))
		
		# Get the most frequent value
		values_freq = dict()
		for value in values:
			values_freq[value] = values_freq.get(value, 0) + 1
		if len(values_freq.keys()) == 0:
			# No components were able to perform service
			return None
		else:
			return max(values_freq, key=values_freq.get)

	# Spaghetti zone
	def write(self, components, filename, value):
		lengths = []
		for idx, component in enumerate(components):
			try:
				length = component.write(filename, value)
				lengths.append((component, length))
			except Exception as e:
				if not self.silent:
					print("Component %i failed writing\n%s" % (idx+1, e))
		# Find correct output
		lengths_freq = dict()
		for _, length in lengths:
			lengths_freq[length] = lengths_freq.get(length, 0) + 1
		if len(lengths_freq.keys()) == 0:
			# No components were able to perform service
			return None
		plurality_length = max(lengths_freq, key=lengths_freq.get)
		final_component = next(component for component, length in lengths if length==plurality_length)
		final_component.write(filename, value)
		return plurality_length

class RBStrategy():

	def __init__(self, silent=True):
		self.silent = silent

	def read(self, components, filename):
		pass

	def write(self, components, filename, value):
		pass


class Baseline():

	def __init__(self, component, data_dir, silent=True):
		self.__component = component
		self.data_dir = data_dir
		if not os.path.exists(data_dir):
			os.makedirs(data_dir)
		self.silent = silent

	def set_component(self, component):
		self.__component = component

	def read(self, filename):
		path = os.path.join(self.data_dir, filename)
		try:
			result = self.__component.read(path)
			return result
		except Exception as e:
			if not self.silent:
				print(e)
			return None

	def write(self, filename, value):
		path = os.path.join(self.data_dir, filename)
		try:
			self.__component.write(path, value)
		except Exception as e:
			if not self.silent:
				print(e)
			return None


class FileStorage():

	def __init__(self, ft_strategy, components, data_dir):
		self.__components = components
		self.data_dir = data_dir
		self.ft_strategy = ft_strategy

	def set_components(self, components):
		self.__components = components

	def read(self, filename):
		path = os.path.join(self.data_dir, filename)
		return self.ft_strategy.read(self.__components, path)

	def write(self, filename, value):
		path = os.path.join(self.data_dir, filename)
		return self.ft_strategy.write(self.__components, path, value)
