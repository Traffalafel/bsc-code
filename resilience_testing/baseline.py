
class Baseline():
	def __init__(self, version, silent=True):
		self.version = version
		self.silent = silent

	def read(self, state_id):
		try:
			result = self.version.read(state_id)
			return result
		except Exception as e:
			if not self.silent:
				print("Baseline failed reading: ", e)
			return None

	def write(self, state_id, state_value):
		try:
			self.version.write(state_id, state_value)
		except Exception as e:
			if not self.silent:
				print("Baseline failed writing: ", e)

	def clear(self, state_id):
		try:
			self.version.clear(state_id)
		except Exception as e:
			if not self.silent:
				print("Baseline failed clearing: ", e)
