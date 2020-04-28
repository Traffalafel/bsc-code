import re
import string
import random
import sys

def find_commands(source: str):
	commands = []
	line_nums = []
	lines = source.split("\n")
	for idx, line in enumerate(lines):
		if not re.match("([\t ]*def )|([\t ]*class )", line) and not line_empty(line):
			commands.append(line)
			line_nums.append(idx)
	return commands, line_nums

def line_empty(line: str):
	return not bool(line.strip())

def random_line(source: str):
	cmds, line_nums = find_commands(source)
	idx = random.randint(0, len(cmds)-1)
	return cmds[idx], line_nums[idx]

def trim_indent(line: str):
	stripped = line.lstrip()
	len_indent = len(line) - len(stripped)
	return stripped, len_indent

def line_offset(source: str, line_num: int):
	lines = source.split("\n")
	offset = sum(len(line) for line in lines[:line_num-1])
	offset += line_num - 1
	_, len_indent = trim_indent(lines[line_num-1])
	offset += len_indent
	return offset

def insert_char(source: str):
	cmd, line_num = random_line(source)
	offset = line_offset(source, line_num)
	cmd = cmd.lstrip()
	new_pos = offset + random.randint(0, len(cmd))
	chars = list(string.ascii_letters)
	chars += list(string.digits)
	new_char = random.choice(chars)
	return source[:new_pos] + new_char + source[new_pos:]

def swap_lines(source: str, line_num_1, line_num_2):
	lines = source.split("\n")
	tmp = lines[line_num_1]
	lines[line_num_1] = lines[line_num_2]
	lines[line_num_2] = tmp
	return "\n".join(lines)

def swap_commands(source: str):
	_, line_num_1 = random_line(source)
	_, line_num_2 = random_line(source)
	while line_num_2 == line_num_1:
		_, line_num_2 = random_line(source)
	return swap_lines(source, line_num_1, line_num_2)

class FaultInjector():

	def __init__(self):
		self.mutations = [insert_char, swap_commands]

	# Regenerate the fault that is going to be injected
	def regenerate(self):
		pass

	# Log a description of the fault sequence being injected
	def log_fault(self):
		pass

	def inject_faults(self, source: str):
		mutation = random.choice(self.mutations)
		return mutation(source)

def main(*args):
	s = """
def hejsa():
    hva så
    ikk så meget
class dinmor():
	def __init__(self):
		self.dinmor = 'ost' """
	print(s)
	print(find_commands(s))
	print(swap_lines(s, 0, 1))

if __name__ == "__main__":
		main(sys.argv)