import matplotlib.pyplot as plt
import sys
import os
from experiment_controller import load_results

def barplot_heights(results, remove_outliers=True):
	freqs = dict()
	for f in results:
		freqs[f] = freqs.get(f, 0) + 1
	xs = list(freqs.keys())
	heights = list(freqs.values())
	indices = list(range(len(xs)))
	indices.remove(xs.index(min(xs)))
	indices.remove(xs.index(max(xs)))
	if remove_outliers:
		return [xs[i] for i in indices], [heights[i] for i in indices]
	else:
		return xs, heights

def create_barplot(x, heights, xlims=None):
	fig, ax = plt.subplots()
	ax.bar(x, heights)
	if xlims is not None:
		ax.set_xlim(xlims[0]-0.5, xlims[1]+0.5)
		ax.set_xticks(range(xlims[0], xlims[1]+1))
	return fig, ax

if __name__ == "__main__":
	path = sys.argv[1]
	if len(sys.argv) == 4:
		xlims = (int(sys.argv[2]), int(sys.argv[3]))
	else:
		xlims = None
	results = load_results(path)
	x, heights = barplot_heights(results, remove_outliers=False)
	create_barplot(x, heights, xlims)
	plt.show()