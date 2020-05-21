import matplotlib.pyplot as plt
import sys
import os
from experiment_controller import load_results

def count_freqs(results):
	freqs = dict()
	for f in results:
		freqs[f] = freqs.get(f, 0) + 1
	xs = list(freqs.keys())
	heights = list(freqs.values())
	indices = sorted(range(len(xs)), key=lambda k: xs[k])
	return [xs[i] for i in indices], [heights[i] for i in indices]

def create_barplot(x, heights, xlims=None, title=None):
	fig, ax = plt.subplots(figsize=(12,8))
	ax.bar(x, heights)
	if xlims is not None:
		ax.set_xlim(xlims[0]-0.5, xlims[1]+0.5)
	if title is not None:
		fig.suptitle(title, fontsize=25)
	ax.set_xlabel("Number of failures", fontsize=18)
	ax.set_ylabel("Frequency", fontsize=18)
	ax.tick_params(labelsize=18)
	return fig, ax

if __name__ == "__main__":
	path = sys.argv[1]
	results = load_results(path)

	if len(sys.argv) >= 4:
		xlims = (int(sys.argv[2]), int(sys.argv[3]))
	else:
		xlims = None
	
	if len(sys.argv) == 5:
		title = sys.argv[4]
	else:
		title = None
		
	failures, freqs = count_freqs(results)
	print("Percentage of complete success: ", freqs[0]/sum(freqs)*100)
	print("Percentage of complete failure: ", freqs[-1]/sum(freqs)*100)
	create_barplot(failures[1:-1], freqs[1:-1], xlims, title)
	plt.show()