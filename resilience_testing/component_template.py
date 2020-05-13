class Component():

	def __init__(self, directory):
		self.directory = directory

	def read(self, grain_id):
		pass

	def write(self, grain_id, state):
		pass

	def clear(self, grain_id):
		pass