import os
from .module_loading import load_modules

def get_most_frequent(elements):
	freqs = dict()
	for element in elements:
		freqs[element] = freqs.get(element, 0) + 1
	if len(freqs.keys()) == 0:
		return None
	else:
		return max(freqs, key=freqs.get)

class NVersionProgramming():
	def __init__(self, versions_package, data_dir, silent=True):
		self.silent = silent
		self.versions = []
		modules = load_modules(versions_package, silent)
		for module_idx, module in enumerate(modules):
			try:
				version_data_dir = os.path.join(data_dir, str(module_idx))
				version = module.Database(version_data_dir)
				self.versions.append(version)
			except Exception as e:
				if not self.silent:
					print("NVP: Failed to load version %d: %s" % (module_idx, e))

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
