import idaapi

idaapi.require('tree.patterns.abstracts')

from tree.patterns.abstracts import SeqPat, BindExpr

# [TODO]: mb somehow it should have architecture when patterns can provide some more feedback to matcher, not only True/False
# it can be useful to not traverse every expresion for every pattern-chain, and do it only with a particular-ones
 
class Matcher:
    def __init__(self, processed_function):
        self.function = processed_function
        self.patterns = list()

    def check_patterns(self, item) -> bool:
        for p, h, c in self.patterns:
            try:
                if p.check(item, c) and h(item, c):
                    return True

            except Exception as e:
                print('[!] Got an exception due checking and handling AST: %s' % e)
        
        return False

    def insert_pattern(self, pat, handler):
        ctx = SavedContext(self.function)
        self.patterns.append((pat, handler, ctx))

    def expressions_traversal_is_needed(self):
        for p, _, _ in self.patterns:
            if p.op >= 0 and p.op < idaapi.cit_empty or isinstance(p, BindExpr):
                return True

        return False


class SavedContext:
    def __init__(self, current_function):
        self.current_function = current_function
        self.expressions = dict()
        self.variables = dict()

    def get_var(self, name):
        return self.variables.get(name, None)

    def save_var(self, name, variable):
        self.variables[name] = variable

    def has_var(self, name):
        return self.variables.get(name, None) is not None

    def get_expr(self, name):
        return self.expressions.get(name, None)

    def save_expr(self, name, expression):
        self.expressions[name] = expression
