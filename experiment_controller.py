import os
import shutil
import sys
from fault_injection import FaultInjector
from workload_generator import WorkloadGenerator
from file_storage import FileStorage, NVPStrategy
import importlib
import pkgutil

import threading
import asyncio

def load_components(package_name, silent=True):
	components = []
	for component in pkgutil.iter_modules([package_name]):
		try:
			component_module = importlib.import_module(".%s" % component.name, package_name)
			components.append(component_module.Component())
			if not silent:
				print("Successfully imported component %s" % component.name)
		except Exception as e:
			if not silent:
				print("Failed to import component '%s'\n%s" % (component.name, e))
	return components

def load_package_src(name):
	files = os.listdir(name)
	files = [file for file in files if file[-3:] == '.py' and file != '__init__.py']
	components_src = []
	for file in files:
		path = "%s/%s" % (name, file)
		with open(path, 'r', encoding='utf-8') as fd:
			src = fd.read()
			components_src.append(src)
	return components_src

# Saves the source of a package
def save_package_src(package_src, name, silent=True):
	if os.path.exists(name):
		if not silent:
			print('Warning: Deleting pre-existing directory %s to make room for new package' % name)
		shutil.rmtree(name)
	os.makedirs(name)
	open('%s/__init__.py' % name, 'w+').close() # Create __init__.py
	for idx, component_src in enumerate(package_src):
		with open('%s/component_%d.py' % (name, idx+1), 'w+', encoding='utf-8') as fd:
			fd.write(component_src)

def clear_directory(path):
	for filename in os.listdir(path):
		file_path = os.path.join(path, filename)
		os.remove(file_path)

def count_open_files(path):
	for filename in os.listdir(path):
		file_path = os.path.join(path, filename)
		print(os.access(file_path, os.W_OK))

class FailureLogger():

	def __init__(self, silent=True):
		self.silent = silent
		self.num_failures = 0

	def log_failure(self):
		self.num_failures += 1
		if not self.silent:
			print("Failure detected")


def break_components(input_dir, output_dir, fault_injector):
	components_src = load_package_src(input_dir)
	for idx, _ in enumerate(components_src):
		components_src[idx] = fault_injector.inject(components_src[idx])
	return save_package_src(components_src, output_dir)

def run_experiment(target, workload_size, workload_generator):
	failure_count = 0
	for _ in range(workload_size):
		command, true_result = workload_generator.next()
		result = command(target)
		if result != true_result:
			failure_count += 1
	return failure_count

def main(args):

	if len(args) != 3:
		print("Usage: experiment_controller.py <num_experiments> <workload_size>")
		return
	
	try:
		num_experiments = int(args[1])
	except:
		print("num_experiments must be number")
		return
	try:
		workload_size = int(args[2])
	except:
		print("workload_size must be number")
		return

	fi = FaultInjector()
	failures = []

	for idx in range(num_experiments):

		print("Experiment no. %d" % idx)

		count_open_files("./data")
		clear_directory("./data")
		wg = WorkloadGenerator("./data")

		# Break components
		break_components('components', 'components_broken', fi)
		# Create file storage from broken components
		components = load_components("components_broken", silent=False)
		nvp = NVPStrategy(silent=False)
		fs = FileStorage(nvp, components)
		experiment_failures = run_experiment(fs, workload_size, wg)
		failures.append(experiment_failures)

	print(failures)

if __name__ == '__main__':
	main(sys.argv)
