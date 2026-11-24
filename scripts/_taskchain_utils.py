"""任务链工具共享函数。仅使用 Python 标准库。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("任务链 JSON 根对象必须是对象")
    return data


def choose_version(data: Dict[str, Any], version_id: Optional[str] = None) -> Tuple[Dict[str, Any], str]:
    versions = data.get("versionInfo") or []
    if not isinstance(versions, list) or not versions:
        raise ValueError("任务链 JSON 中没有可用的 versionInfo")

    if version_id:
        for version in versions:
            if version.get("id") == version_id:
                return version, "命令行指定版本"
        raise ValueError(f"找不到指定版本: {version_id}")

    enabled_id = (((data.get("bodyInfo") or {}).get("extendData") or {}).get("enable_version"))
    if enabled_id:
        for version in versions:
            if version.get("id") == enabled_id:
                return version, "bodyInfo.extendData.enable_version 指定的当前启用版本"

    raise ValueError("无法确定当前启用版本；请确认后使用 --version-id 明确指定版本")


def component(node: Dict[str, Any]) -> Dict[str, Any]:
    value = node.get("component")
    return value if isinstance(value, dict) else {}


def args_by_key(args: Any) -> Dict[str, Dict[str, Any]]:
    if not isinstance(args, list):
        return {}
    return {item.get("key"): item for item in args if isinstance(item, dict) and item.get("key")}


def arg_value(arg: Optional[Dict[str, Any]]) -> Any:
    if not arg:
        return None
    if "value" in arg:
        return arg.get("value")
    return arg.get("defaultValue")


def is_script_node(node: Dict[str, Any]) -> bool:
    comp = component(node)
    code = str(comp.get("code") or "")
    bean = str(comp.get("beanName") or "")
    return code in {"script", "scriptV2"} or "script-component" in bean


def script_details(node: Dict[str, Any]) -> Dict[str, Any]:
    comp = component(node)
    args = args_by_key(comp.get("inputArgs"))
    lang = arg_value(args.get("lang")) or "unknown"
    code = arg_value(args.get("code"))
    input_spec = args.get("input") if isinstance(args.get("input"), dict) else {}
    nested_input_args = (input_spec.get("props") or {}).get("args", [])
    if not isinstance(nested_input_args, list):
        nested_input_args = []
    return {
        "language": str(lang),
        "code": code if isinstance(code, str) else None,
        "input_args": [
            {"key": item.get("key"), "name": item.get("name"), "type": item.get("type"), "required": item.get("required")}
            for item in nested_input_args
            if isinstance(item, dict)
        ],
    }


def safe_name(value: str, fallback: str = "未命名脚本") -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value or "")
    cleaned = cleaned.strip().rstrip(".")
    return cleaned or fallback


def language_extension(language: str) -> str:
    value = language.lower()
    if "python" in value:
        return ".py"
    if "javascript" in value or value in {"js", "javascript"}:
        return ".js"
    if "groovy" in value:
        return ".groovy"
    return ".txt"


def node_summary(node: Dict[str, Any]) -> Dict[str, Any]:
    comp = component(node)
    props = node.get("props") if isinstance(node.get("props"), dict) else {}
    input_args = comp.get("inputArgs") if isinstance(comp.get("inputArgs"), list) else []
    output_args = comp.get("outputArgs") if isinstance(comp.get("outputArgs"), list) else []
    summary = {
        "node_id": node.get("id"),
        "name": node.get("name") or comp.get("name"),
        "component_name": comp.get("name"),
        "component_code": comp.get("code"),
        "component_type": comp.get("type"),
        "bean_name": comp.get("beanName"),
        "position": {"x": props.get("x"), "y": props.get("y")},
        "input_args": [
            {"key": item.get("key"), "name": item.get("name"), "type": item.get("type"), "required": item.get("required")}
            for item in input_args
            if isinstance(item, dict)
        ],
        "output_args": [
            {"key": item.get("key"), "name": item.get("name"), "type": item.get("type"), "required": item.get("required")}
            for item in output_args
            if isinstance(item, dict)
        ],
    }
    if is_script_node(node):
        details = script_details(node)
        summary["script"] = {"language": details["language"], "has_code": bool(details["code"])}
    return summary


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def iter_workflow_topologies(topology: Dict[str, Any], location: str = "主流程") -> Iterable[Tuple[Dict[str, Any], str]]:
    yield topology, location
    nodes = topology.get("nodeList") or []
    if not isinstance(nodes, list):
        return
    for node in nodes:
        if not isinstance(node, dict):
            continue
        comp = component(node)
        for arg in comp.get("inputArgs") or []:
            if not isinstance(arg, dict):
                continue
            nested_topologies = find_topologies(arg.get("defaultValue"))
            nested_topologies.extend(find_topologies(arg.get("value")))
            for nested_index, nested in enumerate(nested_topologies, start=1):
                nested_name = str(nested.get("name") or arg.get("name") or f"子流程{nested_index}")
                yield from iter_workflow_topologies(nested, f"{location}/{node.get('name') or comp.get('name')}/{nested_name}")


def iter_workflow_nodes(topology: Dict[str, Any], location: str = "主流程") -> Iterable[Tuple[Dict[str, Any], str]]:
    for current_topology, current_location in iter_workflow_topologies(topology, location):
        nodes = current_topology.get("nodeList") or []
        if not isinstance(nodes, list):
            continue
        for node in nodes:
            if isinstance(node, dict):
                yield node, current_location


def find_topologies(value: Any) -> List[Dict[str, Any]]:
    found: List[Dict[str, Any]] = []

    def visit(item: Any) -> None:
        if isinstance(item, dict):
            if isinstance(item.get("nodeList"), list) and isinstance(item.get("linkList"), list):
                found.append(item)
                return
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)

    visit(value)
    return found
