import herast.storage_manager as storage_manager

# forward imports for herast usage
from herast.tree.patterns.abstracts import *
from herast.tree.patterns.expressions import *
from herast.tree.patterns.instructions import *
from herast.tree.matcher import Matcher
from herast.schemes.single_pattern_schemes import SPScheme
from herast.herast_settings import get_herast_enabled, get_herast_files, get_herast_folders, add_herast_enabled, add_herast_file, add_herast_folder
from herast.idb_settings import get_enabled_idb, get_idb_files, get_idb_folders, add_idb_enabled, add_idb_file, add_idb_folder

def get_storages():
	return [s for s in storage_manager.schemes_storages.values()]

def get_storage(storage_path):
	return storage_manager.get_storage(storage_path)

def skip_casts(expr):
	import idaapi
	if expr.op == idaapi.cot_cast:
		return expr.x
	return expr