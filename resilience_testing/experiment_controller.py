import os
import sys
import random
import py_compile
from multiprocessing import Process, Queue
import json
import shutil

from fault_tolerance.nvp import NVersionProgramming
from fault_tolerance.rb import RecoveryBlock
from fault_tolerance.module_loading import load_modules

from source_loading import load_package_src, save_package_src
from fault_injection import FaultInjector
from workload_generator import WorkloadGenerator
from baseline import Baseline

def break_versions(input_dir, output_dir, fault_injector, num_bypass=0):
	assert(num_bypass >= 0)
	versions_src = load_package_src(input_dir)
	num_versions = len(versions_src)
	if num_bypass != 0:
		bypass_idxs = random.sample(range(num_versions), k=num_bypass)
	else:
		bypass_idxs = []
	bypassed_src = [versions_src[i] for i in bypass_idxs]
	break_idxs = [i for i in range(num_versions) if i not in bypass_idxs]
	break_src = [versions_src[i] for i in break_idxs]
	broken_src = []
	for v in break_src:
		broken_src.append(fault_injector.inject(v))

	output = []
	for v in versions_src:
		output.append(fault_injector.inject(v))

	save_package_src(output, output_dir)

def process_fn(target, workload_generator, out_queue):
	num_failures = 0
	num_read = 0
	for operation, true_result in workload_generator:
		try:
			actual_result = operation(target)
		except:
			actual_result = None
		if true_result == None:
			continue
		num_read += 1
		if ((actual_result == None) or (len(actual_result) != len(true_result))):
			num_failures += 1
	out_queue.put(num_failures/num_read)

def test(target, workload_generator):
	queue = Queue()
	p = Process(target=process_fn, args=(target, workload_generator, queue))
	p.start()
	p.join()
	p.kill()
	if not queue.empty(): # Avoids deadlock
		return queue.get()
	else:
		# If cannot get result set every I/O pair to failure
		return 1.0

def test_multiple(targets, workload_generator):
	results = []
	for target_idx, target in enumerate(targets):		
		queue = Queue()
		p = Process(target=process_fn, args=(target, workload_generator, queue))
		p.start()
		p.join()
		p.kill()
		if not queue.empty(): # Avoids deadlock
			r = queue.get()
		else:
			# If cannot get result set every I/O pair to failure
			r = workload_generator.size
		results.append(r)
		workload_generator.restart()
	return results

def save_results(obj, path):
	with open(path + ".json", "w+") as file:
		json.dump(obj, file,)

def load_results(path):
	with open(path, "r") as file:
		return json.load(file)

def resilience_test(num_experiments, workload_size, versions_dir, data_dir, results_dir, num_bypass):

	fi = FaultInjector()

	nvp_results = []
	rb_results = []
	baseline_results = []

	for idx in range(num_experiments):

		# Logging information about experiment
		print("Experiment no. %d" % (idx+1))

		# Reset data directories
		if os.path.exists(data_dir):
			shutil.rmtree(data_dir, ignore_errors=True)

		# Create new broken versions
		break_versions(versions_dir, 'versions_broken', fi, num_bypass=num_bypass)
		modules_broken = load_modules("versions_broken")

		# Create target databases with broken components
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
			except Exception as e:
				pass

		targets
		
		wg = WorkloadGenerator(workload_size)

		# Test targets
		target_results = test_multiple(targets, wg)	
		nvp_results.append(target_results[0])
		rb_results.append(target_results[1])

		# Test baselines
		baseline_results += test_multiple(baselines, wg)

	return nvp_results, rb_results, baseline_results

def count(results, value):
	return len([r for r in results if r == value]) 

def percentage(a, b):
	return (a/b) * 100

def main(args):
	if len(args) != 7:
		print("Usage: experiment_controller.py <num_experiments> <workload_size> <versions_dir> <data_dir> <results_dir> <num_bypass>")
		return
	try:
		num_experiments = int(args[1])
		workload_size = int(args[2])
		versions_dir = args[3]
		data_dir = args[4]
		results_dir = args[5]
		num_bypass = int(args[6])
	except Exception as e:
		print("Inputted formatted incorrectly:\n", e)
		return

	results = resilience_test(num_experiments, workload_size, versions_dir, data_dir, results_dir, num_bypass)
	nvp_results, rb_results, baseline_results = results

	nvp_failures = count(nvp_results, 1.0)
	rb_failures = count(rb_results, 1.0)
	baseline_failures = count(baseline_results, 1.0)

	# Log number of failures
	print("NVP failures: %d of %d (%f %%)" % (nvp_failures, len(nvp_results), percentage(nvp_failures, len(nvp_results))) )
	print("RB failures: %d of %d (%f %%)" % (rb_failures, len(rb_results), percentage(rb_failures, len(rb_results))))
	print("Baseline failures: %d of %d (%f %%)" % (baseline_failures, len(baseline_results), percentage(baseline_failures, len(baseline_results))))

	# if not os.path.exists(results_dir):
	# 	os.makedirs(results_dir)
	# suffix = "_%d_%d" % (num_experiments, workload_size)
	# save_results(nvp_results, os.path.join(results_dir, "nvp%s" % suffix))
	# save_results(rb_failures, os.path.join(results_dir, "rb%s" % suffix))
	# save_results(baseline_failures, os.path.join(results_dir, "baseline%s" % suffix))

if __name__ == '__main__':
	main(sys.argv)
