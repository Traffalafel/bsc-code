import random
import string
import sys

class WorkloadGenerator():

	def __init__(self, workload_size, seed=None):
		self.size = workload_size
		self.state = dict()
		if seed is None:
			self.gen_new_seed()
		else:
			self.seed = seed
		self.restart()

	def gen_new_seed(self):
		self.seed = random.randint(-sys.maxsize-1, sys.maxsize)

	def restart(self,):
		self.count = 0
		self.random = random.Random(self.seed)

	def gen_new_value(self, max_length=10):
		possible_chars = list(string.ascii_letters)
		possible_chars += list(string.digits)
		possible_chars += list(string.punctuation)
		possible_chars += list(string.whitespace)
		output = ""
		length = self.random.randint(1, max_length)
		for _ in range(length):
			output += self.random.choice(possible_chars)
		return output

	def get_existing_id(self):
		return self.random.choice(list(self.state.keys()))

	def gen_new_id(self, max_length=10):
		possible_chars = list(string.ascii_letters)
		possible_chars += list(string.digits)
		output = ""
		length = self.random.randint(1, max_length)
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

		if self.count == self.size:
			raise StopIteration()
		self.count += 1

		if len(self.state.keys()) == 0:
			rnd = 0
		else:
			rnd = self.random.randint(0, 2)

		# Write to new grain
		if rnd == 0:
			new_id = self.gen_new_id(max_length=200)
			new_val = self.gen_new_value(max_length=1000)
			self.state[new_id] = new_val
			return self.gen_write(new_id, new_val), len(new_val)

		# Overwrite existing grain
		if rnd == 1:
			grain_id = self.get_existing_id()
			new_val = self.gen_new_value(max_length=1000)
			self.state[grain_id] = new_val
			return self.gen_write(grain_id, new_val), len(new_val)

		# Read from existing grain
		if rnd == 2:
			grain_id = self.get_existing_id()
			return self.gen_read(grain_id), self.state[grain_id]
