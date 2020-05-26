import re
import string
import random
import sys


def sample_random_line(source: str):
	lines = source.split('\n')
	idx = random.randint(0, len(lines)-1)
	return idx, lines[idx]

def add_char(source: str):
	pos = random.randint(0, len(source))
	chars = list(string.ascii_letters)
	chars += list(string.digits)
	new_char = random.choice(chars)
	return source[:pos] + new_char + source[pos:]

def rm_char(source: str):
	pos = random.randint(0, len(source)-1)
	return source[:pos] + source[pos+1:]

def swap(source: str, idx_1, idx_2):
	lines = source.split("\n")
	tmp = lines[idx_1]
	lines[idx_1] = lines[idx_2]
	lines[idx_2] = tmp
	return "\n".join(lines)

def swap_lines(source: str):
	idx_1, _ = sample_random_line(source)
	idx_2, _ = sample_random_line(source)
	while idx_2 == idx_1:
		idx_2, _ = sample_random_line(source)
	return swap(source, idx_1, idx_2)

def dup_line(source: str):
	idx, _ = sample_random_line(source)
	lines = source.split("\n")
	lines = lines[:idx] + [lines[idx]] + lines[idx+1:]
	return "\n".join(lines)

def rm_line(source: str):
	idx, _ = sample_random_line(source)
	lines = source.split("\n")
	lines = lines[:idx] + lines[idx+1:]
	return "\n".join(lines)

class FaultInjector():

	def __init__(self):
		self.mutations = [add_char, rm_char, dup_line, swap_lines, rm_line]

	def inject(self, source:str, num_mutations=1):
		src = source
		for i in range(num_mutations):
			mutation = random.choice(self.mutations)
			src = mutation(src)
		return src
		