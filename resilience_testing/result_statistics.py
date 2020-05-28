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

def mean(x, heights):
	return sum(x[i]*heights[i] for i in range(len(x)))/sum(h for h in heights)

def create_barplot(x, heights, title):
	fig, ax = plt.subplots(figsize=(8,8))
	ax.bar(x, heights, width=0.02)
	ax.set_xlim(0.0-MARGIN, 1.0+MARGIN)
	fig.suptitle(title, fontsize=25)
	ax.axvline(mean(x, heights), color='orange', linestyle='--', linewidth=3)
	ax.set_xlabel("Baseline failure rate ", fontsize=18)
	ax.set_ylabel("Frequency", fontsize=18)
	ax.tick_params(labelsize=18)
	return fig, ax

def rate_scatter(baseline, target, title):
	above = np.array([(baseline[i], t) for i,t in enumerate(target) if t > baseline[i]])
	below = np.array([(baseline[i], t) for i,t in enumerate(target) if t < baseline[i]])
	above_mean = np.mean(above, axis=0)
	below_mean = np.mean(below, axis=0)
	means_x = [x for x,y in [above_mean, below_mean]]
	means_y = [y for x,y in [above_mean, below_mean]]
	fig, ax = plt.subplots(figsize=(5,5))
	ax.scatter(baseline, target, s=40, alpha=0.5)
	ax.scatter(means_x, means_y, marker='+', c='r', s=100)
	ax.set_xlabel("Baseline mean failure rate", fontsize=10)
	ax.set_ylabel(title + " failure rate", fontsize=10)
	ax.set_xlim(0.0-MARGIN, 1.0+MARGIN)
	ax.set_ylim(0.0-MARGIN, 1.0+MARGIN)
	ax.plot([0.0-MARGIN, 1.0+MARGIN], [0.0-MARGIN, 1.0+MARGIN], linestyle='--', color='grey', linewidth=1)
	fig.suptitle(title, fontsize=18)
	ax.tick_params(labelsize=8)
	return fig, ax

if __name__ == "__main__":
	path = sys.argv[1]
	_, filename = os.path.split(path)
	experiment_params = filename.split(".")[0]
	results = load_results(path)

	plots_dir = sys.argv[2]
	
	num_experiments = len(results)

	nvp_results = [nvp for nvp,_,_ in results]
	rb_results = [rb for _,rb,_ in results]
	baseline_results = [bl for _,_,bl in results]

	baseline_means = [sum(r)/len(r) for r in baseline_results]
	baseline_all = [b for br in baseline_results for b in br]

	fig, _ = rate_scatter(baseline_means, nvp_results, "NVP")
	fig.savefig(os.path.join(plots_dir, experiment_params + '_nvp'))

	fig, _ = rate_scatter(baseline_means, rb_results, "RB")
	fig.savefig(os.path.join(plots_dir, experiment_params + '_rb'))

	x, heights = count_freqs(baseline_all)
	fig, _ = create_barplot(x, heights, "Distribution of baseline failure rate")
	fig.savefig(os.path.join(plots_dir, experiment_params + '_baseline'))

	print("Number of experiments: %d" % num_experiments)
	print("Average number of baselines: %f" % (sum(len(b) for b in baseline_results)/num_experiments))

	above_nvp = len([r for i,r in enumerate(nvp_results) if r > baseline_means[i]])
	below_nvp = len([r for i,r in enumerate(nvp_results) if r < baseline_means[i]])
	zero_nvp = len([r for i,r in enumerate(nvp_results) if r == baseline_means[i] and r == 0.0])
	one_nvp = len([r for i,r in enumerate(nvp_results) if r == baseline_means[i] and r == 1.0])
	print("NVP above: %d%%" % ((above_nvp/num_experiments)*100))
	print("NVP below: %d%%" % ((below_nvp/num_experiments)*100))
	print("NVP on line (0.0): %d%%" % ((zero_nvp/num_experiments)*100))
	print("NVP on line (1.0): %d%%" % ((one_nvp/num_experiments)*100))

	above_rb = len([r for i,r in enumerate(rb_results) if r > baseline_means[i]])
	below_rb = len([r for i,r in enumerate(rb_results) if r < baseline_means[i]])
	zero_rb = len([r for i,r in enumerate(rb_results) if r == baseline_means[i] and r == 0.0])
	one_rb = len([r for i,r in enumerate(rb_results) if r == baseline_means[i] and r == 1.0])
	print("rb above: %d%%" % ((above_rb/num_experiments)*100))
	print("rb below: %d%%" % ((below_rb/num_experiments)*100))
	print("rb on line (0.0): %d%%" % ((zero_rb/num_experiments)*100))
	print("rb on line (1.0): %d%%" % ((one_rb/num_experiments)*100))
