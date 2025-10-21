from lark import v_args, Token
from lark.visitors import Transformer


class ClassDeclarationsTransformer(Transformer):
    def unit(self, children):
        items = {}
        items["_type"] = "unit"
        items["items"] = []

        for ch in children:
            if isinstance(ch, dict):
                if ch.get("_type") == "class_def":
                    items["items"].append(ch)
                if ch.get("_type") == "method_declaration":
                    items["items"].append(ch)

        return items

    def class_def(self, children):
        items = {}
        items["_type"] = "class_def"
        items["access_modifier"] = children[0]
        items["class_name"] = children[2]

        for ch in children:
            if isinstance(ch, dict):
                if ch.get("_type") == "class_body":
                    items["class_body"] = ch

        return items

    def class_body(self, children):
        items = {}
        items["field_declarations"] = []
        items["property_declarations"] = []
        items["method_declarations"] = []
        items["_type"] = "class_body"

        for ch in children:
            if isinstance(ch, dict):
                if ch.get("_type") == "constructor":
                    items["constructor"] = ch
                elif ch.get("_type") == "field_declaration":
                    items["field_declarations"].append(ch)
                elif ch.get("_type") == "property_declaration":
                    items["property_declarations"].append(ch)
                elif ch.get("_type") == "method_declaration":
                    items["method_declarations"].append(ch)
        return items

    def constructor(self, children):
        return {
            "_type": "constructor",
            "access_modifier": children[0],
            "name": children[1],
        }

    def parameter_list_optional(self, children):
        return children if children else None

    def parameter_list(self, children):
        return children if children else None

    def parameter(self, children):
        params = []
        names = []
        is_var = children[0] != None
        is_paramarray = children[1] != None

        for ch in children:
            if isinstance(ch, Token) and ch.type == "WORD":
                names.append(ch.value)

        for name in names:
            params.append(
                {
                    "_type": "parameter",
                    "var": is_var,
                    "paramarray": is_paramarray,
                    "name": name,
                    "type": children[-2],
                    "default": children[-1],
                }
            )
        return params

    # === Модификаторы доступа ===
    def access_modifier(self, children):
        return children[0]

    def protected_friend(self, _):
        return "Protected Friend"

    def field_declaration(self, children):
        return {
            "_type": "field_declaration",
            "access_modifier": children[0],
            "shared": children[1],
            "name": children[2],
            "field_type": children[3],
        }

    def property_declaration(self, children):
        return {
            "_type": "property_declaration",
            "access_modifier": children[0],
            "shared": children[1],
            "name": children[3],
            "parameters": children[4],
            "return_type": children[5],
            "get_body": "children[6]",
            "set_body": "children[7]",
        }

    def method_declaration(self, children):
        return {
            "_type": "method_declaration",
            "access_modifier": children[0],
            "shared": children[1],
            "callable": children[2],
            "name": children[3],
            "parameters": "children[4]",
            "return_type": children[5],
            "body": children[6],
        }

    def method_body(self, children):
        return {
            "_type": "method_body",
            "const_block": "children[0]",
            "var_block": "children[1]",
            "statements": children[3],
        }

    def statement_list(self, children):
        items = [
            
        ]
        return children  # children

    def statement(self, children):
        return children[0] if children else None

    def if_statement(self, children):
        return {
            "_type": "if_statement",
            "condition": "expression",  # children[1]
            "statements": children[3],
            "elseif": [
                {
                    "condition": "expression",
                    "statements": "statements",
                }
            ],
            "else_statements": children[9],
        }

    def assignment_statement(self, children):
        return {
            "_type": "assignment_statement",
            "left": children[0],
            "right": children[1],
        }

    def constructor_call(self, children):
        return {
            "_type": "constructor_call",
            "constructor": children[1],
        }

    def member_access(self, children):
        return {"_type": "member_access", "object": children[0], "member": children[1]}

    def return_statement(self, children):
        return {
            "_type": "return_statement",
        }

    def argument_list(self, children):
        return children

    def ternary_expression(self, children):
        return {
            "type": "ternary",
            "condition": children[0],
            "true_expr": children[1],
            "false_expr": children[2],
        }

    def simple_expression(self, children):
        if len(children) == 1:
            return children[0]

        return {
            "_type": "simple_expression",
            "op": children[1],
            "left": children[0],
            "right": children[2],
        }

    def type_cast(self, children):
        return {
            "_type": "type_cast",
            "type": children[1],
        }

    def type_check(self, children):
        return {
            "_type": "type_check",
            "type": children[1],
        }

    def method_call(self, children):
        return {
            "_type": "method_call",
            "method": children[0],
            "args": children[1]
        }

    def expression(self, children):
        return {
            "_type": "expression",
        }

    def foreach_statement(self, children):
        return {
            "_type": "for_each_statement",
        }

    def term(self, children):
        return {
            "_type": "term",
        }

    def mul_op(self, children):
        return {
            "_type": "mul_op",
        }
