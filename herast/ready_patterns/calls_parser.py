import idc
import idautils
import idaapi
import herapi

"""
This example shows how to automate objects renamings from this:
	import_function("FooFunction", &dword_123456);
to this
	import_function("Foo", &FooFunction);
"""

def get_unique_name(name_candidate):
	if idc.get_name_ea_simple(name_candidate) == idaapi.BADADDR:
		return name_candidate

	i = 0
	while idc.get_name_ea_simple(name_candidate + '_' + str(i)) != idaapi.BADADDR:
		i += 1
	return name_candidate + '_' + str(i)

class CallsParser(herapi.SPScheme):
	def __init__(self, *function_address):
		if len(function_address) == 0:
			raise ValueError("No function address provided")

		if len(function_address) == 1:
			obj_pat = herapi.ObjPat(ea=function_address[0])
		else:
			obj_pat = herapi.OrPat(*[herapi.ObjPat(ea=addr) for addr in function_address])
		pattern = herapi.CallExprPat(obj_pat, herapi.ObjPat(), herapi.RefPat(herapi.ObjPat()), skip_missing=True)
		super().__init__("calls_parser", pattern)

	def on_matched_item(self, item, ctx: herapi.PatternContext):
		arg0 = item.a[0]
		arg1 = item.a[1]
		new_name = idc.get_strlit_contents(arg0.obj_ea)
		if new_name is None: return False
		new_name = new_name.decode()
		new_name = get_unique_name(new_name)
		rename_address = arg1.x.obj_ea
		print("renaming", hex(rename_address), "to", new_name)
		idaapi.set_name(rename_address, new_name)
		return False

def get_func_calls_to(fea):
	rv = filter(None, [herapi.get_func_start(x.frm) for x in idautils.XrefsTo(fea)])
	rv = filter(lambda x: x != idaapi.BADADDR, rv)
	return list(rv)

def find_calls(*functions):
	scheme = CallsParser(*functions)
	matcher = herapi.Matcher(scheme)

	cfuncs_eas = set()
	for func_ea in functions:
		calls = get_func_calls_to(func_ea)
		cfuncs_eas.update(calls)

	print("need to decompile {} cfuncs".format(len(cfuncs_eas)))
	cfuncs = {ea: herapi.get_cfunc(ea) for ea in cfuncs_eas}
	for cfunc in cfuncs.values():
		if cfunc is None:
			continue

		matcher.match_cfunc(cfunc)