#!/usr/bin/env python3
"""
SimplifiedScript Interpreter v1.0.0
====================================
A lightweight interpreter for the SimplifiedScript (.ss) language.

Supported syntax:
  - Comments:           # this is a comment
  - Variable declaration:
      let x = <expr>;
  - Print:              print(<expr>);
  - Arithmetic:         +  -  *  /  %
  - String concat:      "hello" + name
  - Comparison:         ==  !=  <  >  <=  >=
  - Logical:            &&  ||  !
  - If / else if / else blocks
  - While loops
  - Functions:          func name(params) { ... }  /  return <expr>;
  - Arrays:             [1, 2, 3]  /  arr[0]
  - Dictionaries:       {"key": value}  /  dict["key"]
  - Built-ins:          fetch(url), write(path, data), read(path), exit()
  - Try / catch blocks

Usage:
  python interpreter.py <script.ss>     # run a script
  python interpreter.py                 # start interactive REPL
"""

import sys
import json
import re
import os

# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------

TOKEN_PATTERNS = [
    ("COMMENT",     r"#[^\n]*"),
    ("NUMBER",      r"\d+\.\d+|\d+"),
    ("STRING",      r'"(?:[^"\\]|\\.)*"'),
    ("BOOL",        r"\b(?:true|false)\b"),
    ("NULL",        r"\bnull\b"),
    ("LET",         r"\blet\b"),
    ("FUNC",        r"\bfunc\b"),
    ("RETURN",      r"\breturn\b"),
    ("IF",          r"\bif\b"),
    ("ELSE",        r"\belse\b"),
    ("WHILE",       r"\bwhile\b"),
    ("TRY",         r"\btry\b"),
    ("CATCH",       r"\bcatch\b"),
    ("PRINT",       r"\bprint\b"),
    ("FETCH",       r"\bfetch\b"),
    ("WRITE",       r"\bwrite\b"),
    ("READ",        r"\bread\b"),
    ("EXIT",        r"\bexit\b"),
    ("IDENT",       r"[A-Za-z_][A-Za-z0-9_]*"),
    ("LBRACE",      r"\{"),
    ("RBRACE",      r"\}"),
    ("LBRACKET",    r"\["),
    ("RBRACKET",    r"\]"),
    ("LPAREN",      r"\("),
    ("RPAREN",      r"\)"),
    ("SEMICOLON",   r";"),
    ("COMMA",       r","),
    ("COLON",       r":"),
    ("OP_AND",      r"&&"),
    ("OP_OR",       r"\|\|"),
    ("OP_NOT",      r"!(?!=)"),
    ("OP_LTEQ",     r"<="),
    ("OP_GTEQ",     r">="),
    ("OP_EQ",       r"=="),
    ("OP_NEQ",      r"!="),
    ("OP_LT",       r"<"),
    ("OP_GT",       r">"),
    ("ASSIGN",      r"="),
    ("OP_PLUS",     r"\+"),
    ("OP_MINUS",    r"-"),
    ("OP_STAR",     r"\*"),
    ("OP_SLASH",    r"/"),
    ("OP_PERCENT",  r"%"),
    ("NEWLINE",     r"\n"),
    ("WHITESPACE",  r"[ \t\r]+"),
]

_MASTER_RE = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_PATTERNS)
)

class Token:
    __slots__ = ("type", "value", "line")
    def __init__(self, type_, value, line):
        self.type  = type_
        self.value = value
        self.line  = line
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"


def tokenize(source: str):
    """Return a flat list of meaningful tokens (strips whitespace/comments)."""
    tokens = []
    line = 1
    for m in _MASTER_RE.finditer(source):
        kind  = m.lastgroup
        value = m.group()
        if kind in ("WHITESPACE", "COMMENT"):
            pass
        elif kind == "NEWLINE":
            line += 1
        else:
            tokens.append(Token(kind, value, line))
    return tokens


