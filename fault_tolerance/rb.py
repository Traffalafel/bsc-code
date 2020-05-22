from .version_loading import load_modules
import os

class RecoveryBlock():
	def __init__(self, versions_package, data_dir, silent=True):
		self.silent = silent
		self.versions = []
		modules = load_modules(versions_package, silent)
		for module_idx, module in enumerate(modules):
			try:
				version = module.Database(data_dir)
				self.versions.append(version)
			except Exception as e:
				if not self.silent:
					print("RB: Failed to load version %d: %s" % (module_idx, e))

	def read(self, state_id):
		for version_idx, version in enumerate(self.versions):
			try:
				result = version.read(state_id)
				return result
			except Exception as e:
				if not self.silent:
					print("RB: Version %d failed reading: %s" % (version_idx+1, e))
		# If all versions fail
		return None

	def write(self, state_id, state_value):
		for version_idx, version in enumerate(self.versions):
			try:
				version.write(state_id, state_value)
			except Exception as e:
				if not self.silent:
					print("RB: Version %d failed writing: %s" % (version_idx+1, e))

	def clear(self, state_id):
		for version_idx, version in enumerate(self.versions):
			try:
				version.clear(state_id)
			except Exception as e:
				if not self.silent:
					print("RB: Version %d failed clearing: %s" % (version_idx+1, e))
