import random
import string

# TODO: turn into a Python generator object

class WorkloadGenerator():

	def __init__(self, directory):
		self.directory = directory
		self.state = dict()

	def gen_new_value(self):
		possible_chars = list(string.ascii_letters)
		possible_chars += list(string.digits)
		output = ""
		length = random.randint(1, 10)
		for _ in range(length):
			output += random.choice(possible_chars)
		return output

	def get_existing_id(self):
		return random.choice(list(self.state.keys()))

	def gen_new_id(self):
		possible_chars = list(string.ascii_letters)
		possible_chars += list(string.digits)
		output = ""
		length = random.randint(1, 10)
		for _ in range(length):
			output += random.choice(possible_chars)
		return output

	def gen_write(self, grain_id, grain_val):
		path = "%s/%s" % (self.directory, grain_id)
		def write(file_storage):
			return file_storage.write(path, grain_val)
		return write

	def gen_read(self, grain_id):
		path = "%s/%s" % (self.directory, grain_id)
		def read(file_storage):
			return file_storage.read(path)
		return read

	# Returns (input, true_result)
	def next(self):

		if len(self.state.keys()) == 0:
			rnd = 0
		else:
			rnd = random.randint(0, 2)

		# Write to new grain
		if rnd == 0:
			new_id = self.gen_new_id()
			new_val = self.gen_new_value()
			self.state[new_id] = new_val
			return self.gen_write(new_id, new_val), len(new_val)

		# Overwrite existing grain
		if rnd == 1:
			grain_id = self.get_existing_id()
			new_val = self.gen_new_value()
			self.state[grain_id] = new_val
			return self.gen_write(grain_id, new_val), len(new_val)

		# Read from existing grain
		if rnd == 2:
			grain_id = self.get_existing_id()
			return self.gen_read(grain_id), self.state[grain_id]
