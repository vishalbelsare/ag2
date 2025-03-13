
class Matcher:

    def add_var(self, name, value, ctx):
        if name in ctx:
            return ctx[name] == value
        ctx[name] = value
        return True

class NumberMatcher(Matcher):
    def __init__(self, number):
        self.number = number

    def match(self, value, ctx):
        return self.number == value

    def __repr__(self):
        return f"NumberMatcher({self.number})"

class StringMatcher(Matcher):
    def __init__(self, string):
        self.string = string

    def match(self, value, ctx):
        return self.string == value
    
    def __repr__(self):
        return f"StringMatcher({self.string})"

    
class NullMatcher(Matcher):
    def match(self, value, ctx):
        return value is None

    def __repr__(self):
        return f"NullMatcher()"
    
class TrueMatcher(Matcher):
    def match(self, value, ctx):
        return value is True

    def __repr__(self):
        return f"TrueMatcher()"

class FalseMatcher(Matcher):
    def match(self, value, ctx):
        return value is False   

    def __repr__(self):
        return f"FalseMatcher()"

class VarMatcher(Matcher):
    def __init__(self, name):
        self.name = name

    def match(self, value, ctx):
        return self.add_var(self.name, value, ctx)

    def __repr__(self):
        return f"VarMatcher({self.name})"

class ListRestMatcher(Matcher):
    def __init__(self, name):
        self.name = name

    def match(self, value, ctx):
        return self.add_var(self.name, value, ctx)

    def __repr__(self):
        return f"ListRestMatcher({self.name})"

class ObjectRestMatcher(Matcher):
    def __init__(self, name):
        self.name = name

    def match(self, value, ctx):

        return self.add_var(self.name, value, ctx)

    def __repr__(self):
        return f"ObjectRestMatcher({self.name})"

class ListMatcher(Matcher):
    def __init__(self, matchers, rest=None):
        self.matchers = matchers
        self.rest = rest

    def match(self, value, ctx):
        if not isinstance(value, list):
            return False
        if len(self.matchers) > len(value):
            return False
        lix = 0 
        for m in self.matchers:
            list_item = value[lix]
            if not m.match(list_item, ctx):
                return False
            lix += 1
        if self.rest is None:
            return len(value) == len(self.matchers)
        
        return self.rest.match(value[lix:], ctx)
    
    def __repr__(self):
        return f"ListMatcher({self.matchers}, {self.rest})"
        
    
class ObjectMatcher(Matcher):
    def __init__(self, matchers, rest=None):
        self.matchers = matchers
        self.rest = rest

    def match(self, value, ctx):
        if not isinstance(value, dict):
            return False
        checked = []
        for k, m in self.matchers.items():
            key = k.string
            if key not in value:
                return False
            if not m.match(value[key], ctx):
                return False
            checked.append(key)
        if self.rest is None:
            return len(value.keys()) == len(self.matchers)
        rest = dict(value)
        for k in checked:
            del rest[k]

        return self.rest.match(rest, ctx)   

    def __repr__(self):
        return f"ObjectMatcher(items: {self.matchers}, rest:{self.rest})"
