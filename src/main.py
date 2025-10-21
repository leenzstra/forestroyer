import json
from lark import Lark
from transformer import ClassDeclarationsTransformer

grammar = ""
code = ""
with open("./syntax/syntax.lark", "r", encoding="utf-8") as file:
    grammar = file.read()

with open("./examples/code.txt", "r", encoding="utf-8") as file:
    code = file.read()

parser = Lark(
    grammar,
    start="unit",
    parser="lalr",
    debug=True,
    transformer=ClassDeclarationsTransformer(),
    maybe_placeholders=True
)

tree = parser.parse(code, "unit")
# print(tree)
print(json.dumps(tree, ensure_ascii=False))

# int_parser: In = parser.parse_interactive(code, "unit")
# iter = int_parser.iter_parse()
# for token in iter:
#     print(token, token.type)
