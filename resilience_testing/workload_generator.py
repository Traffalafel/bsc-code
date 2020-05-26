import random
import string
import sys

class WorkloadGenerator():

	def __init__(self, workload_size, seed=None):
		self.operations = [self.read, self.write_new, self.write_existing, self.clear]
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

	def sample_existing_id(self):
		return self.random.choice(list(self.state.keys()))

	def gen_new_id(self, max_length=10):
		possible_chars = list(string.ascii_letters)
		possible_chars += list(string.digits)
		output = ""
		length = self.random.randint(1, max_length)
		for _ in range(length):
			output += self.random.choice(possible_chars)
		return output

	def read(self):
		grain_id = self.sample_existing_id()
		def read_op(database):
			return database.read(grain_id)
		return read_op, self.state[grain_id]

	def write_existing(self):
		grain_id = self.sample_existing_id()
		new_val = self.gen_new_value(max_length=1000)
		self.state[grain_id] = new_val
		def write_op(database):
			return database.write(grain_id, new_val)
		return write_op, None

	def write_new(self):
		new_id = self.gen_new_id(max_length=100)
		new_val = self.gen_new_value(max_length=1000)
		self.state[new_id] = new_val
		def write_op(database):
			return database.write(new_id, new_val)
		return write_op, None

	def clear(self):
		grain_id = self.sample_existing_id()
		del self.state[grain_id]
		def clear_op(database):
			return database.clear(grain_id)
		return clear_op, None

	def __iter__(self):
		return self

	# Returns (input, true_result)
	def __next__(self):

		if self.count == self.size:
			raise StopIteration()
		self.count += 1

		if len(self.state.keys()) == 0:
			operation = self.write_new
		else:
			operation = self.random.choice(self.operations)
		return operation()
