import importlib
import pkgutil
import py_compile
import os

def load_modules(package_name, silent=True):
	modules = []
	for submodule in pkgutil.iter_modules([package_name]):
		try:
			filename = submodule.name + ".py"
			path = os.path.join(".", package_name, filename)
			py_compile.compile(path, doraise=True)
			module = importlib.import_module(".%s" % submodule.name, package_name)
			if "Database" not in dir(module):
				if not silent:
					print("Cannot find \"Database\" in file %s" % filename)
				continue
			modules.append(module)
			if not silent:
				print("Successfully imported submodule %s" % submodule.name)
		except Exception as e:
			if not silent:
				print("Failed to import submodule '%s'\n%s" % (submodule.name, e))
	return modules

def load_versions(modules, data_dir, folder_name, individual_dirs):
	path = os.path.join(data_dir, folder_name)
	versions = []
	for module_idx, module in enumerate(modules):
		if individual_dirs:
			path = os.path.join(data_dir, folder_name, str(module_idx))
		try:
			version = module.Database(data_dir=path)
		except:
			continue
		versions.append(version)
	return versions
	