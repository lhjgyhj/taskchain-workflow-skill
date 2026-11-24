"""创建具体任务的基础工作目录，不处理任务链或执行脚本。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="创建任务链工作区基础目录")
    parser.add_argument("--path", required=True, help="任务工作文件夹路径")
    args = parser.parse_args()

    root = Path(args.path).expanduser()
    directories = [root / "ai痕迹", root / "doc", root / "code"]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    print(json.dumps({"root": str(root.resolve()), "created": [str(item.resolve()) for item in directories]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
