"""从明确指定的脚本目录复制出新的 vNNN 版本，不覆盖已有版本。"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="从指定脚本版本创建新的副本目录")
    parser.add_argument("--script-dir", required=True, help="单个脚本的独立目录")
    parser.add_argument("--from", dest="source_name", required=True, help="明确指定来源目录名，例如 backup 或 v001")
    args = parser.parse_args()

    script_dir = Path(args.script_dir).expanduser().resolve()
    source = (script_dir / args.source_name).resolve()
    if source.parent != script_dir or not source.is_dir():
        raise SystemExit("来源必须是脚本目录下已存在的直接子目录，例如 backup 或 v001。")

    existing_versions = []
    for item in script_dir.iterdir():
        match = re.fullmatch(r"v(\d{3,})", item.name)
        if item.is_dir() and match:
            existing_versions.append(int(match.group(1)))
    next_number = max(existing_versions, default=0) + 1
    while True:
        destination = script_dir / f"v{next_number:03d}"
        if not destination.exists():
            break
        next_number += 1

    shutil.copytree(source, destination)
    print(f"新版本已创建：{destination}")
    print(f"来源版本：{source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
