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

NUM_SYNTHESIZED_VERSIONS = 8

def break_versions(input_dir, output_dir, fault_injector, num_bypass=0, num_mutations=1):
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
		broken_src.append(fault_injector.inject(v, num_mutations))
	output = broken_src + bypassed_src
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
			continue # skip write and clear
		num_read += 1
		if (actual_result == None) or (len(actual_result) != len(true_result)):
			num_failures += 1
	out_queue.put(num_failures/num_read)

def run_tests(targets, workload_generator):
	results = []
	for target_idx, target in enumerate(targets):		
		queue = Queue()
		p = Process(target=process_fn, args=(target, workload_generator, queue))
		p.start()
		p.join()
		p.kill()
		if not queue.empty():
			r = queue.get()
		else:
			# If cannot get result set every I/O pair to failure
			r = 1.0
		results.append(r)
		workload_generator.restart()
	return results

def save_results(obj, path):
	with open(path + ".json", "w+") as file:
		json.dump(obj, file,)

def load_results(path):
	with open(path, "r") as file:
		return json.load(file)

def resilience_test(num_experiments, workload_size, versions_dir, data_dir, results_dir, num_bypass, num_mutations):

	fi = FaultInjector()

	results = []

	for idx in range(num_experiments):

		# Logging information about experiment
		print("Experiment no. %d" % (idx+1))

		# Reset data directories
		if os.path.exists(data_dir):
			shutil.rmtree(data_dir, ignore_errors=True)
	
		baselines = []
		while len(baselines) < min(2+num_bypass, NUM_SYNTHESIZED_VERSIONS):
			# Create new broken versions
			break_versions(versions_dir, 'versions_broken', fi, num_bypass, num_mutations)
			modules_broken = load_modules("versions_broken")
			
			# Create baselines
			modules = load_modules('versions_broken')
			for module_idx, module in enumerate(modules):
				try:
					baseline_data_dir = os.path.join(data_dir, 'baseline', str(module_idx))
					version = module.Database(baseline_data_dir)
					baselines.append(Baseline(version))
				except Exception as e:
					pass

		# Create target databases with broken components
		nvp_dir = os.path.join(data_dir, 'nvp')
		nvp = NVersionProgramming('versions_broken', nvp_dir)
		rb_dir = os.path.join(data_dir, 'rb')
		rb = RecoveryBlock('versions_broken', rb_dir)
		targets = [nvp, rb]

		wg = WorkloadGenerator(workload_size)

		# Test targets
		target_results = run_tests(targets, wg)	
		results_nvp = target_results[0]
		results_rb = target_results[1]
		
		# Test baselines
		results_baseline = run_tests(baselines, wg)

		results.append((results_nvp, results_rb, results_baseline))

		print("NVP results: ", results_nvp)
		print("RB results: ", results_rb)
		print("Baseline results: ", results_baseline)
		print()

	return results

def count(results, value):
	return len([r for r in results if r == value]) 

def percentage(a, b):
	return (a/b) * 100

def main(args):
	argc = len(args)
	if argc != 8:
		print("Usage: experiment_controller.py <num_experiments> <workload_size> <versions_dir> <data_dir> <results_dir> <num_bypass> <num_mutations>")
		return
	try:
		num_experiments = int(args[1])
		workload_size = int(args[2])
		versions_dir = args[3]
		data_dir = args[4]
		results_dir = args[5]
		num_bypass = int(args[6])
		num_mutations = int(args[7])
	except Exception as e:
		print("Inputted formatted incorrectly:", e)
		return

	results = resilience_test(num_experiments, workload_size, versions_dir, data_dir, results_dir, num_bypass, num_mutations)

	if not os.path.exists(results_dir):
		os.makedirs(results_dir)
	filename = "num_%d__workload_%d__bypass_%d__mutations_%d" % (num_experiments, workload_size, num_bypass, num_mutations)
	save_results(results, os.path.join(results_dir, "%s" % filename))

if __name__ == '__main__':
	main(sys.argv)
