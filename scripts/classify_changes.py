#!/usr/bin/env python3
"""Classify a PR diff and enforce the documentation directory policy."""
import os
from pathlib import PurePosixPath
import subprocess
import sys

DOC_EXTENSIONS = {".md", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf"}


def classify(entries):
    only_docs = bool(entries)
    for name, mode in entries:
        path = PurePosixPath(name)
        under_docs = bool(path.parts) and path.parts[0] == "docs"
        if under_docs and (path.suffix.lower() not in DOC_EXTENSIONS or mode not in ("100644", None)):
            raise ValueError(f"Fichier non autorisé dans docs/ : {name}")
        is_doc = under_docs or (len(path.parts) == 1 and path.suffix.lower() == ".md" and mode in ("100644", None))
        only_docs = only_docs and is_doc
    return "docs" if only_docs else "full"


def git(*args):
    return subprocess.check_output(["git", *args])


def main():
    base = os.environ["BASE_SHA"]
    subprocess.run(["git", "diff", "--check", base, "HEAD"], check=True)
    names = git("diff", "--name-only", "--no-renames", "-z", base, "HEAD").split(b"\0")
    entries = []
    for raw in filter(None, names):
        name = os.fsdecode(raw)
        metadata = git("ls-tree", "-z", "HEAD", "--", name)
        mode = metadata.split(b" ", 1)[0].decode() if metadata else None
        entries.append((name, mode))
    # A docs-only change cannot hide an existing executable or configuration in docs/.
    tree = git("ls-tree", "-rz", "HEAD", "--", "docs/")
    for raw in filter(None, tree.split(b"\0")):
        metadata, name = raw.split(b"\t", 1)
        classify([(os.fsdecode(name), metadata.split(b" ", 1)[0].decode())])
    classification = classify(entries)
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write(f"scope={classification}\n")
    print(f"Périmètre CI : {classification}")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Échec de la classification : {error}", file=sys.stderr)
        sys.exit(1)
