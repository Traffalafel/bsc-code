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
	cmd = args[3]
	
	try:
		component = load_component(component_module, data_dir)
	except Exception as e:
		print("Was not able to load component: ", e)

	if (cmd == "read"):
		try:
			result = component.read(args[4])
			print(result)
		except Exception as e:
			print("")
		return

	if (cmd == "write"):
		try:
			component.write(args[4], args[5])
		except Exception as e:
			print("Error: ", e)
		return

	if (cmd == "clear"):
		try:
			component.clear(args[4])
		except Exception as e:
			print("Error: ", e)
		return

if __name__ == "__main__":
	main(sys.argv)