# ---------------------------------------------------------------------------
# AST node types (plain dicts for simplicity)
# ---------------------------------------------------------------------------
# Every node is a dict with at minimum a "type" key.


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    # -- helpers -------------------------------------------------------------

    def peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def consume(self, expected_type=None):
        tok = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        if tok is None:
            raise ParseError(f"Unexpected end of input (expected {expected_type})")
        if expected_type and tok.type != expected_type:
            raise ParseError(
                f"Line {tok.line}: expected {expected_type}, got {tok.type!r} ({tok.value!r})"
            )
        self.pos += 1
        return tok

    def match(self, *types):
        tok = self.peek()
        if tok and tok.type in types:
            self.pos += 1
            return tok
        return None

    def at_end(self):
        return self.pos >= len(self.tokens)

    # -- program -------------------------------------------------------------

    def parse_program(self):
        stmts = []
        while not self.at_end():
            stmts.append(self.parse_statement())
        return {"type": "Program", "body": stmts}

    # -- statements ----------------------------------------------------------

    def parse_statement(self):
        tok = self.peek()
        if tok is None:
            raise ParseError("Unexpected end of input")

        if tok.type == "LET":
            return self.parse_let()
        if tok.type == "PRINT":
            return self.parse_print()
        if tok.type == "IF":
            return self.parse_if()
        if tok.type == "WHILE":
            return self.parse_while()
        if tok.type == "FUNC":
            return self.parse_func_decl()
        if tok.type == "RETURN":
            return self.parse_return()
        if tok.type == "TRY":
            return self.parse_try()
        if tok.type == "EXIT":
            return self.parse_exit()
        if tok.type == "WRITE":
            return self.parse_write()
        if tok.type == "LBRACE":
            return self.parse_block()

        # expression statement (e.g. function call or assignment)
        expr = self.parse_expression()
        self.match("SEMICOLON")
        return {"type": "ExprStmt", "expr": expr}

    def parse_let(self):
        self.consume("LET")
        name = self.consume("IDENT").value
        self.consume("ASSIGN")
        value = self.parse_expression()
        self.match("SEMICOLON")
        return {"type": "Let", "name": name, "value": value}

    def parse_print(self):
        self.consume("PRINT")
        self.consume("LPAREN")
        expr = self.parse_expression()
        self.consume("RPAREN")
        self.match("SEMICOLON")
        return {"type": "Print", "expr": expr}

    def parse_if(self):
        self.consume("IF")
        self.consume("LPAREN")
        cond = self.parse_expression()
        self.consume("RPAREN")
        then_block = self.parse_block()
        else_block = None
        if self.peek() and self.peek().type == "ELSE":
            self.consume("ELSE")
            if self.peek() and self.peek().type == "IF":
                else_block = self.parse_if()
            else:
                else_block = self.parse_block()
        return {"type": "If", "cond": cond, "then": then_block, "else": else_block}

    def parse_while(self):
        self.consume("WHILE")
        self.consume("LPAREN")
        cond = self.parse_expression()
        self.consume("RPAREN")
        body = self.parse_block()
        return {"type": "While", "cond": cond, "body": body}

    def parse_func_decl(self):
        self.consume("FUNC")
        name   = self.consume("IDENT").value
        self.consume("LPAREN")
        params = []
        while self.peek() and self.peek().type != "RPAREN":
            params.append(self.consume("IDENT").value)
            self.match("COMMA")
        self.consume("RPAREN")
        body = self.parse_block()
        return {"type": "FuncDecl", "name": name, "params": params, "body": body}

    def parse_return(self):
        self.consume("RETURN")
        expr = None
        if self.peek() and self.peek().type != "SEMICOLON":
            expr = self.parse_expression()
        self.match("SEMICOLON")
        return {"type": "Return", "expr": expr}

    def parse_try(self):
        self.consume("TRY")
        try_block = self.parse_block()
        catch_var = None
        catch_block = None
        if self.peek() and self.peek().type == "CATCH":
            self.consume("CATCH")
            self.consume("LPAREN")
            catch_var = self.consume("IDENT").value
            self.consume("RPAREN")
            catch_block = self.parse_block()
        return {
            "type": "Try",
            "try":   try_block,
            "catch_var":   catch_var,
            "catch": catch_block,
        }

    def parse_exit(self):
        self.consume("EXIT")
        self.consume("LPAREN")
        self.consume("RPAREN")
        self.match("SEMICOLON")
        return {"type": "Exit"}

    def parse_write(self):
        self.consume("WRITE")
        self.consume("LPAREN")
        path = self.parse_expression()
        self.consume("COMMA")
        data = self.parse_expression()
        self.consume("RPAREN")
        self.match("SEMICOLON")
        return {"type": "Write", "path": path, "data": data}

    def parse_block(self):
        self.consume("LBRACE")
        stmts = []
        while self.peek() and self.peek().type != "RBRACE":
            stmts.append(self.parse_statement())
        self.consume("RBRACE")
        return {"type": "Block", "body": stmts}

    # -- expressions ---------------------------------------------------------

    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        left = self.parse_logical_or()
        if self.peek() and self.peek().type == "ASSIGN":
            # simple assignment: ident = expr  or  ident[key] = expr
            self.consume("ASSIGN")
            right = self.parse_assignment()
            return {"type": "Assign", "target": left, "value": right}
        return left

    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self.peek() and self.peek().type == "OP_OR":
            op = self.consume().value
            right = self.parse_logical_and()
            left = {"type": "BinOp", "op": op, "left": left, "right": right}
        return left

    def parse_logical_and(self):
        left = self.parse_equality()
        while self.peek() and self.peek().type == "OP_AND":
            op = self.consume().value
            right = self.parse_equality()
            left = {"type": "BinOp", "op": op, "left": left, "right": right}
        return left

    def parse_equality(self):
        left = self.parse_comparison()
        while self.peek() and self.peek().type in ("OP_EQ", "OP_NEQ"):
            op = self.consume().value
            right = self.parse_comparison()
            left = {"type": "BinOp", "op": op, "left": left, "right": right}
        return left

    def parse_comparison(self):
        left = self.parse_additive()
        while self.peek() and self.peek().type in ("OP_LT", "OP_GT", "OP_LTEQ", "OP_GTEQ"):
            op = self.consume().value
            right = self.parse_additive()
            left = {"type": "BinOp", "op": op, "left": left, "right": right}
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.peek() and self.peek().type in ("OP_PLUS", "OP_MINUS"):
            op = self.consume().value
            right = self.parse_multiplicative()
            left = {"type": "BinOp", "op": op, "left": left, "right": right}
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.peek() and self.peek().type in ("OP_STAR", "OP_SLASH", "OP_PERCENT"):
            op = self.consume().value
            right = self.parse_unary()
            left = {"type": "BinOp", "op": op, "left": left, "right": right}
        return left

    def parse_unary(self):
        if self.peek() and self.peek().type == "OP_NOT":
            op = self.consume().value
            operand = self.parse_unary()
            return {"type": "UnaryOp", "op": op, "operand": operand}
        if self.peek() and self.peek().type == "OP_MINUS":
            op = self.consume().value
            operand = self.parse_unary()
            return {"type": "UnaryOp", "op": op, "operand": operand}
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()
        while self.peek() and self.peek().type in ("LBRACKET", "LPAREN"):
            if self.peek().type == "LBRACKET":
                self.consume("LBRACKET")
                index = self.parse_expression()
                self.consume("RBRACKET")
                expr = {"type": "Index", "obj": expr, "index": index}
            elif self.peek().type == "LPAREN":
                self.consume("LPAREN")
                args = []
                while self.peek() and self.peek().type != "RPAREN":
                    args.append(self.parse_expression())
                    self.match("COMMA")
                self.consume("RPAREN")
                expr = {"type": "Call", "callee": expr, "args": args}
        return expr

    def parse_primary(self):
        tok = self.peek()
        if tok is None:
            raise ParseError("Unexpected end of input in expression")

        if tok.type == "NUMBER":
            self.consume()
            v = tok.value
            return {"type": "Literal", "value": float(v) if "." in v else int(v)}

        if tok.type == "STRING":
            self.consume()
            # unescape basic escape sequences
            raw = tok.value[1:-1]
            raw = raw.replace("\\n", "\n").replace("\\t", "\t").replace('\\"', '"').replace("\\\\", "\\")
            return {"type": "Literal", "value": raw}

        if tok.type == "BOOL":
            self.consume()
            return {"type": "Literal", "value": tok.value == "true"}

        if tok.type == "NULL":
            self.consume()
            return {"type": "Literal", "value": None}

        if tok.type == "LBRACKET":
            return self.parse_array_literal()

        if tok.type == "LBRACE":
            return self.parse_dict_literal()

        if tok.type == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            return expr

        # Built-in call expressions
        if tok.type == "FETCH":
            self.consume("FETCH")
            self.consume("LPAREN")
            url_expr = self.parse_expression()
            self.consume("RPAREN")
            return {"type": "Fetch", "url": url_expr}

        if tok.type == "READ":
            self.consume("READ")
            self.consume("LPAREN")
            path_expr = self.parse_expression()
            self.consume("RPAREN")
            return {"type": "Read", "path": path_expr}

        if tok.type == "EXIT":
            self.consume("EXIT")
            self.consume("LPAREN")
            self.consume("RPAREN")
            return {"type": "ExitExpr"}

        if tok.type == "IDENT":
            self.consume()
            return {"type": "Ident", "name": tok.value}

        raise ParseError(f"Line {tok.line}: unexpected token {tok.type!r} ({tok.value!r})")

    def parse_array_literal(self):
        self.consume("LBRACKET")
        elements = []
        while self.peek() and self.peek().type != "RBRACKET":
            elements.append(self.parse_expression())
            self.match("COMMA")
        self.consume("RBRACKET")
        return {"type": "Array", "elements": elements}

    def parse_dict_literal(self):
        self.consume("LBRACE")
        pairs = []
        while self.peek() and self.peek().type != "RBRACE":
            key = self.parse_expression()
            self.consume("COLON")
            val = self.parse_expression()
            pairs.append((key, val))
            self.match("COMMA")
        self.consume("RBRACE")
        return {"type": "Dict", "pairs": pairs}


