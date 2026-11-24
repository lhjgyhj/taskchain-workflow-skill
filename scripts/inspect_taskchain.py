"""从任务链 JSON 生成精简全局地图，避免后续反复读取长 JSON。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from _taskchain_utils import choose_version, is_script_node, iter_workflow_nodes, iter_workflow_topologies, load_json, node_summary, write_json


def build_map(source: Path, data: Dict[str, Any], version_id: str | None) -> Dict[str, Any]:
    version, selection = choose_version(data, version_id)
    version_data = version.get("data") or {}
    topology = version_data.get("topology") or {}
    nodes = topology.get("nodeList") or []
    workflow_topologies = list(iter_workflow_topologies(topology))
    body = data.get("bodyInfo") or {}

    workflow_nodes = list(iter_workflow_nodes(topology))
    node_items = [node_summary(node) for node, _ in workflow_nodes]
    for item, (_, location) in zip(node_items, workflow_nodes):
        item["workflow_location"] = location
    script_items = [
        {**node_summary(node), "workflow_location": location}
        for node, location in workflow_nodes
        if is_script_node(node)
    ]
    code_counts: Dict[str, int] = {}
    for item in node_items:
        code = item.get("component_code") or "unknown"
        code_counts[code] = code_counts.get(code, 0) + 1

    normalized_links: List[Dict[str, Any]] = []
    for current_topology, location in workflow_topologies:
        for link in current_topology.get("linkList") or []:
            if not isinstance(link, dict):
                continue
            normalized_links.append({
                "workflow_location": location,
                "from": link.get("from") or {},
                "to": link.get("to") or {},
            })

    return {
        "schema_version": 1,
        "source_file": str(source.resolve()),
        "selection": {"basis": selection, "version_id": version.get("id"), "version": version.get("version"), "name": version.get("name")},
        "taskchain": {"id": body.get("id"), "name": body.get("name"), "tag_name": body.get("tagName"), "type": body.get("type")},
        "statistics": {"node_count": len(node_items), "link_count": len(normalized_links), "script_count": len(script_items), "component_counts": code_counts},
        "nodes": node_items,
        "scripts": script_items,
        "links": normalized_links,
        "warnings": (["未找到启用版本，已使用最后一个版本"] if selection.startswith("未找到") else []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="生成任务链精简全局地图")
    parser.add_argument("--source", required=True, help="任务链 JSON 文件")
    parser.add_argument("--output", required=True, help="地图输出 JSON 文件")
    parser.add_argument("--version-id", help="可选，指定 versionInfo 中的版本 ID")
    args = parser.parse_args()

    source = Path(args.source).expanduser()
    data = load_json(source)
    result = build_map(source, data, args.version_id)
    write_json(Path(args.output).expanduser(), result)
    print(json.dumps({"output": str(Path(args.output).expanduser().resolve()), "statistics": result["statistics"], "selection": result["selection"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
