# ByteBloom – Mini Custom Programming Language

ByteBloom is a small educational scripting language with its own beginner-friendly keywords. It demonstrates source translation, Python AST parsing, and a restricted interpreter. It uses only the Python standard library.

## Features
- `make` for variable assignment
- `display` for output
- `when` and `otherwise` for decisions
- `times` for counted loops
- Arithmetic, comparisons, boolean expressions, lists, and variables
- Interactive prompt and source-to-Python translation
- Restricted AST evaluation (no arbitrary Python `exec`)

## Quick start

```bash
python bytebloom.py examples/hello.bb
python bytebloom.py examples/logic.bb --translate
python bytebloom.py
```

## Language examples

```text
make score = 8
when score > 5:
    display "You passed!"
otherwise:
    display "Try again"

times 3:
    display "Keep learning"
```

## Keyword guide

| ByteBloom | Python equivalent |
|---|---|
| `make x = 5` | `x = 5` |
| `display x` | `print(x)` |
| `when condition:` | `if condition:` |
| `otherwise:` | `else:` |
| `times 4:` | `for _ in range(4):` |
| `yes` / `no` | `True` / `False` |
| `empty` | `None` |

## Project structure

```text
bytebloom_project/
├── bytebloom.py
├── README.md
├── pyproject.toml
├── examples/
│   ├── hello.bb
│   └── logic.bb
└── test_bytebloom.py
```

This is a learning project, not a replacement for Python. The interpreter intentionally supports a limited set of safe statements and expressions.