# ---------------------------------------------------------------------------
# Runtime exceptions
# ---------------------------------------------------------------------------

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class ExitException(Exception):
    pass

class RuntimeError_(Exception):
    pass


# ---------------------------------------------------------------------------
# Environment (scope)
# ---------------------------------------------------------------------------

class Environment:
    def __init__(self, parent=None):
        self._vars  = {}
        self.parent = parent

    def get(self, name):
        if name in self._vars:
            return self._vars[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError_(f"Undefined variable: '{name}'")

    def set(self, name, value):
        """Set in the scope where the variable already exists, else current."""
        if name in self._vars:
            self._vars[name] = value
            return
        if self.parent and self.parent.has(name):
            self.parent.set(name, value)
            return
        self._vars[name] = value

    def define(self, name, value):
        self._vars[name] = value

    def has(self, name):
        if name in self._vars:
            return True
        if self.parent:
            return self.parent.has(name)
        return False


# ---------------------------------------------------------------------------
# Interpreter
# ---------------------------------------------------------------------------

class Interpreter:
    def __init__(self):
        self.global_env = Environment()

    def run(self, source: str):
        tokens = tokenize(source)
        parser = Parser(tokens)
        tree   = parser.parse_program()
        self.exec_program(tree, self.global_env)

    # -- execution -----------------------------------------------------------

    def exec_program(self, node, env):
        for stmt in node["body"]:
            self.exec_stmt(stmt, env)

    def exec_stmt(self, node, env):
        t = node["type"]

        if t == "Let":
            value = self.eval_expr(node["value"], env)
            env.define(node["name"], value)

        elif t == "Print":
            value = self.eval_expr(node["expr"], env)
            print(self.stringify(value))

        elif t == "If":
            cond = self.eval_expr(node["cond"], env)
            if self.is_truthy(cond):
                self.exec_block(node["then"], Environment(env))
            elif node["else"]:
                other = node["else"]
                if other["type"] == "If":
                    self.exec_stmt(other, env)
                else:
                    self.exec_block(other, Environment(env))

        elif t == "While":
            while self.is_truthy(self.eval_expr(node["cond"], env)):
                self.exec_block(node["body"], Environment(env))

        elif t == "FuncDecl":
            env.define(node["name"], {
                "__func__": True,
                "params":   node["params"],
                "body":     node["body"],
                "closure":  env,
            })

        elif t == "Return":
            value = self.eval_expr(node["expr"], env) if node["expr"] else None
            raise ReturnException(value)

        elif t == "Try":
            try:
                self.exec_block(node["try"], Environment(env))
            except (RuntimeError_, Exception) as exc:
                if node["catch"]:
                    catch_env = Environment(env)
                    if node["catch_var"]:
                        catch_env.define(node["catch_var"], str(exc))
                    self.exec_block(node["catch"], catch_env)

        elif t == "Exit":
            raise ExitException()

        elif t == "Write":
            path = self.stringify(self.eval_expr(node["path"], env))
            data = self.eval_expr(node["data"], env)
            self.builtin_write(path, data)

        elif t == "Block":
            self.exec_block(node, Environment(env))

        elif t == "ExprStmt":
            self.eval_expr(node["expr"], env)

        else:
            raise RuntimeError_(f"Unknown statement type: {t}")

    def exec_block(self, node, env):
        for stmt in node["body"]:
            self.exec_stmt(stmt, env)

    # -- evaluation ----------------------------------------------------------

    def eval_expr(self, node, env):
        t = node["type"]

        if t == "Literal":
            return node["value"]

        if t == "Ident":
            return env.get(node["name"])

        if t == "Array":
            return [self.eval_expr(e, env) for e in node["elements"]]

        if t == "Dict":
            return {
                self.stringify(self.eval_expr(k, env)): self.eval_expr(v, env)
                for k, v in node["pairs"]
            }

        if t == "Index":
            obj   = self.eval_expr(node["obj"],   env)
            index = self.eval_expr(node["index"],  env)
            try:
                if isinstance(obj, list):
                    return obj[int(index)]
                return obj[index]
            except (KeyError, IndexError, TypeError) as exc:
                raise RuntimeError_(f"Index error: {exc}")

        if t == "Assign":
            target = node["target"]
            value  = self.eval_expr(node["value"], env)
            if target["type"] == "Ident":
                env.set(target["name"], value)
            elif target["type"] == "Index":
                obj   = self.eval_expr(target["obj"],   env)
                index = self.eval_expr(target["index"],  env)
                if isinstance(obj, list):
                    obj[int(index)] = value
                else:
                    obj[index] = value
            else:
                raise RuntimeError_("Invalid assignment target")
            return value

        if t == "BinOp":
            return self.eval_binop(node, env)

        if t == "UnaryOp":
            operand = self.eval_expr(node["operand"], env)
            if node["op"] == "!":
                return not self.is_truthy(operand)
            if node["op"] == "-":
                return -operand
            raise RuntimeError_(f"Unknown unary op: {node['op']}")

        if t == "Call":
            callee = self.eval_expr(node["callee"], env)
            args   = [self.eval_expr(a, env) for a in node["args"]]
            return self.call_function(callee, args)

        if t == "Fetch":
            url = self.stringify(self.eval_expr(node["url"], env))
            return self.builtin_fetch(url)

        if t == "Read":
            path = self.stringify(self.eval_expr(node["path"], env))
            return self.builtin_read(path)

        if t == "ExitExpr":
            raise ExitException()

        raise RuntimeError_(f"Unknown expression type: {t}")

    def eval_binop(self, node, env):
        op    = node["op"]
        left  = self.eval_expr(node["left"],  env)
        right = self.eval_expr(node["right"], env)

        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return self.stringify(left) + self.stringify(right)
            return left + right
        if op == "-":   return left - right
        if op == "*":   return left * right
        if op == "/":
            if right == 0:
                raise RuntimeError_("Division by zero")
            return left / right
        if op == "%":   return left % right
        if op == "==":  return left == right
        if op == "!=":  return left != right
        if op == "<":   return left <  right
        if op == ">":   return left >  right
        if op == "<=":  return left <= right
        if op == ">=":  return left >= right
        if op == "&&":  return self.is_truthy(left) and self.is_truthy(right)
        if op == "||":  return self.is_truthy(left) or  self.is_truthy(right)
        raise RuntimeError_(f"Unknown binary op: {op}")

    # -- helpers -------------------------------------------------------------

    def call_function(self, callee, args):
        if not isinstance(callee, dict) or not callee.get("__func__"):
            raise RuntimeError_(f"Cannot call non-function value: {callee!r}")
        params  = callee["params"]
        body    = callee["body"]
        closure = callee["closure"]
        if len(args) != len(params):
            raise RuntimeError_(
                f"Expected {len(params)} argument(s), got {len(args)}"
            )
        func_env = Environment(closure)
        for param, arg in zip(params, args):
            func_env.define(param, arg)
        try:
            self.exec_block(body, func_env)
        except ReturnException as ret:
            return ret.value
        return None

    def is_truthy(self, value):
        if value is None or value is False:
            return False
        if isinstance(value, (int, float)) and value == 0:
            return False
        if isinstance(value, str) and value == "":
            return False
        return True

    def stringify(self, value):
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return str(value)

    # -- built-ins -----------------------------------------------------------

    def builtin_fetch(self, url: str):
        """HTTP GET the URL and return parsed JSON (or raw text as string)."""
        try:
            import urllib.request
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "SimplifiedScript/1.0.0"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return body
        except Exception as exc:
            raise RuntimeError_(f"fetch() failed for '{url}': {exc}")

    def builtin_write(self, path: str, data):
        """Write data to a file as JSON (dicts/lists) or plain text."""
        try:
            with open(path, "w", encoding="utf-8") as fh:
                if isinstance(data, (dict, list)):
                    json.dump(data, fh, indent=2)
                else:
                    fh.write(self.stringify(data))
        except OSError as exc:
            raise RuntimeError_(f"write() failed for '{path}': {exc}")

    def builtin_read(self, path: str):
        """Read a file and return parsed JSON or raw text."""
        try:
            with open(path, "r", encoding="utf-8") as fh:
                body = fh.read()
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return body
        except OSError as exc:
            raise RuntimeError_(f"read() failed for '{path}': {exc}")


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

def run_repl():
    interp = Interpreter()
    print("SimplifiedScript REPL v1.0.0")
    print("Type 'exit()' or press Ctrl+C to quit.\n")
    while True:
        try:
            line = input(">>> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not line.strip():
            continue
        try:
            interp.run(line)
        except ExitException:
            print("Goodbye!")
            break
        except (ParseError, RuntimeError_) as exc:
            print(f"Error: {exc}")
        except Exception as exc:
            print(f"Unexpected error: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) == 1:
        run_repl()
        return

    script_path = sys.argv[1]
    if not os.path.isfile(script_path):
        print(f"Error: file not found: '{script_path}'", file=sys.stderr)
        sys.exit(1)

    with open(script_path, "r", encoding="utf-8") as fh:
        source = fh.read()

    interp = Interpreter()
    try:
        interp.run(source)
    except ExitException:
        pass
    except ParseError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError_ as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
