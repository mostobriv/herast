import idaapi
import idc


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
    
def resolve_name_address(addr):
    return idc.get_name_ea_simple(addr)

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

    try:
        block.remove(unwanted_ins)
    except Exception as e:
        print('Got an exception %s' % e)


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