import idaapi
import idc
import idautils
import importlib
import importlib.util


def _resolve_obj_address(obj):
	if obj.op != idaapi.cot_obj:
		return None
	
	if obj.obj_ea != idaapi.BADADDR and obj.obj_ea is not None:
		return obj.obj_ea

	return None

def _resolve_obj_symbol(obj):
	ea = _resolve_obj_address(obj)
	if ea is None:
		return None

	return idaapi.get_name(ea)


def resolve_calling_function_from_node(call_node):
	node = call_node
	while node.x.op == idaapi.cot_cast:
		node = node.x

	if node.x.op == idaapi.cot_obj:
		return _resolve_obj_address(node.x), _resolve_obj_symbol(node.x)
	
	elif node.x.op == idaapi.cot_helper:
		return None, node.x.helper

	else:
		return None, None

def get_obj_from_call_node(call_node):
	node = call_node
	while node.x.op == idaapi.cot_cast:
		node = node.x

	if node.x.op == idaapi.cot_obj:
		return node.x

	return None

def get_following_instr(parent_block, item):
	container = parent_block.cinsn.cblock
	item_idx = container.index(item)
	if item_idx is None:
		return None
	if item_idx == len(container) - 1:
		return None
	return container[item_idx + 1]
	
def resolve_name_address(name):
	return idc.get_name_ea_simple(name)

def resolve_addresses_by_prefix(prefix):
	return [resolve_name_address(name) for name in idautils.Names() if name.startswith(prefix)]

def resolve_addresses_by_suffix(suffix):
	return [resolve_name_address(name) for name in idautils.Names() if name.startswith(suffix)]
			

def remove_instruction_from_ast(unwanted_ins, parent):
	assert type(unwanted_ins) is idaapi.cinsn_t, "Removing item must be an instruction (cinsn_t)"

	block = None
	if type(parent) is idaapi.cinsn_t and parent.op == idaapi.cit_block:
		block = parent.cblock

	elif type(parent) is idaapi.cfuncptr_t or type(parent) is idaapi.cfunc_t:
		ins = parent.body.find_parent_of(unwanted_ins).cinsn
		assert type(ins) is idaapi.cinsn_t and ins.op == idaapi.cit_block, "block is not cinsn_t or op != idaapi.cit_block"
		block = ins.cblock

	else:
		raise TypeError("Parent must be cfuncptr_t or cblock_t")

	if unwanted_ins.contains_label():
		return False

	if len(block) <= 1:
		return False

	try:
		return block.remove(unwanted_ins)
	except Exception as e:
		print('Got an exception %s while trying to remove instruction from block' % e)
		return False


def make_cblock(instructions):
	block = idaapi.cblock_t()
	for i in instructions:
		block.push_back(i)
	
	return block

def make_block_insn(instructions, address, label_num=-1):
	block = None
	if type(instructions) is idaapi.cblock_t:
		block = instructions
	elif type(instructions) is list or type(instructions) is tuple:
		block = make_cblock(instructions)
	else:
		raise TypeError("Trying to make cblock instruicton neither of cblock_t or list|tuple")
	
	insn = idaapi.cinsn_t()
	insn.ea = address
	insn.op = idaapi.cit_block
	insn.cblock = block
	insn.label_num = label_num
	insn.thisown = False

	return insn

def make_expr_instr(expr):
	new_item = idaapi.cinsn_t()
	new_item.op = idaapi.cit_expr
	new_item.cexpr = expr
	new_item.thisown = False
	return new_item

def make_call_helper_expr(name, *args, retval=None):
	if retval is None:
		retval = idaapi.get_unk_type(8)

	arglist = idaapi.carglist_t()
	for arg in args:
		if arg is None:
			print("[!] Warning: argument is None, skipping")
			continue

		if isinstance(arg, idaapi.carg_t):
			arglist.push_back(arg)
		else:
			narg = idaapi.carg_t()
			narg.assign(arg)
			arglist.push_back(narg)

	return idaapi.call_helper(retval, arglist, name)

def make_call_helper_instr(name, *args):
	return make_expr_instr(make_call_helper_expr(name, *args))

def strip_casts(expr):
	import idaapi
	if expr.op == idaapi.cot_cast:
		return expr.x
	return expr

def load_python_module_from_file(path):
	try:
		spec = importlib.util.spec_from_file_location("module", path)
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)
	except Exception as e:
		print("[!] Exception happened during loading module from file %s: %s" % (path, e))
		return None
	return module

def singleton(cls):
	instances = {}
	def getinstance(*args, **kwargs):
		if cls not in instances:
			instances[cls] = cls(*args, **kwargs)
		return instances[cls]
	return getinstance
