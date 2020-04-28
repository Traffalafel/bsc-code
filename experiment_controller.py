import os
import shutil
import sys
from fault_injection import FaultInjector
from workload_generator import WorkloadGenerator
import file_storage

# Returns array of component sources
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
def save_package_src(package_src, name):
	if os.path.exists(name):
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


def main(*args):

	# Create broken components
	components_src = load_package_src('components')
	fi = FaultInjector()	
	for idx, _ in enumerate(components_src):
		components_src[idx] = fi.inject_faults(components_src[idx])
	save_package_src(components_src, 'components_broken')

	# Create file storage from broken components
	components = file_storage.load_components("components_broken", silent=False)
	nvp = file_storage.NVPStrategy()
	fs = file_storage.FileStorage(nvp, components)

	# Create auxillary objects
	# TODO: clear data directory before starting experiment
	clear_directory("./data")
	wg = WorkloadGenerator("./data")
	fl = FailureLogger()

	# Test file storage
	for idx in range(20):
		command, true_result = wg.next()
		result = command(fs)
		if result != true_result:
			fl.log_failure()
	
	print("Number of failures: %d" % fl.num_failures)

if __name__ == '__main__':
		main(sys.argv)
