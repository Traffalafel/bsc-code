import matplotlib.pyplot as plt
import sys
import os
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
	fig, ax = plt.subplots(figsize=(8,8))
	ax.bar(x, heights, width=0.02)
	ax.set_xlim(0.0-MARGIN, 1.0+MARGIN)
	fig.suptitle(title, fontsize=25)
	ax.set_xlabel("Baseline failure rate ", fontsize=18)
	ax.set_ylabel("Frequency", fontsize=18)
	ax.tick_params(labelsize=18)
	return fig, ax

def rate_scatter(baseline, target, title):
	fig, ax = plt.subplots(figsize=(5,5))
	ax.scatter(baseline, target, s=40, alpha=0.25)
	ax.set_xlabel("Baseline mean failure rate", fontsize=10)
	ax.set_ylabel("Target failure rate", fontsize=10)
	ax.set_xlim(0.0-MARGIN, 1.0+MARGIN)
	ax.set_ylim(0.0-MARGIN, 1.0+MARGIN)
	ax.plot([0.0-MARGIN, 1.0+MARGIN], [0.0-MARGIN, 1.0+MARGIN], linestyle='--', color='grey', linewidth=1)
	fig.suptitle(title, fontsize=18)
	ax.tick_params(labelsize=8)
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

	fig, _ = rate_scatter(baseline_means, nvp_results, "NVP, n_faults = %d" % n_faults)
	fig.savefig(os.path.join(plots_dir, params + '_nvp'))

	fig, _ = rate_scatter(baseline_means, rb_results, "RB, n_faults = %d" % n_faults)
	fig.savefig(os.path.join(plots_dir, params + '_rb'))

	x, heights = count_freqs(baseline_all)
	fig, _ = create_barplot(x, heights, "n_faults = %d" % n_faults)
	fig.savefig(os.path.join(plots_dir, params + '_baseline'))

	print("Number of experiments: %d" % n_experiments)
	print("Average number of baselines: %f" % (sum(len(b) for b in baseline_results)/n_experiments))

	above_nvp = len([r for i,r in enumerate(nvp_results) if r > baseline_means[i]])
	below_nvp = len([r for i,r in enumerate(nvp_results) if r < baseline_means[i]])
	zero_nvp = len([r for i,r in enumerate(nvp_results) if r == baseline_means[i] and r == 0.0])
	one_nvp = len([r for i,r in enumerate(nvp_results) if r == baseline_means[i] and r == 1.0])
	print("NVP above: %d%%" % ((above_nvp/n_experiments)*100))
	print("NVP below: %d%%" % ((below_nvp/n_experiments)*100))
	print("NVP on line (0.0): %d%%" % ((zero_nvp/n_experiments)*100))
	print("NVP on line (1.0): %d%%" % ((one_nvp/n_experiments)*100))

	above_rb = len([r for i,r in enumerate(rb_results) if r > baseline_means[i]])
	below_rb = len([r for i,r in enumerate(rb_results) if r < baseline_means[i]])
	zero_rb = len([r for i,r in enumerate(rb_results) if r == baseline_means[i] and r == 0.0])
	one_rb = len([r for i,r in enumerate(rb_results) if r == baseline_means[i] and r == 1.0])
	print("rb above: %d%%" % ((above_rb/n_experiments)*100))
	print("rb below: %d%%" % ((below_rb/n_experiments)*100))
	print("rb on line (0.0): %d%%" % ((zero_rb/n_experiments)*100))
	print("rb on line (1.0): %d%%" % ((one_rb/n_experiments)*100))
