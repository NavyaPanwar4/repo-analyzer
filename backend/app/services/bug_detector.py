import re
from pathlib import Path

def detect_bugs(parsed_files: list) -> list:
    """
    Run static analysis heuristics across all parsed files.
    Returns a list of findings with file, line, severity, and message.
    """
    findings = []

    for pf in parsed_files:
        filepath = pf["file"]
        language = pf.get("language", "")
        raw = pf.get("raw", "")
        lines = raw.splitlines()

        if language == "py":
            findings.extend(_check_python(filepath, lines, pf))
        elif language in ("js", "jsx", "ts", "tsx"):
            findings.extend(_check_javascript(filepath, lines, pf))

        # Universal checks that apply to all languages
        findings.extend(_check_universal(filepath, lines))

    return findings


def _check_python(filepath: str, lines: list, pf: dict) -> list:
    findings = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        lineno = i + 1

        # Bare except clause
        if re.match(r"^except\s*:", stripped):
            findings.append({
                "file": filepath,
                "line": lineno,
                "severity": "warning",
                "rule": "bare-except",
                "message": "Bare `except:` catches everything including KeyboardInterrupt. Use `except Exception:` or a specific exception.",
                "snippet": line.rstrip(),
            })

        # Mutable default argument
        if re.search(r"def\s+\w+\(.*=\s*(\[\]|\{\}|\(\))", stripped):
            findings.append({
                "file": filepath,
                "line": lineno,
                "severity": "error",
                "rule": "mutable-default-arg",
                "message": "Mutable default argument ([], {}, ()) is shared across all calls. Use `None` and initialise inside the function.",
                "snippet": line.rstrip(),
            })

        # == None instead of is None
        if re.search(r"==\s*None|!=\s*None", stripped) and "==" in stripped:
            findings.append({
                "file": filepath,
                "line": lineno,
                "severity": "warning",
                "rule": "none-comparison",
                "message": "Use `is None` / `is not None` instead of `== None` / `!= None`.",
                "snippet": line.rstrip(),
            })

        # Print statement left in (debug artifact)
        if re.match(r"^\s*print\(", line) and "logger" not in line:
            findings.append({
                "file": filepath,
                "line": lineno,
                "severity": "info",
                "rule": "print-statement",
                "message": "Debug `print()` found. Consider using a logger instead.",
                "snippet": line.rstrip(),
            })

        # TODO / FIXME / HACK comments
        if re.search(r"#\s*(TODO|FIXME|HACK|XXX)", line, re.IGNORECASE):
            findings.append({
                "file": filepath,
                "line": lineno,
                "severity": "info",
                "rule": "todo-comment",
                "message": f"Unresolved comment: {stripped}",
                "snippet": line.rstrip(),
            })

        # Hardcoded credentials
        if re.search(r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]{4,}['\"]", stripped, re.IGNORECASE):
            findings.append({
                "file": filepath,
                "line": lineno,
                "severity": "error",
                "rule": "hardcoded-secret",
                "message": "Possible hardcoded credential. Move to environment variables.",
                "snippet": re.sub(r"=\s*['\"][^'\"]+['\"]", "= '***'", line.rstrip()),
            })

    # Functions with too many lines (complexity smell)
    for fn in pf.get("functions", []):
        length = fn["end_line"] - fn["start_line"]
        if length > 60:
            findings.append({
                "file": filepath,
                "line": fn["start_line"] + 1,
                "severity": "warning",
                "rule": "long-function",
                "message": f"`{fn['name']}` is {length} lines long. Consider breaking it into smaller functions.",
                "snippet": f"def {fn['name']}(...)",
            })

    return findings


def _check_javascript(filepath: str, lines: list, pf: dict) -> list:
    findings = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        lineno = i + 1

        # == instead of ===
        if re.search(r"[^=!<>]==[^=]", stripped) and "===" not in stripped:
            findings.append({
                "file": filepath,
                "line": lineno,
                "severity": "warning",
                "rule": "loose-equality",
                "message": "Use `===` instead of `==` to avoid type coercion bugs.",
                "snippet": line.rstrip(),
            })

        # console.log left in
        if re.search(r"console\.(log|warn|error|debug)\(", stripped):
            findings.append({
                "file": filepath,
                "line": lineno,
                "severity": "info",
                "rule": "console-log",
                "message": "Debug `console.log` found. Remove before production.",
                "snippet": line.rstrip(),
            })

        # var instead of let/const
        if re.match(r"^\s*var\s+", line):
            findings.append({
                "file": filepath,
                "line": lineno,
                "severity": "warning",
                "rule": "no-var",
                "message": "Use `const` or `let` instead of `var` to avoid hoisting issues.",
                "snippet": line.rstrip(),
            })

        # Hardcoded credentials
        if re.search(r"(password|secret|apiKey|api_key|token)\s*[:=]\s*['\"][^'\"]{4,}['\"]", stripped, re.IGNORECASE):
            findings.append({
                "file": filepath,
                "line": lineno,
                "severity": "error",
                "rule": "hardcoded-secret",
                "message": "Possible hardcoded credential. Move to environment variables.",
                "snippet": re.sub(r"[:=]\s*['\"][^'\"]+['\"]", ": '***'", line.rstrip()),
            })

        # TODO / FIXME
        if re.search(r"//\s*(TODO|FIXME|HACK|XXX)", line, re.IGNORECASE):
            findings.append({
                "file": filepath,
                "line": lineno,
                "severity": "info",
                "rule": "todo-comment",
                "message": f"Unresolved comment: {stripped}",
                "snippet": line.rstrip(),
            })

    return findings


def _check_universal(filepath: str, lines: list) -> list:
    findings = []

    for i, line in enumerate(lines):
        lineno = i + 1

        # Extremely long lines
        if len(line.rstrip()) > 300:
            findings.append({
                "file": filepath,
                "line": lineno,
                "severity": "info",
                "rule": "long-line",
                "message": f"Line is {len(line.rstrip())} characters. Consider splitting for readability.",
                "snippet": line[:80].rstrip() + "...",
            })

    return findings


def group_by_severity(findings: list) -> dict:
    grouped = {"error": [], "warning": [], "info": []}
    for f in findings:
        grouped[f["severity"]].append(f)
    return grouped


def findings_summary(findings: list) -> dict:
    grouped = group_by_severity(findings)
    return {
        "total": len(findings),
        "errors": len(grouped["error"]),
        "warnings": len(grouped["warning"]),
        "info": len(grouped["info"]),
        "findings": findings,
    }