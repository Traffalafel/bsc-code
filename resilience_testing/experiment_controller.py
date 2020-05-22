import os
import sys
import random
import py_compile
from multiprocessing import Process, Queue
import json
import shutil

from fault_tolerance.nvp import NVersionProgramming
from fault_tolerance.rb import RecoveryBlock
from fault_tolerance.version_loading import load_modules

from source_loading import load_package_src, save_package_src
from fault_injection import FaultInjector
from workload_generator import WorkloadGenerator
from baseline import Baseline

def break_versions(input_dir, output_dir, fault_injector):
	versions_src = load_package_src(input_dir)
	for idx, _ in enumerate(versions_src):
		versions_src[idx] = fault_injector.inject(versions_src[idx])
	return save_package_src(versions_src, output_dir)

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

def resilience_test(num_experiments, workload_size, versions_dir, data_dir, results_dir):

	fi = FaultInjector()

	nvp_failures = []
	rb_failures = []
	baseline_failures = []

	for idx in range(num_experiments):

		# Logging information about experiment
		print("Experiment no. %d" % (idx+1))

		# Reset data directories
		if os.path.exists(data_dir):
			shutil.rmtree(data_dir)

		# Create new broken versions
		break_versions(versions_dir, 'versions_broken', fi)
		modules_broken = load_modules("versions_broken")

		# Inject resilience targets with new versions
		nvp_dir = os.path.join(data_dir, 'nvp')
		nvp = NVersionProgramming('versions_broken', nvp_dir)
		rb_dir = os.path.join(data_dir, 'rb')
		rb = RecoveryBlock('versions_broken', rb_dir)
		targets = [nvp, rb]

		# Create baselines
		baselines = []
		modules = load_modules('versions_broken')
		for module_idx, module in enumerate(modules):
			try:
				baseline_data_dir = os.path.join(data_dir, 'baseline', str(module_idx))
				version = module.Database(baseline_data_dir)
				baselines.append(Baseline(version))
			except:
				pass
		
		wg = WorkloadGenerator(workload_size)

		# Test targets
		target_failures = test_multiple(targets, wg)
		nvp_failures.append(target_failures[0])
		rb_failures.append(target_failures[1])

		# Test baselines
		baseline_failures += test_multiple(baselines, wg)

	return nvp_failures, rb_failures, baseline_failures

def main(args):
	if len(args) != 6:
		print("Usage: experiment_controller.py <num_experiments> <workload_size> <versions_dir> <data_dir> <results_dir>")
		return
	try:
		num_experiments = int(args[1])
		workload_size = int(args[2])
		versions_dir = args[3]
		data_dir = args[4]
		results_dir = args[5]
	except Exception as e:
		print("Inputted formatted incorrectly:\n", e)
		return

	results = resilience_test(num_experiments, workload_size, versions_dir, data_dir, results_dir)
	nvp_failures, rb_failures, baseline_failures = results

	# Log results
	print("NVP failures: ", nvp_failures)
	print("RB failures: ", rb_failures)
	print("Baseline failures: ", baseline_failures)

	if not os.path.exists(results_dir):
		os.makedirs(results_dir)
	suffix = "_%d_%d" % (num_experiments, workload_size)
	save_results(nvp_failures, os.path.join(results_dir, "nvp%s" % suffix))
	save_results(rb_failures, os.path.join(results_dir, "rb%s" % suffix))
	save_results(baseline_failures, os.path.join(results_dir, "baseline%s" % suffix))

if __name__ == '__main__':
	main(sys.argv)
