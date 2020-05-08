import os
import shutil
import sys
from fault_injection import FaultInjector
from workload_generator import WorkloadGenerator
from file_storage import FileStorage, NVPStrategy, RBStrategy, Baseline
import importlib
import pkgutil
import random
import py_compile
from multiprocessing import Process, Queue
import matplotlib.pyplot as plt
import json

def load_components(package_name, silent=True):
	components = []
	for component in pkgutil.iter_modules([package_name]):
		try:
			path = os.path.join(".", package_name, component.name + ".py")
			py_compile.compile(path, doraise=True)
			component_module = importlib.import_module(".%s" % component.name, package_name)
			if "Component" not in dir(component_module):
				continue
			component = component_module.Component()
			components.append(component)
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

def break_components(input_dir, output_dir, fault_injector):
	components_src = load_package_src(input_dir)
	for idx, _ in enumerate(components_src):
		components_src[idx] = fault_injector.inject(components_src[idx])
	return save_package_src(components_src, output_dir)

def process_fn(target, workload_generator, out_queue):
	failure_count = 0
	for command, true_result in workload_generator:
		result = command(target)
		if result != true_result:
			failure_count += 1
	out_queue.put(failure_count)

def test(target, workload_generator):
	queue = Queue()
	p = Process(target=process_fn, args=(target, workload_generator, queue,))
	p.start()
	p.join()
	p.kill()
	if not queue.empty(): # Avoids deadlock
		return queue.get()
	else:
		# If cannot get result set every I/O pair to failure
		return workload_generator.size

def test_multiple(targets, workload_generator):
	fails = []
	for target_idx, target in enumerate(targets):
		num_failures = test(target, workload_generator)
		fails.append(num_failures)
		workload_generator.restart()
	return fails

def save_results(obj, path):
	with open(path + ".json", "w+") as file:
		json.dump(obj, file,)

def load_results(path):
	with open(path, "r") as file:
		return json.load(file)

def resilience_test(num_experiments, workload_size):

	fi = FaultInjector()
	
	nvp_strat = NVPStrategy()
	rb_strat = RBStrategy()

	nvp_failures = []
	rb_failures = []
	baseline_failures = []

	for idx in range(num_experiments):

		# Reset data directories
		shutil.rmtree("data")

		# Create new broken components
		break_components('components', 'components_broken', fi)
		components = load_components("components_broken")

		# Inject resilience targets with new components
		nvp = FileStorage(nvp_strat, components, os.path.join("data", "nvp"))
		rb = FileStorage(rb_strat, components, os.path.join("data", "rb"))
		targets = [nvp, rb]

		# Create new baselines
		baselines = []
		for component_idx, component in enumerate(components):
			data_dir = os.path.join("data", "baseline", str(component_idx))
			baselines.append(Baseline(component, data_dir))

		# Logging information about experiment
		print("Experiment no. %d" % (idx+1))
		
		wg = WorkloadGenerator(workload_size)

		# Test targets
		target_failures = test_multiple(targets, wg)
		nvp_failures.append(target_failures[0])
		rb_failures.append(target_failures[1])

		# Test baselines
		baseline_failures += test_multiple(baselines, wg)

	return nvp_failures, rb_failures, baseline_failures

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

	nvp_failures, rb_failures, baseline_failures = resilience_test(num_experiments, workload_size)

	# Log results
	print("NVP failures: ", nvp_failures)
	print("RB failures: ", rb_failures)
	print("Baseline failures: ", baseline_failures)

	suffix = "_%d_%d" % (num_experiments, workload_size)
	save_results(nvp_failures, os.path.join("results", "nvp%s" % suffix))
	save_results(rb_failures, os.path.join("results", "rb%s" % suffix))
	save_results(baseline_failures, os.path.join("results", "baseline%s" % suffix))

if __name__ == '__main__':
	main(sys.argv)
