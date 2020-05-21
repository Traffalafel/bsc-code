
def get_most_frequent(elements):
	freqs = dict()
	for element in elements:
		freqs[element] = freqs.get(element, 0) + 1
	if len(freqs.keys()) == 0:
		return None
	else:
		return max(freqs, key=freqs.get)

class NVersionProgramming():
	def __init__(self, versions, silent=True):
		self.versions = versions
		self.silent = silent

	def read(self, state_id):
		results = []
		for version_idx, version in enumerate(self.versions):
			try:
				result = version.read(state_id)
				results.append(result)
			except Exception as e:
				if not self.silent:
					print("Version %d failed reading: %s" % (version_idx+1, e))
		return get_most_frequent(results)

	def write(self, state_id, state_value):
		lengths = []
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
