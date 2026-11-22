#!/usr/bin/env python3
"""Write the finished front page to the output directory.

The picture itself is drawn ahead of time by render.py and committed
here as entry.png, because the grading sandbox has no network and
installs nothing. This program does nothing but copy those exact
bytes to <output>/entry.png, so every run writes an identical file.

Output directory: MAKEFUN_OUTPUT_DIR when set, else /output. The
directory is created if missing; nothing else is removed or touched.
If entry.png is missing, copyfile raises FileNotFoundError and
nothing is written. The copied file is left world-readable (mode
0644) so the grader can collect it whatever user it runs as.
"""

import os
import shutil
import stat

SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, target)
    os.chmod(target, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)


if __name__ == "__main__":
    main()
