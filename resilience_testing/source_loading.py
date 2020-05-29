import os
import shutil

def load_package_src(name):
	files = os.listdir(name)
	files = [file for file in files if file[-3:] == '.py' and file != '__init__.py']
	versions_src = []
	for file in files:
		path = "%s/%s" % (name, file)
		with open(path, 'r', encoding='utf-8') as fd:
			src = fd.read()
			versions_src.append(src)
	return versions_src

# Saves the source of a package
def save_package_src(package_src, name, silent=True):
	if not os.path.exists(name):
		os.makedirs(name)
	open('%s/__init__.py' % name, 'w+').close() # Create __init__.py
	for idx, version_src in enumerate(package_src):
		with open('%s/version_%d.py' % (name, idx+1), 'w+', encoding='utf-8') as fd:
			fd.write(version_src)