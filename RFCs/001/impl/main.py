from selector_parser import  SelectorParser
from selector_transformer import SelectorTransformer

parser = SelectorParser()

test_json = """
{
    name: $nameVar,
    age: 30,
    isStudent: false,
    address: {
        street: "123 Main St",
        city: $cityVar
    },
    grades: [$grade1, $grade2, 78],
    nullable: None,
    specialIdentifier
}
"""

test_json2 = """{"kljuc": 123, k2: "peor", **resto}"""
test_json3 = r""" ["k1", 123, =varko, "k2", 43, *resto] """

try:
    tree = parser.parse(test_json3)
    print(tree.pretty())
    #print(tree) 
    transformed = parser.transform(tree, SelectorTransformer)
    print(transformed) 
    

except Exception as e:
    print(f"Error parsing selector: {e}")

