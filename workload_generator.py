import random
import string
import sys

# TODO: turn into a Python generator object

class WorkloadGenerator():

	def __init__(self, workload_size, seed):
		self.size = workload_size
		self.state = dict()
		self.seed = seed
		self.reset()

	def reset(self,):
		self.count = 0
		self.random = random.Random(self.seed)

	def gen_new_value(self):
		possible_chars = list(string.ascii_letters)
		possible_chars += list(string.digits)
		output = ""
		length = self.random.randint(1, 10)
		for _ in range(length):
			output += self.random.choice(possible_chars)
		return output

	def get_existing_id(self):
		return self.random.choice(list(self.state.keys()))

	def gen_new_id(self):
		possible_chars = list(string.ascii_letters)
		possible_chars += list(string.digits)
		output = ""
		length = self.random.randint(1, 10)
		for _ in range(length):
			output += self.random.choice(possible_chars)
		return output

	def gen_write(self, grain_id, grain_val):
		def write(file_storage):
			return file_storage.write(grain_id, grain_val)
		return write

	def gen_read(self, grain_id):
		def read(file_storage):
			return file_storage.read(grain_id)
		return read

	def __iter__(self):
		return self

	# Returns (input, true_result)
	def __next__(self):

		self.count += 1
		if self.count == self.size:
			raise StopIteration()

		if len(self.state.keys()) == 0:
			rnd = 0
		else:
			rnd = self.random.randint(0, 2)

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
