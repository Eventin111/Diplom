import os
from pathlib import Path

# какие папки и файлы не хотим видеть в дереве
IGNORED_DIRS = {
    "venv", ".venv", "env",          # виртуальные окружения
    "__pycache__",                   # pycache
    ".git", ".idea", ".vscode",      # служебные
    "node_modules", ".mypy_cache",
}
IGNORED_EXTS = {
    ".pyc", ".pyo", ".pyd", ".log",  # мусорные/служебные файлы
}


def build_tree(start_path: Path, prefix: str = ""):
    lines = []

    # получаем содержимое папки
    entries = list(start_path.iterdir())

    # отфильтровываем игнорируемые директории и файлы
    filtered = []
    for e in entries:
        if e.is_dir() and e.name in IGNORED_DIRS:
            continue
        if e.is_file() and e.suffix in IGNORED_EXTS:
            continue
        filtered.append(e)

    # сортировка: сначала папки, потом файлы, по имени
    filtered.sort(key=lambda p: (p.is_file(), p.name.lower()))

    for idx, entry in enumerate(filtered):
        is_last = idx == len(filtered) - 1
        connector = "└── " if is_last else "├── "

        lines.append(prefix + connector + entry.name)

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            lines.extend(build_tree(entry, prefix + extension))

    return lines


def main():
    root = Path(".").resolve()
    root_name = root.name

    tree_lines = [root_name + "/"]
    tree_lines.extend(build_tree(root))

    out_path = root / "project_tree.txt"

    try:
        with out_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(tree_lines))
    except PermissionError:
        # Сообщение только ASCII, чтобы не словить ошибки кодировки в консоли
        print("PermissionError: cannot write project_tree.txt. "
              "Close this file if it is open or check that it is not a folder.")


if __name__ == "__main__":
    main()