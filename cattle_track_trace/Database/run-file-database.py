import sys
import fileinput
import importlib

import fault_tolerance

def load_component(module_name, data_dir):
	module = importlib.import_module(module_name)
	return module.Component(data_dir)

def main(args):
	data_dir = args[1]
	component_module = args[2]

	try:
		component = load_component(component_module, data_dir)
	except Exception as e:
		print("Was not able to load component: ", e)
		return

	for line in sys.stdin:
		content = line[:-1]
		args = content.split(" ")
		cmd = args[0]

		with open("stdin", "w+") as f:
			f.write(content)
			
		if cmd == "read":
			try:
				result = component.read(args[1])
				output = result + '\n'
			except Exception as e:
				output = 'Nothing found\n'
			sys.stdout.write(output)
			with open('stdout', 'w+') as f:
				f.write(output)

		if cmd == "write":
			try:
				component.write(args[1], args[2])
			except Exception as e:
				print("Error: ", e)

		if cmd == "clear":
			try:
				component.clear(args[1])
			except Exception as e:
				print("Error: ", e)

		if cmd == "exit":
			return

if __name__ == "__main__":
	main(sys.argv)
