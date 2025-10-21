import json
from lark import Lark
from _generated import ForeTransformer
from visitors import ClassDeclarationsTransformer

grammar = ""
code = ""
with open("syntax_fore.lark", "r", encoding="utf-8") as file:
    grammar = file.read()

with open("methods.example", "r", encoding="utf-8") as file:
    code = file.read()

parser = Lark(
    grammar,
    start="unit",
    parser="lalr",
    debug=True,
    transformer=ClassDeclarationsTransformer(),
)
# parser = Lark(grammar, start="unit", parser="lalr", debug=True, transformer=ForeTransformer())
tree = parser.parse(code, "unit")
print(tree)
print(json.dumps(tree))

# parser = parser.parse_interactive(code, "program")
# iter = parser.iter_parse()
# for token in iter:
#     print(token, token.type)
