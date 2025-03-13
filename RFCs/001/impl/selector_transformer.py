from lark import Transformer, v_args
from matcher import TrueMatcher, FalseMatcher, NullMatcher, VarMatcher, NumberMatcher, StringMatcher, ListMatcher, ObjectMatcher, ListRestMatcher, ObjectRestMatcher

class SelectorTransformer(Transformer):
    """
    Transforms the parsed JSON tree into Python dict/list structures.
    """
    def number(self, items):
        """
        Converts a SIGNED_NUMBER token to an integer or float.
        """
        n = items[0]
        try:
            val = int(n)
        except ValueError:
            val = float(n)  # If it has a decimal
        return NumberMatcher(val)

    def true(self, items):
        """
        Returns a Python boolean True.
        """
        return TrueMatcher()

    def false(self, items):
        """
        Returns a Python boolean False.
        """
        return FalseMatcher()

    def null(self, items):
        """
        Returns a Python None.
        """
        return NullMatcher()

    def string(self, items):
      s = items[0][1:-1]  # Remove quotes
      s = s.replace('\\"', '"').replace('\\\\', '\\') # Basic unescape. Add more when needed.
      return StringMatcher(s)

    def IDENTIFIER(self, items):
      s = items[0]  # Remove quotes
      return StringMatcher(s)

    def args(self, items):
      return ListRestMatcher(items[0][1:])

    def kwargs(self, items):
      return ObjectRestMatcher(items[0][2:])

    def array(self, items):
      return ListMatcher(list(items[:-1]), items[-1])

    def variable(self, items):
      return VarMatcher(items[0][1:])

    def object(self, items):
      item_transformers = {}
      for key, value in items[:-1]:
        item_transformers[key] = value
      return ObjectMatcher(item_transformers, items[-1])

    def pair(self, items):
      #Handle key-value pair logic. Returning as tuple for now
      return tuple(items)

    def identifier(self, items):
      return str(items[0])

    def varr(self, items):
      return str(items[0])