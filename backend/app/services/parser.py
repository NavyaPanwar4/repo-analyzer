from pathlib import Path

PARSERS = {}

PARSEABLE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".rs", ".cpp", ".cc", ".cxx", ".c",
    ".go", ".rb", ".php", ".swift", ".kt",
}

FUNCTION_TYPES = {
    "function_definition",
    "function_declaration",
    "method_definition",
    "method_declaration",
    "arrow_function",
    "function_item",
}

CLASS_TYPES = {
    "class_definition",
    "class_declaration",
    "class_item",
    "struct_item",
    "struct_specifier",
}

IMPORT_TYPES = {
    "import_statement",
    "import_from_statement",
    "import_declaration",
    "use_declaration",
    "package_declaration",
}


def _get_parser(suffix: str):
    if suffix in PARSERS:
        return PARSERS[suffix]

    try:
        from tree_sitter import Language, Parser

        if suffix == ".py":
            import tree_sitter_python as tslang
            lang = Language(tslang.language())
        elif suffix in (".js", ".jsx"):
            import tree_sitter_javascript as tslang
            lang = Language(tslang.language())
        elif suffix in (".ts", ".tsx"):
            import tree_sitter_typescript as m
            lang = m.language_typescript() if suffix == ".ts" else m.language_tsx()
        elif suffix == ".java":
            import tree_sitter_java as tslang
            lang = Language(tslang.language())
        elif suffix == ".rs":
            import tree_sitter_rust as tslang
            lang = Language(tslang.language())
        elif suffix in (".cpp", ".cc", ".cxx", ".c"):
            import tree_sitter_cpp as tslang
            lang = Language(tslang.language())
        else:
            PARSERS[suffix] = None
            return None

        p = Parser(lang)
        PARSERS[suffix] = p
        return p

    except Exception as e:
        print(f"[parser] No grammar for {suffix}: {e}")
        PARSERS[suffix] = None
        return None


def _extract_name(node, code_bytes: bytes) -> str:
    name_node = node.child_by_field_name("name")
    if name_node:
        return name_node.text.decode(errors="ignore")
    for child in node.children:
        if child.type == "identifier":
            return child.text.decode(errors="ignore")
    return "anonymous"


def parse_file(path: Path) -> dict:
    code_bytes = path.read_bytes()
    code_str = code_bytes.decode(errors="ignore")

    result = {
        "file": str(path),
        "language": path.suffix.lstrip(".") or path.name.lower(),
        "functions": [],
        "classes": [],
        "imports": [],
        "raw": code_str,
    }

    # For non-parseable files, just store raw text and return early
    if path.suffix not in PARSEABLE_EXTENSIONS:
        return result

    parser = _get_parser(path.suffix)
    if parser is None:
        return result

    try:
        tree = parser.parse(code_bytes)
    except Exception as e:
        print(f"[parser] Failed to parse {path}: {e}")
        return result

    def walk(node):
        if node.type in FUNCTION_TYPES:
            result["functions"].append({
                "name": _extract_name(node, code_bytes),
                "start_line": node.start_point[0],
                "end_line": node.end_point[0],
                "body": code_bytes[node.start_byte:node.end_byte].decode(errors="ignore"),
            })
        elif node.type in CLASS_TYPES:
            result["classes"].append({
                "name": _extract_name(node, code_bytes),
                "start_line": node.start_point[0],
            })
        elif node.type in IMPORT_TYPES:
            result["imports"].append(
                code_bytes[node.start_byte:node.end_byte].decode(errors="ignore").strip()
            )
        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return result


def parse_all(files: list) -> list:
    parsed = []
    for f in files:
        try:
            parsed.append(parse_file(f))
        except Exception as e:
            print(f"[parser] Skipping {f}: {e}")
    return parsed