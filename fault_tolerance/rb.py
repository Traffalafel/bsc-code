from .module_loading import load_modules
import os

class VersionsTrust():
	def __init__(self, versions):
		self.versions = versions
		self.trust = [0 for v in self.versions]

	def increment(self, version_idx):
		self.trust[version_idx] += 1

	def decrement(self, version_idx):
		self.trust[version_idx] -= 1

	def rearrange(self):
		idxs = sorted(range(len(self.trust)), key=lambda x: self.trust[x], reverse=True)
		self.versions = [self.versions[i] for i in idxs]
		self.trust = [self.trust[i] for i in idxs]

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
		self.read_versions = VersionsTrust(self.versions)
		self.write_versions = VersionsTrust(self.versions)
		self.clear_versions = VersionsTrust(self.versions)

	# Rearranges the order of versions according to their levels of trust
	def rearrange(self):
		idxs = sorted(range(len(self.trust)), key=lambda x: self.trust[x], reverse=True)
		self.versions = [self.versions[i] for i in idxs]
		self.trust = [self.trust[i] for i in idxs]

	def read(self, state_id):
		self.read_versions.rearrange()
		for version_idx, version in enumerate(self.read_versions.versions):
			try:
				result = version.read(state_id)
				self.read_versions.increment(version_idx)
				return result
			except Exception as e:
				self.read_versions.decrement(version_idx)
				if not self.silent:
					print("RB: Version %d failed reading: %s" % (version_idx+1, e))
		# If all versions fail
		return None

	def write(self, state_id, state_value):
		self.write_versions.rearrange()
		for version_idx, version in enumerate(self.write_versions.versions):
			try:
				version.write(state_id, state_value)
				self.write_versions.increment(version_idx)
			except Exception as e:
				self.write_versions.decrement(version_idx)
				if not self.silent:
					print("RB: Version %d failed writing: %s" % (version_idx+1, e))

	def clear(self, state_id):
		self.clear_versions.rearrange()
		for version_idx, version in enumerate(self.clear_versions.versions):
			try:
				version.clear(state_id)
				self.clear_versions.increment(version_idx)
			except Exception as e:
				self.clear_versions.decrement(version_idx)
				if not self.silent:
					print("RB: Version %d failed clearing: %s" % (version_idx+1, e))
