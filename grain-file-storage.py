import importlib
import sys

class NBlockStrategy():

	def read(self, components, filename):
		values = []
		for idx, component in enumerate(components):
			try:
				value = component.read(filename)
				values.append(value)
			except Exception as e:
				print("Component %i failed" % (idx+1))
		# Get the most frequent value
		values_freq = dict()
		for value in values:
			if value not in values_freq:
				values_freq[value] = 1
			else:
				values_freq[value] += 1
		return max(values_freq, key=values_freq.get)

	# Spaghetti zone
	def write(self, components, filename, value):
		lengths = []
		for idx, component in enumerate(components):
			try:
				length = component.write(filename, value)
				lengths.append((component, length))
			except Exception as e:
				print("Component %i failed" % (idx+1))
		lengths_freq = dict()
		for _, length in lengths:
			if length not in lengths_freq:
				lengths_freq[length] = 1
			else:
				lengths_freq[length] += 1
		plurality_length = max(lengths_freq, key=lengths_freq.get)
		final_component = next(component for component, length in lengths if length==plurality_length)
		final_component.write(filename, value)

class Baseline():

	def __init__(self):
		pass

class FileStorage():

	def __init__(self, ft_algorithm):
		pass

class FileStorage():

	def __init__(self):
		self.inhabitants = []
		for i in range(4):
			inhab_name = "inhabitants.inhabitant_%i" % (i+1)
			try:
				inhabitant = importlib.import_module(inhab_name)
				self.inhabitants.append(inhabitant.GrainFileStorage())
			except Exception as e:
				print("Failed to import component '%s'\n%s" % (inhab_name, e))

	def read(self, filename):
		for i in range(len(self.inhabitants)):
			try:
				value = self.inhabitants[i].read(filename)
				return value
			except Exception as e:
				print("Component %i failed\n%s" % (i, e))

	def write(self, filename, value):
		for i in range(len(self.inhabitants)):
			try:
				self.inhabitants[i].write(filename, value)
				return
			except Exception as e:
				print("Component %i failed\n%s" % (i, e))

def main(*args):
	fs = FileStorage()
	nv = NBlockStrategy()
	nv.write(fs.inhabitants, "greeting.txt", "niiiii huuuuu")

if __name__ == "__main__":
	main(sys.argv)