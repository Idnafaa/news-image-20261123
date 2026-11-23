#!/usr/bin/env python3
"""Entry point for news-image-20261123 (Python 3.13, standard library only).

Copies the repository-held entry.png to /output/entry.png, exactly as the
grader expects. MAKEFUN_OUTPUT_DIR overrides the destination for local runs.
"""
import os
import shutil
from pathlib import Path


def destination() -> Path:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "entry.png"


def main() -> None:
    source = Path(__file__).resolve().with_name("entry.png")
    shutil.copyfile(source, destination())


if __name__ == "__main__":
    main()
