"""将任务链中的后端脚本按节点名称拆分到独立目录。"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from _taskchain_utils import (
    choose_version,
    component,
    is_script_node,
    iter_workflow_nodes,
    language_extension,
    load_json,
    safe_name,
    script_details,
    write_json,
)


def collect_scripts(data: Dict[str, Any], version_id: str | None) -> tuple[Dict[str, Any], List[Dict[str, Any]], str]:
    version, selection = choose_version(data, version_id)
    version_data = version.get("data") or {}
    topology = version_data.get("topology") or {}
    scripts: List[Dict[str, Any]] = []
    for node, location in iter_workflow_nodes(topology):
        if not is_script_node(node):
            continue
        comp = component(node)
        details = script_details(node)
        scripts.append({
            "name": node.get("name") or comp.get("name") or "未命名脚本",
            "component_name": comp.get("name"),
            "component_code": comp.get("code"),
            "component_desc": comp.get("desc"),
            "component_type": comp.get("type"),
            "bean_name": comp.get("beanName"),
            "node_id": node.get("id"),
            "workflow_location": location,
            "language": details["language"],
            "code": details["code"],
            "input_args": details["input_args"],
            "output_args": [
                {"key": arg.get("key"), "name": arg.get("name"), "type": arg.get("type"), "required": arg.get("required")}
                for arg in (comp.get("outputArgs") or [])
                if isinstance(arg, dict)
            ],
        })
    return version, scripts, selection


def main() -> int:
    parser = argparse.ArgumentParser(description="按后端脚本节点拆分任务链脚本")
    parser.add_argument("--source", required=True, help="任务链 JSON 文件")
    parser.add_argument("--output-dir", required=True, help="脚本分类根目录，通常是任务工作区的 code 目录")
    parser.add_argument("--version-id", help="可选，指定 versionInfo 中的版本 ID")
    args = parser.parse_args()

    source = Path(args.source).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    data = load_json(source)
    version, scripts, selection = collect_scripts(data, args.version_id)
    if not scripts:
        raise SystemExit("未发现可拆分的后端脚本节点；没有创建输出目录。")

    name_counts = Counter(item["name"] for item in scripts)
    duplicate_index: Counter[str] = Counter()
    planned: List[tuple[Dict[str, Any], str]] = []
    for item in scripts:
        duplicate_index[item["name"]] += 1
        folder_name = safe_name(item["name"])
        if name_counts[item["name"]] > 1:
            folder_name = f"{folder_name}__{duplicate_index[item['name']]:02d}"
        planned.append((item, folder_name))

    names = [folder_name.casefold() for _, folder_name in planned]
    if len(names) != len(set(names)):
        raise SystemExit("脚本名称转换为文件夹后出现冲突，未写入任何文件；请先确认命名。")
    if any(item["code"] is None for item, _ in planned):
        raise SystemExit("存在脚本正文缺失或非文本的节点，未写入任何文件；请先确认源数据。")
    conflicts = [str(output_dir / folder_name) for _, folder_name in planned if (output_dir / folder_name).exists()]
    if conflicts:
        raise SystemExit("以下脚本目录已存在，为避免覆盖，未写入任何文件：\n" + "\n".join(conflicts))

    output_dir.mkdir(parents=True, exist_ok=True)
    for item, folder_name in planned:
        script_dir = output_dir / folder_name
        backup_dir = script_dir / "backup"
        backup_dir.mkdir(parents=True)
        extension = language_extension(item["language"])
        script_path = backup_dir / (safe_name(item["name"]) + extension)
        code = item.pop("code")
        if code is None:
            code = ""
            item["code_missing_or_non_text"] = True
        script_path.write_text(code, encoding="utf-8")
        item["source_file"] = str(source.resolve())
        item["source_version_id"] = version.get("id")
        item["source_version"] = version.get("version")
        item["selection_basis"] = selection
        item["backup_file"] = str(script_path.resolve())
        write_json(script_dir / "metadata.json", item)

    print(json.dumps({
        "source": str(source.resolve()),
        "selected_version": version.get("version"),
        "selection_basis": selection,
        "script_count": len(planned),
        "output_dir": str(output_dir.resolve()),
        "folders": [folder for _, folder in planned],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
