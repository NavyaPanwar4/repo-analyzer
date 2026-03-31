import git
import zipfile
import tempfile
import shutil
from pathlib import Path

# Files we can parse with tree-sitter (structured extraction)
PARSEABLE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".rs", ".cpp", ".cc", ".cxx", ".c",
    ".go", ".rb", ".php", ".swift", ".kt",
}

# Files we index as raw text (no AST, just content)
RAW_TEXT_EXTENSIONS = {
    ".html", ".css", ".scss", ".sass", ".less",
    ".md", ".txt", ".json", ".yaml", ".yml",
    ".toml", ".env.example", ".xml", ".svg",
    ".sh", ".bash", ".zsh", ".dockerfile",
}

ALL_SUPPORTED = PARSEABLE_EXTENSIONS | RAW_TEXT_EXTENSIONS

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", "dist", "build",
    ".venv", "venv", ".next", "target", "out", "coverage",
    ".idea", ".vscode", "vendor", "third_party",
}

SKIP_FILES = {
    "package-lock.json", "yarn.lock", "poetry.lock",
    "Pipfile.lock", "Cargo.lock",
}


def ingest_from_url(github_url: str) -> str:
    tmp = tempfile.mkdtemp()
    try:
        git.Repo.clone_from(github_url, tmp, depth=1)
    except Exception as e:
        shutil.rmtree(tmp)
        raise ValueError(f"Failed to clone repo: {e}")
    return tmp


def ingest_from_zip(zip_path: str) -> str:
    tmp = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(tmp)
    except Exception as e:
        shutil.rmtree(tmp)
        raise ValueError(f"Failed to extract ZIP: {e}")
    return tmp


def walk_repo(root: str) -> list:
    files = []
    for path in Path(root).rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in ALL_SUPPORTED and path.name not in {"Dockerfile", "Makefile"}:
            continue
        if path.name in SKIP_FILES:
            continue
        if any(skip in path.parts for skip in SKIP_DIRS):
            continue
        if ".min." in path.name:
            continue
        if path.stat().st_size > 200_000:
            continue
        files.append(path)
    return files


def cleanup(path: str):
    shutil.rmtree(path, ignore_errors=True)