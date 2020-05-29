import os
import sys
import random
import py_compile
from multiprocessing import Process, Queue
import json
import pkgutil
import shutil
import importlib

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
		p = Process(target=process_fn, args=(target, workload_generator, queue),)
		p.start()
		p.join()
		p.kill()
		if not queue.empty():
			r = queue.get()
		else:
			# If cannot get result set every I/O pair to failure
			r = None
		results.append(r)
		workload_generator.restart()
	return results

def save_results(obj, path):
	with open(path + ".json", "w+") as file:
		json.dump(obj, file,)

def load_results(path):
	with open(path, "r") as file:
		return json.load(file)

def resilience_test(versions_dir, data_dir, results_dir, num_experiments, workload_size, num_bypass, num_mutations):

	fi = FaultInjector()

	results = []

	experiments_completed = 0

	while experiments_completed < num_experiments:

		# Reset data directories
		if os.path.exists(data_dir):
			shutil.rmtree(data_dir, ignore_errors=False)
		os.makedirs(data_dir)
	
		# Break and load versions
		versions = []
		while len(versions) < min(2+num_bypass, NUM_SYNTHESIZED_VERSIONS):
			break_versions(versions_dir, 'versions_broken', fi, num_bypass, num_mutations)
			modules_broken = load_modules("versions_broken")
			for module_idx, module in enumerate(modules_broken):
				try:
					version = module.Database('.')
					versions.append(version)
				except Exception as e:
					pass

		# Create FT strategies with broken versions
		nvp_dir = os.path.join(data_dir, 'nvp')
		nvp = NVersionProgramming(versions, nvp_dir, silent=True)
		rb_dir = os.path.join(data_dir, 'rb')
		rb = RecoveryBlock(versions, rb_dir, silent=True)
		targets = [nvp, rb]

		# Create baselines with broken versions
		baselines = []
		for idx, version in enumerate(versions):
			baseline_dir = os.path.join(data_dir, 'baseline', str(idx))
			baseline = Baseline(version, baseline_dir)
			baselines.append(baseline)
			
		wg = WorkloadGenerator(workload_size)

		# Test targets
		target_results = run_tests(targets, wg)
		if None in target_results:
			print("Experiment failed - trying again")
			continue
		results_nvp = target_results[0]
		results_rb = target_results[1]

		# Test baselines
		results_baseline = run_tests(baselines, wg)
		if None in results_baseline:
			print("Experiment failed - trying again")
			continue

		results.append((results_nvp, results_rb, results_baseline))

		experiments_completed += 1

		print("Experiment no. %d results:" % experiments_completed)
		print("NVP results: ", results_nvp)
		print("RB results: ", results_rb)
		print("Baseline results: ", results_baseline)
		print()

	return results

def main(args):
	argc = len(args)
	if argc != 8:
		print("Usage: experiment_controller.py <versions_dir> <data_dir> <results_dir> <num_experiments> <workload_size>  <num_bypass> <num_mutations>")
		return
	try:
		versions_dir = args[1]
		data_dir = args[2]
		results_dir = args[3]
		num_experiments = int(args[4])
		workload_size = int(args[5])
		num_bypass = int(args[6])
		num_mutations = int(args[7])
	except Exception as e:
		print("Inputted formatted incorrectly:", e)
		return

	results = resilience_test(versions_dir, data_dir, results_dir, num_experiments, workload_size, num_bypass, num_mutations)

	if not os.path.exists(results_dir):
		os.makedirs(results_dir)
	filename = "num_%d__workload_%d__bypass_%d__mutations_%d" % (num_experiments, workload_size, num_bypass, num_mutations)
	save_results(results, os.path.join(results_dir, "%s" % filename))

if __name__ == '__main__':
	main(sys.argv)
