import matplotlib.pyplot as plt
import sys
import os
import math
import numpy as np
from experiment_controller import load_results

MARGIN = 0.025

def count_freqs(results):
	freqs = dict()
	for f in results:
		freqs[f] = freqs.get(f, 0) + 1
	xs = list(freqs.keys())
	heights = list(freqs.values())
	indices = sorted(range(len(xs)), key=lambda k: xs[k])
	return [xs[i] for i in indices], [heights[i] for i in indices]

def create_barplot(x, heights, title):
	fig, ax = plt.subplots(figsize=(5,5))
	ax.bar(x, heights, width=0.02)
	ax.set_xlim(0.0-MARGIN, 1.0+MARGIN)
	fig.suptitle(title, fontsize=14)
	ax.set_xlabel("Baseline failure rate ", fontsize=10)
	ax.set_ylabel("Frequency", fontsize=10)
	ax.tick_params(labelsize=10)
	return fig, ax

def rate_scatter(baseline, target, title):
	fig, ax = plt.subplots(figsize=(5,5))
	ax.scatter(baseline, target, s=40, alpha=0.25)
	ax.set_xlabel("Baseline mean failure rate", fontsize=10)
	ax.set_ylabel("Target failure rate", fontsize=10)
	ax.set_xlim(0.0-MARGIN, 1.0+MARGIN)
	ax.set_ylim(0.0-MARGIN, 1.0+MARGIN)
	ax.plot([0.0-MARGIN, 1.0+MARGIN], [0.0-MARGIN, 1.0+MARGIN], linestyle='--', color='grey', linewidth=1)
	fig.suptitle(title, fontsize=14)
	ax.tick_params(labelsize=10)
	return fig, ax

if __name__ == "__main__":
	results_dir = sys.argv[1]
	plots_dir = sys.argv[2]
	n_experiments = int(sys.argv[3])
	workload_size = int(sys.argv[4])
	n_bypass = int(sys.argv[5])
	n_faults = int(sys.argv[6])

	params = "num_%d__workload_%d__bypass_%d__mutations_%d" % (n_experiments, workload_size, n_bypass, n_faults)

	results = load_results(os.path.join(results_dir, params + ".json"))

	nvp_results = [nvp for nvp,_,_ in results]
	rb_results = [rb for _,rb,_ in results]
	baseline_results = [bl for _,_,bl in results]

	baseline_means = [sum(r)/len(r) for r in baseline_results]
	baseline_all = [b for br in baseline_results for b in br]

	fig, _ = rate_scatter(baseline_means, nvp_results, "NVP, n_bypass=%d, n_faults=%d" % (n_bypass, n_faults))
	fig.savefig(os.path.join(plots_dir, params + '_nvp'))

	fig, _ = rate_scatter(baseline_means, rb_results, "RB, n_bypass=%d, n_faults=%d" % (n_bypass, n_faults))
	fig.savefig(os.path.join(plots_dir, params + '_rb'))

	x, heights = count_freqs(baseline_all)
	fig, _ = create_barplot(x, heights, "n_bypass=%d, n_faults=%d" % (n_bypass, n_faults))
	fig.savefig(os.path.join(plots_dir, params + '_baseline'))

	print("Number of experiments: %d" % n_experiments)
	print("Average number of baselines: %f" % (sum(len(b) for b in baseline_results)/n_experiments))

	margin = 0.025

	# Compute statistics for NVP
	above_nvp = len([r for i,r in enumerate(nvp_results) if r > baseline_means[i]+margin])
	below_nvp = len([r for i,r in enumerate(nvp_results) if r < baseline_means[i]-margin])
	on_nvp = len([r for i,r in enumerate(nvp_results) if abs(r-baseline_means[i]) <= margin])
	print("NVP above: %f%%" % ((above_nvp/n_experiments)*100))
	print("NVP below: %f%%" % ((below_nvp/n_experiments)*100))
	print("NVP on line: %f%%" % ((on_nvp/n_experiments)*100))

	# Compute statistics for RB
	above_rb = len([r for i,r in enumerate(rb_results) if r > baseline_means[i] + margin])
	below_rb = len([r for i,r in enumerate(rb_results) if r < baseline_means[i] - margin])
	on_rb = len([r for i,r in enumerate(rb_results) if abs(r-baseline_means[i]) <= margin])
	print("RB above: %f%%" % ((above_rb/n_experiments)*100))
	print("RB below: %f%%" % ((below_rb/n_experiments)*100))
	print("RB on line: %f%%" % ((on_rb/n_experiments)*100))
