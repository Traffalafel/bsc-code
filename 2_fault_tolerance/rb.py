
class RecoveryBlock():
	def __init__(self, versions, silent=True):
		self.versions = versions
		self.silent = silent

	def read(self, state_id):
		for version_idx, version in enumerate(self.versions):
			try:
				result = version.read(state_id)
				return result
			except Exception as e:
				if not self.silent:
					print("Version %d failed reading: %s" % (version_idx+1, e))
		# If all versions fail
		return None

	def write(self, state_id, state_value):
		for version_idx, version in enumerate(self.versions):
			try:
				version.write(state_id, state_value)
			except Exception as e:
				if not self.silent:
					print("Version %d failed writing: %s" % (version_idx+1, e))

	def clear(self, state_id):
		for version_idx, version in enumerate(self.versions):
			try:
				version.clear(state_id)
			except Exception as e:
				if not self.silent:
					print("Version %d failed clearing: %s" % (version_idx+1, e))
