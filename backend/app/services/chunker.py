from pathlib import Path
import hashlib

MAX_CHUNK_CHARS = 1500

RAW_ONLY_EXTENSIONS = {
    ".html", ".css", ".scss", ".sass", ".less",
    ".md", ".txt", ".json", ".yaml", ".yml",
    ".toml", ".xml", ".sh", ".bash",
}


def make_id(base: str, text: str) -> str:
    """Generate stable unique ID using content hash."""
    h = hashlib.md5(text.encode()).hexdigest()[:8]
    return f"{base}::{h}"


def _chunk_raw_text(parsed: dict) -> list:
    """Sliding window chunker for files with no AST (html, css, md etc)."""
    chunks = []
    filepath = parsed["file"]
    language = parsed.get("language", "")
    raw = parsed.get("raw", "")
    filename = Path(filepath).name

    if not raw.strip():
        return chunks

    # For small files just make one chunk
    if len(raw) <= MAX_CHUNK_CHARS:
        text = f"# File: {filename}\n\n{raw}"
        chunks.append({
            "id": make_id(f"{filepath}::raw::0", text),
            "text": text,
            "metadata": {
                "file": filepath,
                "type": "raw",
                "name": filename,
                "language": language,
            }
        })
        return chunks

    # Sliding window for larger files
    for i, start in enumerate(range(0, len(raw), MAX_CHUNK_CHARS)):
        chunk_text = raw[start:start + MAX_CHUNK_CHARS]
        text = f"# File: {filename} (part {i + 1})\n\n{chunk_text}"
        chunks.append({
            "id": make_id(f"{filepath}::raw::{i}", text),
            "text": text,
            "metadata": {
                "file": filepath,
                "type": "raw",
                "name": filename,
                "language": language,
            }
        })

    return chunks


def chunk_parsed_file(parsed: dict) -> list:
    chunks = []
    filepath = parsed["file"]
    language = parsed.get("language", "")
    suffix = Path(filepath).suffix

    # Raw-only files
    if suffix in RAW_ONLY_EXTENSIONS:
        return _chunk_raw_text(parsed)

    # Functions
    for fn in parsed.get("functions", []):
        body = fn["body"][:MAX_CHUNK_CHARS]
        base = f"{filepath}::fn::{fn['name']}::L{fn['start_line']}"
        text = f"# Function: {fn['name']}\n{body}"

        chunks.append({
            "id": make_id(base, text),
            "text": text,
            "metadata": {
                "file": filepath,
                "type": "function",
                "name": fn["name"],
                "start_line": fn["start_line"],
                "language": language,
            }
        })

    # Classes
    for cls in parsed.get("classes", []):
        base = f"{filepath}::cls::{cls['name']}::L{cls['start_line']}"
        text = f"# Class: {cls['name']} in {Path(filepath).name}"

        chunks.append({
            "id": make_id(base, text),
            "text": text,
            "metadata": {
                "file": filepath,
                "type": "class",
                "name": cls["name"],
                "start_line": cls["start_line"],
                "language": language,
            }
        })

    # Imports
    imports = parsed.get("imports", [])
    if imports:
        text = "# Imports\n" + "\n".join(imports)
        base = f"{filepath}::imports::0"

        chunks.append({
            "id": make_id(base, text),
            "text": text,
            "metadata": {
                "file": filepath,
                "type": "imports",
                "name": "imports",
                "language": language,
            }
        })

    # Fallback to raw if no AST chunks
    if not chunks:
        return _chunk_raw_text(parsed)

    return chunks


def chunk_all(parsed_files: list) -> list:
    all_chunks = []
    for pf in parsed_files:
        all_chunks.extend(chunk_parsed_file(pf))
    return all_chunks