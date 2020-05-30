import os
from .module_loading import load_modules
import random

def get_most_frequent(elements):
	freqs = dict()
	for element in elements:
		freqs[element] = freqs.get(element, 0) + 1
	if len(freqs.keys()) == 0:
		return None
	else:
		max_freq = max(freqs.values())
		max_elements = [k for k in freqs.keys() if freqs[k] == max_freq]
		if len(max_elements) == 1:
			output = max_elements[0]
		else:
			# Tie
			output = random.choice(max_elements)
		return output

class NVersionProgramming():
	def __init__(self, versions, data_dir, silent=True):
		self.silent = silent
		self.versions = versions
		self.num_versions = len(versions)
		self.data_dir = data_dir
		for idx, version in enumerate(self.versions):
			# Reconfigure data directory for versions
			version_dir = os.path.join(data_dir, str(idx))
			if not os.path.exists(version_dir):
				os.makedirs(version_dir)
			version.data_dir = version_dir

	def read(self, state_id):
		results = []
		for version_idx, version in enumerate(self.versions):
			try:
				result = version.read(state_id)
				results.append(result)
			except Exception as e:
				if not self.silent:
					print("NVP: Version %d failed reading: %s" % (version_idx+1, e))
		return get_most_frequent(results)

	def write(self, state_id, state_value):
		lengths = []
		for version_idx, version in enumerate(self.versions):
			try:
				version.write(state_id, state_value)
			except Exception as e:
				if not self.silent:
					print("NVP: Version %d failed writing: %s" % (version_idx+1, e))

	def clear(self, state_id):
		for version_idx, version in enumerate(self.versions):
			try:
				version.clear(state_id)
			except Exception as e:
				if not self.silent:
					print("NVP: Version %d failed clearing: %s" % (version_idx+1, e))
