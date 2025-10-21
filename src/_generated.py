from lark import Transformer, v_args


class ForeTransformer(Transformer):
    # === Литералы ===
    def LITERAL_STRING(self, token):
        s = token.value
        # Удаляем кавычки и обрабатываем raw-строки
        if s.startswith(('r"', "r'", 'ur"', "ur'", 'br"', "br'", 'fr"', "fr'")):
            s = s[1:]
        elif s.startswith(('b"', "b'", 'u"', "u'", 'f"', "f'")):
            s = s[1:]
        if (s.startswith('"') and s.endswith('"')) or (
            s.startswith("'") and s.endswith("'")
        ):
            s = s[1:-1]
        return {"type": "literal", "value_type": "string", "value": s}

    def LITERAL_INTEGER(self, token):
        return {"type": "literal", "value_type": "integer", "value": int(token)}

    def LITERAL_DOUBLE(self, token):
        return {"type": "literal", "value_type": "double", "value": float(token)}

    def LITERAL_BOOLEAN(self, token):
        return {
            "type": "literal",
            "value_type": "boolean",
            "value": token.lower() == "true",
        }

    def NULL(self, _):
        return {"type": "literal", "value_type": "null", "value": None}

    # === Идентификаторы и типы ===
    def WORD(self, token):
        return str(token)

    def TYPE(self, token):
        return str(token)

    def BASE_TYPE(self, token):
        return str(token)

    def CLASS_TYPE(self, token):
        return str(token)

    def INTERFACE_TYPE(self, token):
        return str(token)

    # === Модификаторы доступа ===
    def access_modifier(self, items):
        return items[0]

    def protected_friend(self, _):
        return "Protected Friend"

    # === Корень программы ===
    def unit(self, items):
        return {"type": "unit", "declarations": [d for d in items if d is not None]}

    # === Классы ===
    def class_def(self, items):
        i = 0
        access = None
        shared = False

        if isinstance(items[i], str):
            if items[i] in (
                "Public",
                "Private",
                "Protected",
                "Friend",
                "Protected Friend",
            ):
                access = items[i]
                i += 1

        if i < len(items) and items[i] == "Shared":
            shared = True
            i += 1

        i += 1  # skip CLASS
        name = items[i]
        i += 1
        i += 1  # skip _COLON

        base_types = []
        while i < len(items) and items[i] != "class_body":
            if items[i] != ",":
                base_types.append(items[i])
            i += 1

        body = items[i]
        i += 1  # class_body
        # END CLASS name ;
        return {
            "type": "class",
            "name": name,
            "access": access,
            "shared": shared,
            "base_types": base_types,
            "members": body["members"],
        }

    def class_body(self, items):
        return {"members": [m for m in items if m is not None]}

    # === Конструкторы ===
    def constructor(self, items):
        i = 0
        access = None
        if isinstance(items[i], str) and items[i] in (
            "Public",
            "Private",
            "Protected",
            "Friend",
            "Protected Friend",
        ):
            access = items[i]
            i += 1

        i += 1  # CONSTRUCTOR
        name = items[i]
        i += 1
        params = items[i]
        i += 1  # parameter_list_optional
        i += 1  # _SEMICOLON
        body = items[i]
        i += 1  # method_body
        # CONSTRUCTOR name ;
        return {
            "type": "constructor",
            "name": name,
            "access": access,
            "parameters": params,
            "body": body,
        }

    # === Свойства ===
    def property_declaration(self, items):
        i = 0
        access = None
        shared = False

        if isinstance(items[i], str) and items[i] in (
            "Public",
            "Private",
            "Protected",
            "Friend",
            "Protected Friend",
        ):
            access = items[i]
            i += 1

        if i < len(items) and items[i] == "Shared":
            shared = True
            i += 1

        i += 1  # PROPERTY
        name = items[i]
        i += 1
        params = items[i]
        i += 1
        i += 1  # _COLON
        ptype = items[i]
        i += 1

        getter = setter = None
        while i < len(items):
            if isinstance(items[i], dict):
                if items[i].get("type") == "property_get":
                    getter = items[i]
                elif items[i].get("type") == "property_set":
                    setter = items[i]
            i += 1

        return {
            "type": "property",
            "name": name,
            "access": access,
            "shared": shared,
            "parameters": params,
            "type": ptype,
            "getter": getter,
            "setter": setter,
        }

    def property_get(self, items):
        return {"type": "property_get", "body": items[1]}

    def property_set(self, items):
        return {"type": "property_set", "body": items[1]}

    # === Методы ===
    def method_declaration(self, items):
        i = 0
        access = None
        shared = False
        kind = None

        if isinstance(items[i], str) and items[i] in (
            "Public",
            "Private",
            "Protected",
            "Friend",
            "Protected Friend",
        ):
            access = items[i]
            i += 1

        if i < len(items) and items[i] == "Shared":
            shared = True
            i += 1

        kind = items[i].lower()
        i += 1  # SUB / FUNCTION
        name = items[i]
        i += 1
        params = items[i]
        i += 1

        return_type = None
        if i < len(items) and items[i] != "method_body":
            i += 1  # skip _COLON
            return_type = items[i]
            i += 1

        i += 1  # _SEMICOLON
        body = items[i]
        i += 1
        # CALLABLE name ;
        return {
            "type": "method",
            "kind": kind,
            "name": name,
            "access": access,
            "shared": shared,
            "parameters": params,
            "return_type": return_type,
            "body": body,
        }

    # === Параметры ===
    def parameter_list_optional(self, items):
        return items[0] if items else []

    def parameter_list(self, items):
        return items

    def parameter(self, items):
        i = 0
        var = False
        if items[i] == "Var":
            var = True
            i += 1

        names = []
        while i < len(items) and items[i] != ":":
            names.append(items[i])
            i += 1
            if i < len(items) and items[i] == ",":
                i += 1

        i += 1  # skip _COLON
        ptype = items[i]
        i += 1

        default = None
        if i < len(items) and items[i] == "=":
            i += 1
            default = items[i]

        return {"names": names, "type": ptype, "default": default, "var": var}

    # === Тело метода ===
    def method_body(self, items):
        const_block = None
        var_block = None
        statements = []

        for item in items:
            if not item:
                continue
            if item["type"] == "method_const_block":
                const_block = item
            elif item["type"] == "var_block":
                var_block = item
            elif item["type"] == "statement_list":
                statements = item["statements"]

        return {
            "const_block": const_block,
            "var_block": var_block,
            "statements": statements,
        }

    def statement_list(self, items):
        return {"statements": [s for s in items if s is not None]}

    # === Блоки переменных и констант ===
    def const_block(self, items):
        i = 0
        access = None
        if isinstance(items[i], str) and items[i] in (
            "Public",
            "Private",
            "Protected",
            "Friend",
            "Protected Friend",
        ):
            access = items[i]
            i += 1

        # _CONST is ignored (optional)
        decls = [d for d in items[i:] if d is not None]
        return {"type": "const_block", "access": access, "declarations": decls}

    def method_const_block(self, items):
        return {
            "type": "method_const_block",
            "declarations": [d for d in items if d is not None],
        }

    def method_const_declaration(self, items):
        return {"name": items[0], "value": items[2]}

    def var_block(self, items):
        return {"type": "var_block", "declarations": items[1]}

    def variables_list(self, items):
        return [v for v in items if v is not None]

    def variable_declaration(self, items):
        return {"names": list(items[0]), "type": items[1], "default": items[2]}

    # === Поля ===
    def field_declaration(self, items):
        i = 0
        access = None
        shared = False

        if isinstance(items[i], str) and items[i] in (
            "Public",
            "Private",
            "Protected",
            "Friend",
            "Protected Friend",
        ):
            access = items[i]
            i += 1

        if i < len(items) and items[i] == "Shared":
            shared = True
            i += 1

        name = items[i]
        i += 1
        i += 1  # _COLON
        ftype = items[i]

        return {
            "type": "field",
            "name": name,
            "access": access,
            "shared": shared,
            "type": ftype,
        }

    # === Enum ===
    def enum_declaration(self, items):
        i = 0
        access = None
        if isinstance(items[i], str) and items[i] in (
            "Public",
            "Private",
            "Protected",
            "Friend",
            "Protected Friend",
        ):
            access = items[i]
            i += 1

        i += 1  # ENUM
        name = items[i]
        i += 1
        body = items[i]
        i += 1
        # END ENUM name ;
        return {"type": "enum", "name": name, "access": access, "values": body}

    def enum_body(self, items):
        return [v for v in items if v is not None]

    def enum_value(self, items):
        return {"name": items[0], "value": items[2]}

    # === Операторы ===
    def assignment_statement(self, items):
        return {"type": "assignment", "target": items[0], "value": items[1]}

    def return_statement(self, items):
        expr = items[0] if items else None
        return {"type": "return", "value": expr}

    def compound_statement(self, items):
        return items[0]  # statement_list

    def if_statement(self, items):
        branches = []
        i = 0
        cond = items[i]
        i += 1
        then_body = []
        while i < len(items) and items[i] not in ("Elseif", "Else"):
            then_body.append(items[i])
            i += 1
        branches.append({"condition": cond, "body": then_body})

        while i < len(items) and items[i] == "Elseif":
            i += 1
            cond = items[i]
            i += 1
            elseif_body = []
            while i < len(items) and items[i] not in ("Elseif", "Else"):
                elseif_body.append(items[i])
                i += 1
            branches.append({"condition": cond, "body": elseif_body})

        else_body = []
        if i < len(items) and items[i] == "Else":
            i += 1
            else_body = items[i:]

        return {"type": "if", "branches": branches, "else": else_body}

    def for_statement(self, items):
        init = items[0]
        to_expr = items[1]
        step = None
        i = 2
        if i < len(items) and items[i] == "Step":
            i += 1
            step = items[i]
            i += 1
        i += 1  # DO
        body = items[i:]
        return {"type": "for", "init": init, "to": to_expr, "step": step, "body": body}

    def foreach_statement(self, items):
        var = items[0]
        collection = items[1]
        body = items[2:]
        return {"type": "foreach", "variable": var, "in": collection, "body": body}

    def continue_statement(self, _):
        return {"type": "continue"}

    def break_statement(self, _):
        return {"type": "break"}

    def try_block(self, items):
        i = 0
        try_body = []
        while i < len(items) and items[i] not in ("Except", "Finally"):
            try_body.append(items[i])
            i += 1

        except_on = None
        except_body = None
        finally_body = None

        if i < len(items) and items[i] == "Except":
            i += 1
            if i < len(items) and items[i] == "On":
                i += 1
                exc_var = items[i]
                i += 1
                i += 1  # :
                exc_type = items[i]
                i += 1
                # skip optional comma types
                while i < len(items) and items[i] == ",":
                    i += 2  # skip , TYPE
                i += 1  # DO
                except_on_body = []
                while i < len(items) and items[i] not in ("Except", "Finally"):
                    except_on_body.append(items[i])
                    i += 1
                except_on = {
                    "variable": exc_var,
                    "type": exc_type,
                    "body": except_on_body,
                }

            if i < len(items) and items[i] == "Except":
                i += 1
                except_body = []
                while i < len(items) and items[i] != "Finally":
                    except_body.append(items[i])
                    i += 1

        if i < len(items) and items[i] == "Finally":
            i += 1
            finally_body = items[i:]

        return {
            "type": "try",
            "try": try_body,
            "except_on": except_on,
            "except": except_body,
            "finally": finally_body,
        }

    # Обработка CASE внутри SELECT
    def select_block__case_clause(self, items):
        # Эта функция не вызывается напрямую — обработка в select_block
        pass

    # Но Lark не создаёт отдельного правила для CASE ... : ..., поэтому обрабатываем вручную:
    # В грамматике: (CASE LITERAL ("," LITERAL)* ("To" LITERAL)* ":" statement*)*
    # Мы не можем легко это распарсить без контекста, поэтому изменим подход:

    # Вместо этого, перехватим все элементы после SELECT CASE WORD как позиционные аргументы
    # и обработаем их в select_block (см. выше). Это ограничение Lark без явного правила.

    # Альтернатива: добавить правило в грамматику, но по условию — нельзя менять грамматику.
    # Поэтому оставим как есть: в items будут чередоваться:
    # [selector, "Case", lit1, ",", lit2, ":", stmt, stmt, "Case", ...]

    # Перепишем select_block с учётом этого:

    # ⚠️ Переписываем select_block с корректной обработкой CASE
    def select_block(self, items):
        if not items:
            return {"type": "select", "selector": None, "cases": [], "else": []}
        selector = items[0]
        cases = []
        else_body = []
        i = 1

        while i < len(items):
            if items[i] == "Case":
                i += 1
                values = []
                # Собираем значения до ":"
                while i < len(items) and items[i] != ":":
                    if items[i] not in (",", "To"):
                        values.append(items[i])
                    i += 1
                i += 1  # skip ":"
                case_body = []
                while i < len(items) and items[i] not in ("Case", "Else"):
                    case_body.append(items[i])
                    i += 1
                cases.append({"values": values, "body": case_body})
            elif items[i] == "Else":
                i += 1
                else_body = items[i:]
                break
            else:
                i += 1

        return {
            "type": "select",
            "selector": selector,
            "cases": cases,
            "else": else_body,
        }

    def statement(self, items):
        if not items:
            return None
        stmt = items[0]
        if isinstance(stmt, dict):
            return stmt
        if len(items) == 2 and items[0] == "Inherited":
            return {"type": "inherited_call", "target": items[1]}
        return stmt

    # === Выражения ===
    def expression(self, items):
        if len(items) == 1:
            return items[0]
        node = items[0]

        # Обработка сравнения
        if (
            len(items) >= 2
            and isinstance(items[1], str)
            and items[1] in ("=", "<>", "<", "<=", ">", ">=")
        ):
            if len(items) >= 3:
                node = {
                    "type": "binary_op",
                    "op": items[1],
                    "left": node,
                    "right": items[2],
                }
                items = items[3:]
            else:
                return node

        # type_cast
        if (
            len(items) >= 1
            and isinstance(items[-1], str)
            and items[-1].startswith("As ")
        ):
            node = {"type": "cast", "expr": node, "to_type": items[-1][3:]}

        # type_check
        if (
            len(items) >= 1
            and isinstance(items[-2], str)
            and items[-2].startswith("Is ")
        ):
            node = {"type": "is_check", "expr": node, "type": items[-2][3:]}

        return node

    def ternary_expression(self, items):
        return {
            "type": "ternary",
            "condition": items[0],
            "true_expr": items[1],
            "false_expr": items[2],
        }

    def simple_expression(self, items):
        if len(items) == 1:
            return items[0]
        expr = items[0]
        for i in range(1, len(items), 2):
            op = items[i]
            right = items[i + 1]
            expr = {"type": "binary_op", "op": op, "left": expr, "right": right}
        return expr

    def term(self, items):
        if len(items) == 1:
            return items[0]
        expr = items[0]
        for i in range(1, len(items), 2):
            op = items[i]
            right = items[i + 1]
            expr = {"type": "binary_op", "op": op, "left": expr, "right": right}
        return expr

    def factor(self, items):
        if len(items) == 1:
            return items[0]
        return {"type": "unary_op", "op": items[0], "expr": items[1]}

    def atom(self, items):
        return items[0]

    def method_call(self, items):
        return {
            "type": "call",
            "function": items[0],
            "arguments": items[1] if len(items) > 1 else [],
        }

    def argument_list(self, items):
        return items

    def member_access(self, items):
        return {"type": "member", "object": items[0], "member": items[1]}

    def index_access(self, items):
        return {"type": "index", "object": items[0], "index": items[1]}

    def constructor_call(self, items):
        return {"type": "new", "class": items[1]}

    # === Операторы ===
    def add_op(self, items):
        return str(items[0])

    def mul_op(self, items):
        return str(items[0])

    def unary_op(self, items):
        return str(items[0])

    def comparison_op(self, items):
        return str(items[0])

    # === Ключевые слова как строки ===
    PUBLIC = lambda self, _: "Public"
    PRIVATE = lambda self, _: "Private"
    PROTECTED = lambda self, _: "Protected"
    FRIEND = lambda self, _: "Friend"
    SHARED = lambda self, _: "Shared"
    SUB = lambda self, _: "Sub"
    FUNCTION = lambda self, _: "Function"
    CLASS = lambda self, _: "Class"
    BEGIN = lambda self, _: "Begin"
    END = lambda self, _: "End"
    IF = lambda self, _: "If"
    THEN = lambda self, _: "Then"
    ELSE = lambda self, _: "Else"
    ELSEIF = lambda self, _: "Elseif"
    RETURN = lambda self, _: "Return"
    GET = lambda self, _: "Get"
    SET = lambda self, _: "Set"
    PROPERTY = lambda self, _: "Property"
    CONSTRUCTOR = lambda self, _: "Constructor"
    FOR = lambda self, _: "For"
    EACH = lambda self, _: "Each"
    TO = lambda self, _: "To"
    DO = lambda self, _: "Do"
    IN = lambda self, _: "In"
    BREAK = lambda self, _: "Break"
    CONTINUE = lambda self, _: "Continue"
    NEW = lambda self, _: "New"
    STEP = lambda self, _: "Step"
    INHERITED = lambda self, _: "Inherited"
    ENUM = lambda self, _: "Enum"
    TRY = lambda self, _: "Try"
    EXCEPT = lambda self, _: "Except"
    ON = lambda self, _: "On"
    FINALLY = lambda self, _: "Finally"
    SELECT = lambda self, _: "Select"
    CASE = lambda self, _: "Case"

    def AS_KEYWORD(self, _):
        return "As"

    def IS_KEYWORD(self, _):
        return "Is"

    # Обработка AS Type / IS Type в expression
    def type_cast(self, items):
        return f"As {items[1]}"

    def type_check(self, items):
        return f"Is {items[1]}"

    # === Игнорируемые токены ===
    def _SEMICOLON(self, _):
        return None

    def _COLON(self, _):
        return ":"

    def _ASSIGNMENT(self, _):
        return ":="

    def _QUESTION_MARK(self, _):
        return "?"

    def _VAR(self, _):
        return "Var"

    def _CONST(self, _):
        return "Const"
