"""清点跑批结果目录并生成不包含文件正文的清单。"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


JSON_SUMMARY_LIMIT = 2 * 1024 * 1024
TEXT_SUMMARY_LIMIT = 1024 * 1024


def summarize_file(path: Path, root: Path) -> Dict[str, Any]:
    stat = path.stat()
    entry: Dict[str, Any] = {
        "relative_path": str(path.relative_to(root)),
        "suffix": path.suffix.lower(),
        "size_bytes": stat.st_size,
        "modified_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }

    suffix = path.suffix.lower()
    if suffix == ".json":
        if stat.st_size > JSON_SUMMARY_LIMIT:
            entry["summary"] = "文件超过 2 MiB，仅记录文件属性"
        else:
            try:
                with path.open("r", encoding="utf-8-sig") as handle:
                    value = json.load(handle)
            except (json.JSONDecodeError, UnicodeDecodeError) as error:
                entry["parse_note"] = f"JSON无法解析：{error.__class__.__name__}"
            else:
                if isinstance(value, dict):
                    entry["summary"] = {"kind": "object", "keys": list(value.keys())[:100]}
                elif isinstance(value, list):
                    entry["summary"] = {"kind": "array", "item_count": len(value)}
                else:
                    entry["summary"] = {"kind": type(value).__name__}
    elif suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            headers = next(reader, [])
            row_count = sum(1 for _ in reader)
        entry["summary"] = {"headers": headers[:100], "row_count_excluding_header": row_count}
    elif suffix in {".txt", ".md", ".log"}:
        if stat.st_size > TEXT_SUMMARY_LIMIT:
            entry["summary"] = "文本超过 1 MiB，仅记录文件属性"
        else:
            content = path.read_text(encoding="utf-8-sig")
            entry["summary"] = {"character_count": len(content), "line_count": len(content.splitlines())}
    return entry


def main() -> int:
    parser = argparse.ArgumentParser(description="清点跑批输出结果，不读取或打印完整文件正文")
    parser.add_argument("--result-dir", required=True, help="跑批结果目录")
    parser.add_argument("--output", required=True, help="结果清单 JSON 输出路径")
    args = parser.parse_args()

    root = Path(args.result_dir).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"结果目录不存在：{root}")

    files = sorted(path for path in root.rglob("*") if path.is_file())
    entries = [summarize_file(path, root) for path in files]
    manifest = {"result_dir": str(root), "file_count": len(entries), "files": entries}
    output = Path(args.output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"manifest": str(output.resolve()), "file_count": len(entries)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
