import re
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
        items["constructor_declarations"] = []
        items["const_declarations"] = []
        items["_type"] = "class_body"

        for ch in children:
            if isinstance(ch, dict):
                if ch.get("_type") == "constructor":
                    items["constructor_declarations"].append(ch)
                elif ch.get("_type") == "field_declaration":
                    items["field_declarations"].append(ch)
                elif ch.get("_type") == "property_declaration":
                    items["property_declarations"].append(ch)
                elif ch.get("_type") == "method_declaration":
                    items["method_declarations"].append(ch)
                elif ch.get("_type") == "class_const_declaration":
                    items["const_declarations"].append(ch)
            if isinstance(ch, list):
                for item in ch:
                    if item.get("_type") == "field_declaration":
                        items["field_declarations"].append(item)
        return items

    def class_const_declaration(self, children):
        return {
            "_type": "class_const_declaration",
            "access_modifier": children[0],
            "declaration": children[1],
        }

    def constructor(self, children):
        return {
            "_type": "constructor",
            "access_modifier": children[0],
            "name": children[2],
            "parameters": children[3],
            "body": children[4],
        }

    def parameter_list_optional(self, children):
        return [x for xs in children for x in xs] if children and children[0] else None

    def parameter_list(self, children):
        return [x for xs in children for x in xs]

    def parameter(self, children):
        params = []
        names = []
        is_var = children[0] != None
        is_paramarray = children[1] != None

        for ch in children:
            if isinstance(ch, dict) and ch["_type"] == "variable":
                names.append(ch)

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
        field_names = []
        fields = []

        for ch in children:
            if isinstance(ch, dict) and ch["_type"] == "variable":
                field_names.append(ch)

        for name in field_names:
            fields.append(
                {
                    "_type": "field_declaration",
                    "access_modifier": children[0],
                    "shared": children[1],
                    "name": name,
                    "field_type": children[-1],
                }
            )

        return fields

    def property_declaration(self, children):
        return {
            "_type": "property_declaration",
            "access_modifier": children[0],
            "shared": children[1],
            "name": children[3],
            "parameters": children[4],
            "return_type": children[5],
            "get_body": children[6],
            "set_body": children[7],
        }

    def method_declaration(self, children):
        return {
            "_type": "method_declaration",
            "access_modifier": children[0],
            "shared": children[1],
            "callable": children[2],
            "name": children[3],
            "parameters": children[4],
            "return_type": children[5],
            "body": children[6],
        }

    def method_body(self, children):
        const_block = None
        var_block = None

        for ch in children:
            if isinstance(ch, dict):
                if ch["_type"] == "const_block":
                    if not const_block:
                        const_block = ch
                    else:
                        const_block["items"].extend(ch["items"])
                elif ch["_type"] == "var_block":
                    if not var_block:
                        var_block = ch
                    else:
                        var_block["items"].extend(ch["items"])

        return {
            "_type": "method_body",
            "const_block": const_block,
            "var_block": var_block,
            "statements": children[-2],
        }

    def const_block(self, children):
        return {
            "_type": "const_block",
            "access_modifier": children[0],
            "items": children[1],
        }

    def const_list(self, children):
        return children

    def const_declaration(self, children):
        return {
            "_type": "const_declaration",
            "name": children[0],
            "value": children[1],
        }

    def statement_list(self, children):
        return children  # children

    def statement(self, children):
        if children:
            stmt = children[0]
            if isinstance(stmt, dict) and stmt["_type"] in ("word", "variable"):
                return {
                    "_type": "method_call",
                    "method": stmt,
                    "args": None,
                }

        return children[0] if children else None

    def if_statement(self, children):
        elseifs = []

        for i, ch in enumerate(children):
            if isinstance(ch, Token) and ch.type == "ELSEIF":
                elseifs.append(
                    {
                        "condition": children[i + 1],
                        "statements": children[i + 3],
                    }
                )

        return {
            "_type": "if_statement",
            "condition": children[1],
            "statements": children[3],
            "elseif": elseifs,
            "else_statements": children[-3],
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
        return {
            "_type": "member_access",
            "object": children[0],
            "member": children[1],
        }

    def return_statement(self, children):
        return {
            "_type": "return_statement",
            "expression": children[1],
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
            "op": children[1].value if children[1] is Token else children[1],
            "left": children[0],
            "right": children[2],
        }

    def type_cast(self, children):
        return {
            "_type": "type_cast",
            "expression": children[0],
            "as_type": children[2],
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
            "args": children[1],
        }

    def expression(self, children):
        return {
            "_type": "expression",
            "left": children[0],
            "op": children[1],
            "right": children[2],
        }

    def foreach_statement(self, children):
        return {
            "_type": "for_each_statement",
            "element": children[2],
            "list": children[4],
            "statements": children[6],
        }

    def for_statement(self, children):
        start_stmt = children[1]
        end_stmt = children[3]
        step_stmt = None
        statements = None

        for i, ch in enumerate(children):
            if isinstance(ch, Token):
                if ch.type == "STEP":
                    step_stmt = children[i + 1]
                elif ch.type == "DO":
                    statements = children[i + 1]

        return {
            "_type": "for_statement",
            "start": start_stmt,
            "end": end_stmt,
            "step": step_stmt,
            "statements": statements,
        }

    def break_statement(self, _):
        return {
            "_type": "break_statement",
        }

    def continue_statement(self, _):
        return {
            "_type": "continue_statement",
        }

    def raise_statement(self, children):
        return {
            "_type": "raise_statement",
            "expression": children[1],
        }

    def dispose_statement(self, children):
        return {
            "_type": "dispose_statement",
            "expression": children[1],
        }

    def select_block(self, children):
        select_var = children[0]
        cases = []
        else_stmts = None

        i = 1
        while i < len(children) - 1:
            ch = children[i]
            if isinstance(ch, Token) and ch.type == "ELSE":
                else_stmts = children[i + 1]
            else:
                cases.append(
                    {
                        "case": ch,
                        "statements": children[i + 1],
                    }
                )
            i += 2

        return {
            "_type": "select_block",
            "select_var": select_var,
            "cases": cases,
            "else": else_stmts,
        }

    def lov_case_arg_list(self, children):
        return children

    def lov_case_arg(self, children):
        return children[0]

    def literal_or_var(self, children):
        return children[0]

    def lov_range_expression(self, children):
        return {
            "_type": "lov_range_expression",
            "from": children[0],
            "to": children[2],
        }

    def try_block(self, children):
        excepts = []
        else_statements = []
        finally_statements = []
        statements = []

        except_idx = -1

        for i, ch in enumerate(children):
            if isinstance(ch, Token):
                if ch.type == "EXCEPT":
                    except_idx = i
                elif ch.type == "TRY" and not statements:
                    statements = children[i + 1]
                elif ch.type == "ELSE":
                    else_statements = children[i + 1]
                elif ch.type == "FINALLY":
                    finally_statements = children[i + 1]

        if except_idx != -1:
            while except_idx < len(children):
                ch = children[except_idx]
                if isinstance(ch, Token):
                    if ch.type == "ON":
                        excepts.append(
                            {
                                "name": children[except_idx + 1],
                                "exception_type": children[except_idx + 2],
                                "statements": children[except_idx + 4],
                            }
                        )
                        except_idx += 4
                elif (
                    isinstance(ch, list)
                    and isinstance(children[except_idx - 1], Token)
                    and children[except_idx - 1].type == "EXCEPT"
                ):
                    excepts.append(
                        {
                            "name": None,
                            "exception_type": None,
                            "statements": ch,
                        }
                    )
                except_idx += 1

        return {
            "_type": "try_block",
            "statements": statements,
            "excepts": excepts,
            "else": else_statements,
            "finally": finally_statements,
        }

    def term(self, children):
        return {
            "_type": "term",
            "op": children[1],
            "left": children[0],
            "right": children[2],
        }

    def factor(self, children):
        return {
            "_type": "factor",
            "op": children[0],
            "expression": children[1],
        }

    def mul_op(self, children):
        return children[0]

    def add_op(self, children):
        return children[0]

    def unary_op(self, children):
        return children[0]

    def comparison_op(self, children):
        return children[0]

    def inherited_call(self, children):
        return {
            "_type": "inherited_call",
            "expression": children[1],
        }

    def property_get(self, children):
        return {
            "_type": "property_get",
            "body": children[0],
        }

    def property_set(self, children):
        return {
            "_type": "property_set",
            "body": children[0],
        }

    def var_block(self, children):
        return {
            "_type": "var_block",
            "access_modifier": children[0],
            "items": children[1],
        }

    def variables_list(self, children):
        return [x for xs in children for x in xs]

    def variable_declaration(self, children):
        var_names = []
        var_default_values = []
        vars = []
        var_type = None

        array_regex = r"^((Array Of \w*\[\d+\])|(Array Of \w*)|(Array\[\d+\])|(Array))$"
        is_array = False

        for ch in children:
            if isinstance(ch, dict):
                if ch["_type"] == "variable":
                    var_names.append(ch)
                elif ch["_type"] == "type":
                    var_type = ch
                    is_array = False
                elif ch["_type"] == "type_array":
                    var_type = ch
                    is_array = True
                else:
                    var_default_values.append(ch)

        for name in var_names:
            vars.append(
                {
                    "_type": "variable_declaration",
                    "name": name,
                    "type": var_type,
                    "default_value": (
                        var_default_values
                        if is_array
                        else var_default_values[0] if var_default_values else None
                    ),
                }
            )

        return vars

    def VARIABLE(self, token):
        return {"_type": "variable", "value": token}

    def LITERAL(self, token):
        return {"_type": "literal", "value": token}

    def WORD(self, token):
        return {"_type": "word", "value": token}

    def interface_def(self, children):
        items = {}
        items["_type"] = "interface_def"
        items["access_modifier"] = children[0]
        items["interface_name"] = children[2]
        items["parent"] = children[3]

        for ch in children:
            if isinstance(ch, dict):
                if ch.get("_type") == "interface_body":
                    items["interface_body"] = ch

        return items

    def interface_body(self, children):
        items = {}
        items["interface_property_declarations"] = []
        items["interface_method_declarations"] = []
        items["_type"] = "interface_body"

        for ch in children:
            if isinstance(ch, dict):
                if ch.get("_type") == "interface_property_declaration":
                    items["interface_property_declarations"].append(ch)
                elif ch.get("_type") == "interface_method_declaration":
                    items["interface_method_declarations"].append(ch)

        return items

    def interface_method_declaration(self, children):
        return {
            "_type": "interface_method_declaration",
            "access_modifier": children[0],
            "callable": children[1],
            "name": children[2],
            "parameters": children[3],
            "return_type": children[4],
        }

    def interface_property_declaration(self, children):
        return {
            "_type": "interface_property_declaration",
            "access_modifier": children[0],
            "name": children[2],
            "parameters": children[3],
            "return_type": children[4],
            "get": children[5],
            "set": children[6],
        }

    def INTERFACE_TYPE(self, token):
        return {"_type": "interface", "value": token}

    def CLASS_TYPE(self, token):
        return {"_type": "class", "value": token}

    def type_array(self, children):
        arr_type = None
        arr_size = None

        for ch in children:
            if isinstance(ch, dict):
                if ch['_type'] == 'type':
                    arr_type = ch

        arr_size = children[-1]

        return {"_type": "type_array", "type": arr_type, "size": arr_size}

    def base_type(self, children):
        return children[0]

    def type(self, children):
        return {"_type": "type", "value": children[0]}
    
    def while_statement(self, children):
        return {
            "_type": "while_statement",
            "condition": children[1],
            "statements": children[3],
        }
    
    def with_statement(self, children):
        return {
            "_type": "with_statement",
            "variable": children[1],
            "expression": children[2],
            "statements": children[4],
        }
    
    def repeat_statement(self, children):
        return {
            "_type": "repeat_statement",
            "statements": children[1],
            "condition": children[3],
        }
    
    def delegate_declaration(self, children):
        return {
            "_type": "delegate_declaration",
            "access_modifier": children[0],
            "name": children[2],
            "parameters": children[3],
            "return_type": children[4],
        }
    
    def event_declaration(self, children):
        return {
            "_type": "event_declaration",
            "access_modifier": children[0],
            "name": children[2],
            "delegate_type": children[3],
        }

    def index_access(self, children):
        return {
            "_type": "index_access",
            "object": children[0],
            "index": children[1],
        }