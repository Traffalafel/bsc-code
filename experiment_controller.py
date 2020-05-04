import os
import shutil
import sys
from fault_injection import FaultInjector
from workload_generator import WorkloadGenerator
from file_storage import FileStorage, NVPStrategy, Baseline
import importlib
import pkgutil
import random
import py_compile
from multiprocessing import Process, Queue
import matplotlib.pyplot as plt


def load_components(package_name, silent=True):
	components = []
	for component in pkgutil.iter_modules([package_name]):
		try:
			path = os.path.join(".", package_name, component.name + ".py")
			py_compile.compile(path, doraise=True)
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

def run_experiment(target, workload_generator, out_queue):
	failure_count = 0
	for command, true_result in workload_generator:
		result = command(target)
		if result != true_result:
			failure_count += 1
	out_queue.put(failure_count)

def generate_seed():
	return random.randint(-sys.maxsize-1, sys.maxsize)

def barplot_bins(failures, remove_outliers=True):
	freqs = dict()
	for f in failures:
		freqs[f] = freqs.get(f, 0) + 1
	keys = list(freqs.keys())
	vals = list(freqs.values())
	return keys, vals
	# indices = list(range(len(keys)))
	# indices.remove(keys.index(min(keys)))
	# indices.remove(keys.index(max(keys)))
	# if remove_outliers:
	# 	return [keys[i] for i in indices], [vals[i] for i in indices]
	# else:
	# 	return keys, vals

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
	seed = generate_seed()
	
	nvp_strat = NVPStrategy(silent=True)
	nvp = FileStorage(nvp_strat, [], "./data/nvp")
	bl = Baseline(None, "./data/bl")
	targets = [nvp, bl]
	failures = [[] for _ in targets]

	for idx in range(num_experiments):

		print("Experiment no. %d" % (idx+1))

		clear_directory("./data/nvp")
		clear_directory("./data/bl")

		# Create new broken components
		break_components('components', 'components_broken', fi)
		components = load_components("components_broken", silent=True)
		nvp.set_components(components)
		bl.set_component(components[0])
		
		wg = WorkloadGenerator(workload_size, seed=seed)

		for target_idx, target in enumerate(targets):
			queue = Queue()
			p = Process(target=run_experiment, args=(target, wg, queue,))
			p.start()
			p.join()
			p.kill()
			if not queue.empty(): # Avoids deadlock
				num_failures = queue.get()
			else:
				num_failures = None
			failures[target_idx].append(num_failures)
			wg.reset()

	# x, heights = barplot_bins(failures)
	# plt.bar(x, heights)
	# plt.show()
	print(failures)

if __name__ == '__main__':
	main(sys.argv)
