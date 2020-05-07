import matplotlib.pyplot as plt

def barplot_bins(failures, remove_outliers=True):
	freqs = dict()
	for f in failures:
		freqs[f] = freqs.get(f, 0) + 1
	keys = list(freqs.keys())
	vals = list(freqs.values())
	return keys, vals
	# indices = list(range(len(keys)))
	# indices.remove(keys.index(min(keys)))
	# indices.remove(keys.index(max(keys)))
	# if remove_outliers:
	# 	return [keys[i] for i in indices], [vals[i] for i in indices]
	# else:
	# 	return keys, vals

