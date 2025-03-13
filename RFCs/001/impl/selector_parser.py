from lark import Lark, v_args, exceptions

class SelectorParser:
    """
    A parser for JSON using Lark.
    """

    grammar = r"""
        ?start: value

        ?value: object
              | array
              | string             
              | varr  -> variable         
              | SIGNED_NUMBER      -> number
              | "True"             -> true
              | "False"            -> false
              | "None"             -> null

        array  : "[" [value ("," value)*] ["," args] "]"
        object : "{" [pair ("," pair)*] ["," kwargs] "}"
        pair   : key ":" value
        ?key    : string | IDENTIFIER
        args : /\*[a-zA-Z_][a-zA-Z0-9_]*/
        kwargs : /\*\*[a-zA-Z_][a-zA-Z0-9_]*/

        string : ESCAPED_STRING
        IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
        varr : /=[a-zA-Z_][a-zA-Z0-9_]*/

        %import common.ESCAPED_STRING
        %import common.SIGNED_NUMBER
        %import common.WS
        %ignore WS
    """

    def __init__(self):
        self.parser = Lark(self.grammar, start="start")  # Corrected instantiation

    def parse(self, text):
        """
        Parses the input text and returns the parse tree.
        """
        try:
            return self.parser.parse(text)
        except exceptions.UnexpectedToken as e:
            print(f"Error: Unexpected token in JSON: {e}")
            return None
        except exceptions.UnexpectedCharacters as e:
            print(f"Error: Unexpected characters in JSON: {e}")
            return None
        except exceptions.VisitError as e:
            print(f"Error during tree transformation: {e}")
            return None

    def transform(self, tree, transformer_class):
        """
        Transforms the parse tree using a specified transformer class.
        """
        transformer = transformer_class()
        return transformer.transform(tree)


