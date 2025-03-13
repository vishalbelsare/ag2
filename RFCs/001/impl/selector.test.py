import unittest
from selector_parser import SelectorParser
from selector_transformer import SelectorTransformer

class TestSelectorParser(unittest.TestCase):

    def setUp(self):
        self.parser = SelectorParser()

    def assertParses(self, text):
        """Asserts that the given text parses without error."""
        tree = self.parser.parse(text)
        self.assertIsNotNone(tree, f"Failed to parse: {text}")
        return tree

    def assertParseFails(self, text):
        """Asserts that the given text fails to parse."""
        tree = self.parser.parse(text)
        self.assertIsNone(tree, f"Unexpectedly parsed: {text}")
                           
    def assertTransformsTo(self, text, expected_result):
        """Asserts that the given text parses and transforms to the expected result."""
        tree = self.assertParses(text)
        transformed = self.parser.transform(tree, SelectorTransformer)
        self.assertEqual(transformed, expected_result, f"Transformation failed for: {text}")

    def assertMatchesTo(self, text, value, ctx = dict()):
        """Asserts that the given text parses and transforms to the expected result."""
        tree = self.assertParses(text)
        transformed = self.parser.transform(tree, SelectorTransformer)
        vars = dict()
        result = transformed.match(value, vars)
        self.assertEqual(result, True, f"Match failed for: {text}")
        self.assertEqual(len(ctx.keys()), len(vars.keys()), f"Match succedded, but var lists do not match {ctx}, {vars}" )
        for k in ctx.keys():
            self.assertEqual(ctx[k], vars[k], f"Match succedded, but var values do not match {ctx}, {vars}" )   

    def assertDoesNotMatchTo(self, text, value):
        """Asserts that the given text parses and transforms to the expected result."""
        tree = self.assertParses(text)
        transformed = self.parser.transform(tree, SelectorTransformer)
        vars = {}
        result = transformed.match(value, {})
        self.assertEqual(result, False, f"Match should fail for: {text} , but it did not")


    def test_parse_object_string_key(self):
        self.assertParses('{"key": "value"}')

    def test_parse_object_identifier_key(self):
        self.assertParses('{key: "value"}')

    def test_parse_object_number_value(self):
        self.assertParses('{"key": 123}')

    def test_parse_object_variable_value(self):
        self.assertParses('{"key": =value}')

    def test_parse_object_number_value_identifier_key(self):
        self.assertParses('{key: 123}')

    def test_parse_object_true_value(self):
        self.assertParses('{"key": True}')

    def test_parse_object_false_value(self):
        self.assertParses('{"key": False}')

    def test_parse_object_true_value_identifier_key(self):
        self.assertParses('{key: True}')

    def test_parse_object_null_value(self):
        self.assertParses('{"key": None}')

    def test_parse_object_null_value_identifier_key(self):
        self.assertParses('{key: None}')

    def test_parse_object_array_value(self):
        self.assertParses('{"key": [1, 2, 3]}')

    def test_parse_object_array_value_identifier_key(self):
        self.assertParses('{key: [1, 2, 3]}')

    def test_parse_object_kwargs(self):
        self.assertParses('{"key": 17, **kwargs}')

    def test_parse_object_nested_object(self):
        self.assertParses('{"key": {"nested": "value"}}')


    def test_parse_object_nested_object_identifier_key(self):
        self.assertParses('{key: {"nested": "value"}}')

    def test_parse_array(self):
        self.assertParses('[1, 2, 3]')

    def test_parse_object_multiple_key_value(self):
        self.assertParses('{"key": "value", "key2": 456}')

    def test_parse_object_multiple_key_value_identifier(self):
        self.assertParses('{key: "value", key2: 456}')

    def test_parse_escaped_quotes(self):
        self.assertParses('{"key": "value with \\"quotes\\""}')

    def test_parse_newline(self):
        self.assertParses('{"key": "value\\nwith newline"}')

    def test_parse_tab(self):
        self.assertParses('{"key": "value\\twith tab"}')

    def test_parse_carriage_return(self):
        self.assertParses('{"key": "value\\rwith carriage return"}')

    def test_parse_backslash(self):
        self.assertParses('{"key": "value\\\\with backslash"}')

    def test_parse_number(self):
        self.assertParses('123.45')

    def test_parse_true(self):
        self.assertParses('True')

    def test_parse_false(self):
        self.assertParses('False')

    def test_parse_null(self):
        self.assertParses('None')

    def test_parse_empty_array(self):
        self.assertParses('[]')

    def test_parse_empty_object(self):
        self.assertParses('{}')

    def test_parse_complex_object(self):
        self.assertParses('{"a": "b", "c": {"d": [1, 2, False]}}')

    def test_parse_complex_object_identifier(self):
        self.assertParses('{a: "b", c: {d: [1, 2, False]}}')

    def test_parse_empty_string_value(self):
        self.assertParses('{"key": ""}')

    def test_parse_empty_string_value_identifier(self):
        self.assertParses('{key: ""}')

    def test_parse_empty_string(self):
        self.assertParses('""')

    def test_parse_empty_string_key(self):
        self.assertParses('{"": "value"}')

    def test_parse_empty_array_value(self):
        self.assertParses('{"key": []}')

    def test_parse_list_rest(self):
        self.assertParses('[1,2, *rest]')

    def test_parse_object_rest(self):
        self.assertParses('{"k": 1, **rest}')

    def test_parse_empty_object_value(self):
        self.assertParses('{"key": {}}')

    def test_fail_missing_quotes(self):
        self.assertParseFails('{"key": value}')

    def test_fail_trailing_comma_array(self):
        self.assertParseFails('[1, 2,]')

    def test_fail_missing_value(self):
        self.assertParseFails('{"key": }')

    def test_fail_truefalse(self):
        self.assertParseFails('truefalse')

    def test_fail_invalid_identifier_key(self):
        self.assertParseFails('{123: "value"}')

    def test_fail_invalid_spacing(self):
        self.assertParseFails('{"key"  "value"}')

    def test_fail_trailing_comma_object(self):
        self.assertParseFails('{"key":123,}')

    def test_fail_just_close_brace(self):
        self.assertParseFails('}')

    def test_fail_mismatched_braces(self):
        self.assertParseFails('{]')

    def test_match_list(self):
        self.assertMatchesTo('[1, "koko", 3]', [1, "koko", 3])

    def test_match_list2(self):
        self.assertDoesNotMatchTo('[1, "koko", 3]', [1, "kok", 3])

    def test_match_list3(self):
        self.assertDoesNotMatchTo('[1, "koko", 3]', [1, "koko", 3, 12])

    def test_match_list_var(self):
        self.assertMatchesTo('[1, =name, 3]', [1, "koko", 3], {"name": "koko"})

    def test_match_list_rest(self):
        self.assertMatchesTo('[1, "koko", 3, *r]', [1, "koko", 3, 12], {"r": [12]})

    def test_match_list_rest2(self):
        self.assertMatchesTo('[1, "koko", 3, *r]', [1, "koko", 3, 12, "aa"], {"r": [12, "aa"]})

    def test_match_object(self):
        self.assertMatchesTo('{k:"kk", "xx": 77}', {"k": "kk", "xx": 77})

    def test_match_object_2(self):
        self.assertMatchesTo('{k:"kk", "xx": 77, l:[1,2,3]}', {"k": "kk", "xx": 77, "l": [1,2,3]})

    def test_match_object_rest(self):
        self.assertMatchesTo('{k:"kk", "xx": 77, **rest}', {"k": "kk", "xx": 77, "a": 1, "b": 2}, {"rest": {"a": 1, "b": 2}})

    def test_match_object_rest(self):
        self.assertMatchesTo('{k: =whichK, "xx": 77, **rest}', {"k": "kk", "xx": 77, "a": 1, "b": 2}, {"whichK": "kk", "rest": {"a": 1, "b": 2}})


if __name__ == '__main__':
    unittest.main()