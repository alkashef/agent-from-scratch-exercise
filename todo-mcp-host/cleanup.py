"""
cleanup.py — interactively list and delete temp/cache/log files in this repo.

Large files (>= LARGE_FILE_THRESHOLD) are highlighted in yellow with a warning
so you don't accidentally delete LLM model blobs or other heavy assets.

Run from the repo root:
    python cleanup.py
"""

import os
import shutil
import sys
from pathlib import Path

# ── configuration ────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.resolve()

# Directories whose entire tree will be treated as one deletion target.
TARGET_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "logs",
    ".cache",
    "htmlcov",
    ".tox",
    "dist",
    "build",
    "*.egg-info",
}

# File extensions that are always temp/generated.
TARGET_EXTENSIONS = {".pyc", ".pyo", ".tmp", ".temp", ".log", ".coverage"}

# Skip anything inside these directories (git internals, virtual envs, etc.).
SKIP_DIRS = {".git", "venv", ".venv", "env", ".env", "node_modules"}

# File extensions that are LLM model blobs — never delete these.
SKIP_EXTENSIONS = {
    ".gguf", ".ggml",           # llama.cpp / Ollama
    ".bin",                     # Hugging Face weights
    ".safetensors",             # safe serialization format
    ".pt", ".pth",              # PyTorch checkpoints
    ".onnx",                    # ONNX runtime
    ".mlmodel",                 # Core ML
    ".llamafile",               # Mozilla llamafile
    ".q4_0", ".q4_1",          # quantised GGML variants
    ".q5_0", ".q5_1",
    ".q8_0",
}

# Files >= this size get a LARGE warning (bytes).
LARGE_FILE_THRESHOLD = 50 * 1024 * 1024  # 50 MB

# ── ANSI colours (disabled on Windows if not supported) ──────────────────────

_WIN = sys.platform == "win32"
try:
    if _WIN:
        import ctypes

        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7
        )
    _COLOUR = True
except Exception:
    _COLOUR = False


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOUR else text


RED = lambda t: _c("31;1", t)
YELLOW = lambda t: _c("33;1", t)
GREEN = lambda t: _c("32;1", t)
CYAN = lambda t: _c("36;1", t)
DIM = lambda t: _c("2", t)


# ── helpers ──────────────────────────────────────────────────────────────────


def _human(size: int) -> str:
    """Return a human-readable byte size string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size) < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def _dir_size(path: Path) -> int:
    """Return total size in bytes of all files under *path*."""
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def _is_skipped(path: Path) -> bool:
    """Return True if *path* is inside a directory we must never touch."""
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    return False


def _matches_target_dir(name: str) -> bool:
    """Return True if *name* matches any TARGET_DIRS pattern (supports * glob)."""
    import fnmatch

    return any(fnmatch.fnmatch(name, pat) for pat in TARGET_DIRS)


# ── discovery ────────────────────────────────────────────────────────────────


def find_targets(root: Path) -> tuple[list[Path], list[Path]]:
    """
    Walk *root* and collect deletion candidates.

    Returns (dirs, files) — dirs first so callers delete them before
    descending into their children as individual files.
    """
    dirs: list[Path] = []
    files: list[Path] = []
    visited_dirs: set[Path] = set()

    for current_dir, subdirs, filenames in os.walk(root, topdown=True):
        current = Path(current_dir)

        if _is_skipped(current):
            subdirs[:] = []
            continue

        # Remove skipped dirs from walk so we never recurse into them.
        subdirs[:] = [
            d
            for d in subdirs
            if d not in SKIP_DIRS and not _is_skipped(current / d)
        ]

        # Check if any subdir matches a target pattern.
        kept = []
        for d in subdirs:
            if _matches_target_dir(d):
                candidate = current / d
                if candidate not in visited_dirs:
                    dirs.append(candidate)
                    visited_dirs.add(candidate)
                # Don't recurse — we'll delete the whole tree at once.
            else:
                kept.append(d)
        subdirs[:] = kept

        # Check files.
        for fname in filenames:
            fpath = current / fname
            if Path(fname).suffix.lower() in SKIP_EXTENSIONS:
                continue
            if Path(fname).suffix.lower() in TARGET_EXTENSIONS or (
                ".tmp." in fname  # editor temp files like foo.py.tmp.12345.abc
            ):
                files.append(fpath)

    return dirs, files


# ── interactive deletion ──────────────────────────────────────────────────────


def _prompt(message: str) -> str:
    """Read a line from stdin, stripping whitespace."""
    try:
        return input(message).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return "n"


def _delete_dir(path: Path) -> None:
    """Remove *path* and all its contents."""
    shutil.rmtree(path, ignore_errors=False)


def _delete_file(path: Path) -> None:
    """Remove a single file."""
    path.unlink()


def _confirm_and_delete(
    path: Path,
    size: int,
    is_dir: bool,
    index: int,
    total: int,
) -> bool:
    """
    Print details about *path* and ask the user whether to delete it.

    Returns True if deleted, False if skipped.
    """
    kind = "DIR " if is_dir else "FILE"
    size_str = _human(size)
    rel = path.relative_to(REPO_ROOT)

    large = size >= LARGE_FILE_THRESHOLD
    size_label = YELLOW(f"{size_str} ⚠ LARGE") if large else DIM(size_str)

    counter = DIM(f"[{index}/{total}]")
    print(f"\n{counter} {CYAN(kind)} {rel}  {size_label}")

    if large:
        print(
            YELLOW(
                "  ⚠  This item is large — it may be an LLM model or dataset. "
                "Think before deleting."
            )
        )

    answer = _prompt("  Delete? [y/N/q] ")

    if answer == "q":
        print(RED("Aborted by user."))
        sys.exit(0)

    if answer == "y":
        try:
            if is_dir:
                _delete_dir(path)
            else:
                _delete_file(path)
            print(GREEN("  Deleted."))
            return True
        except Exception as exc:
            print(RED(f"  Error: {exc}"))
    else:
        print(DIM("  Skipped."))

    return False


# ── main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    """Entry point: discover and interactively delete temp/cache/log items."""
    print(CYAN(f"\nScanning repo: {REPO_ROOT}"))
    dirs, files = find_targets(REPO_ROOT)

    if not dirs and not files:
        print(GREEN("Nothing to clean up."))
        return

    total = len(dirs) + len(files)
    print(f"\nFound {CYAN(str(total))} item(s) to review "
          f"({len(dirs)} dir(s), {len(files)} file(s)).\n")
    print(DIM("Tip: Enter 'q' at any prompt to quit immediately.\n"))
    print("─" * 60)

    deleted = 0
    index = 0

    # Dirs first (sorted by depth descending so children are removed before parents).
    dirs.sort(key=lambda p: len(p.parts), reverse=True)

    for path in dirs:
        index += 1
        if not path.exists():
            continue  # already gone (parent was deleted earlier)
        size = _dir_size(path)
        if _confirm_and_delete(path, size, is_dir=True, index=index, total=total):
            deleted += 1

    for path in files:
        index += 1
        if not path.exists():
            continue
        size = path.stat().st_size
        if _confirm_and_delete(path, size, is_dir=False, index=index, total=total):
            deleted += 1

    print("\n" + "─" * 60)
    print(GREEN(f"Done. {deleted}/{total} item(s) deleted."))


if __name__ == "__main__":
    main()
