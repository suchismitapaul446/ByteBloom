"""ByteBloom: a small beginner-friendly custom scripting language."""
import argparse
import ast
import io
import sys
import tokenize

KEYWORDS = {
    "make": "assignment", "display": "output", "when": "condition",
    "otherwise": "else", "times": "loop", "yes": "true", "no": "false",
    "empty": "none",
}


def translate(source):
    """Translate ByteBloom statements into a readable Python equivalent."""
    result = []
    for line in source.splitlines():
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        if not stripped or stripped.startswith("#"):
            result.append(line)
        elif stripped.startswith("make "):
            result.append(indent + stripped[5:])
        elif stripped.startswith("display "):
            result.append(indent + "print(" + stripped[8:] + ")")
        elif stripped.startswith("when "):
            result.append(indent + "if " + stripped[5:])
        elif stripped == "otherwise:":
            result.append(indent + "else:")
        elif stripped.startswith("times "):
            count = stripped[6:].rstrip().removesuffix(":")
            result.append(indent + "for _bb_index in range(" + count + "):")
        else:
            result.append(line)
    return "\n".join(result)


class SafeRunner:
    """Evaluate a deliberately limited Python AST; no arbitrary function calls."""
    def __init__(self):
        self.env = {}
        self.output = []

    def expr(self, node):
        if isinstance(node, ast.Constant): return node.value
        if isinstance(node, ast.Name):
            if node.id not in self.env: raise NameError("Unknown variable: " + node.id)
            return self.env[node.id]
        if isinstance(node, ast.List): return [self.expr(x) for x in node.elts]
        if isinstance(node, ast.Tuple): return tuple(self.expr(x) for x in node.elts)
        if isinstance(node, ast.BinOp):
            a, b = self.expr(node.left), self.expr(node.right)
            ops = {ast.Add: lambda:a+b, ast.Sub:lambda:a-b, ast.Mult:lambda:a*b,
                   ast.Div:lambda:a/b, ast.FloorDiv:lambda:a//b, ast.Mod:lambda:a%b,
                   ast.Pow:lambda:a**b}
            for typ, fn in ops.items():
                if isinstance(node.op, typ): return fn()
        if isinstance(node, ast.UnaryOp):
            v = self.expr(node.operand)
            if isinstance(node.op, ast.USub): return -v
            if isinstance(node.op, ast.UAdd): return +v
            if isinstance(node.op, ast.Not): return not v
        if isinstance(node, ast.Compare):
            left = self.expr(node.left)
            for op, right_node in zip(node.ops, node.comparators):
                right = self.expr(right_node)
                checks = {ast.Eq:lambda:left==right, ast.NotEq:lambda:left!=right,
                          ast.Lt:lambda:left<right, ast.LtE:lambda:left<=right,
                          ast.Gt:lambda:left>right, ast.GtE:lambda:left>=right}
                matched = next((fn() for typ, fn in checks.items() if isinstance(op, typ)), None)
                if matched is None: raise ValueError("Unsupported comparison")
                if not matched: return False
                left = right
            return True
        if isinstance(node, ast.BoolOp):
            vals = [self.expr(v) for v in node.values]
            return all(vals) if isinstance(node.op, ast.And) else any(vals)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            values = [self.expr(arg) for arg in node.args]
            self.output.append(" ".join(str(value) for value in values))
            return None
        raise ValueError("Unsupported expression: " + type(node).__name__)

    def block(self, statements):
        for stmt in statements:
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                self.env[stmt.targets[0].id] = self.expr(stmt.value)
            elif isinstance(stmt, ast.Expr):
                self.expr(stmt.value)
            elif isinstance(stmt, ast.If):
                self.block(stmt.body if self.expr(stmt.test) else stmt.orelse)
            elif isinstance(stmt, ast.For) and isinstance(stmt.iter, ast.Call) and isinstance(stmt.iter.func, ast.Name) and stmt.iter.func.id == "range":
                args = [self.expr(x) for x in stmt.iter.args]
                if len(args) not in (1, 2, 3): raise ValueError("range expects 1 to 3 values")
                for value in range(*args):
                    if isinstance(stmt.target, ast.Name): self.env[stmt.target.id] = value
                    self.block(stmt.body)
            elif isinstance(stmt, ast.Pass):
                continue
            else:
                raise ValueError("Unsupported statement: " + type(stmt).__name__)

    def run(self, source):
        python_source = translate(source)
        try: tree = ast.parse(python_source)
        except SyntaxError as exc: raise SyntaxError("ByteBloom syntax error: " + str(exc))
        self.block(tree.body)
        return self.output


def run_source(source, runner=None):
    runner = runner or SafeRunner()
    runner.run(source)
    return runner


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run ByteBloom source files")
    parser.add_argument("file", nargs="?")
    parser.add_argument("--translate", action="store_true", help="show translated Python")
    args = parser.parse_args(argv)
    if not args.file:
        print("ByteBloom - enter code; type EXIT to quit")
        runner = SafeRunner()
        while True:
            try: line = input("bloom> ")
            except EOFError: break
            if line.strip().upper() == "EXIT": break
            if not line.strip(): continue
            try:
                runner.run(line)
            except Exception as exc: print(type(exc).__name__ + ":", exc)
        return 0
    with open(args.file, encoding="utf-8") as f: source = f.read()
    if args.translate:
        print(translate(source))
    else:
        runner = run_source(source)
        for line in runner.output: print(line)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
