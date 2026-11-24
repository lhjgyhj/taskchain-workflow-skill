# taskchain-workflow-skill

> **本文档是写给人看的项目说明，不是给 AI 执行任务的指令。**
>
> AI 使用本项目时，应以 [`SKILL.md`](SKILL.md) 及其引用的 `references/` 文件为准；`README.md` 只用于帮助人理解项目用途、目录结构和基本维护方式。

## 项目简介

`taskchain-workflow-skill` 用于辅助设计、梳理和最小化修改讯飞星火智能体平台任务链。

它适用于两类工作：

- 根据需求从零梳理任务链流程、组件、入参、出参、数据流和验收方式；
- 基于已有任务链进行需求变更，只修改达成需求所必需的最小范围。

项目内置了离线组件知识层和若干高频工具，用于减少重复读取长任务链 JSON、重复拆分脚本和重复建立工作目录带来的时间与上下文消耗。

## 主要能力

- 任务需求确认与方案审批流程；
- 已有任务链的全局地图和增量修改原则；
- 组件分类、用途、关键输入输出和常见组合方式的离线索引；
- 任务链版本识别，优先识别当前启用版本；
- 任务链后端脚本按脚本名称拆分归档；
- 原始脚本备份和修改版本副本管理；
- 跑批任务的配置、结果、代码和启动入口目录模板；
- 跑批执行授权边界：默认由用户执行，代跑需要明确授权；
- 任务链和跑批结果的精简清单生成。

## 目录结构

```text
taskchain-workflow-skill/
├─ SKILL.md
├─ README.md
├─ references/
│  ├─ component-index.json
│  ├─ components-catalog.md
│  ├─ tooling.md
│  └─ workspace-and-versioning.md
└─ scripts/
   ├─ _taskchain_utils.py
   ├─ init_task_workspace.py
   ├─ inspect_taskchain.py
   ├─ split_taskchain_scripts.py
   ├─ new_script_version.py
   ├─ init_batch_task.py
   └─ inspect_batch_results.py
```

## 使用入口

AI 的正式使用入口是：

```text
SKILL.md
```

组件知识和工作区规则按需读取：

- `references/component-index.json`：机器可检索的离线组件索引；
- `references/components-catalog.md`：面向任务链设计的组件说明；
- `references/tooling.md`：高频工具使用方法；
- `references/workspace-and-versioning.md`：具体任务的工作区和版本管理规则。

## 高频工具

以下命令均使用 Python 标准库，不主动联网，也不会默认执行跑批：

```powershell
# 创建任务工作区
python scripts/init_task_workspace.py --path "C:\任务\本次任务"

# 生成任务链精简全局地图
python scripts/inspect_taskchain.py --source "C:\任务\baseInfo.json" --output "C:\任务\ai痕迹\taskchain-map.json"

# 拆分任务链中的后端脚本
python scripts/split_taskchain_scripts.py --source "C:\任务\baseInfo.json" --output-dir "C:\任务\code"

# 从明确版本创建新的脚本副本
python scripts/new_script_version.py --script-dir "C:\任务\code\脚本名称" --from backup

# 创建跑批任务目录
python scripts/init_batch_task.py --path "C:\任务\跑批任务"

# 清点跑批结果
python scripts/inspect_batch_results.py --result-dir "C:\任务\跑批任务\result" --output "C:\任务\ai痕迹\result-manifest.json"
```

完整参数和边界说明见 [`references/tooling.md`](references/tooling.md)。

## 维护提示

- `SKILL.md` 是 AI 执行规则，不要把一次具体任务的业务内容写入其中。
- 组件离线资料用于日常快速设计；只有遇到本地资料缺失、版本冲突或明确要求时，才需要回查官方文档。
- 任务链实际导出结构优先于抽象组件索引，尤其是 `component.code`、节点参数和连线结构。
- 脚本工具默认避免覆盖已有文件；使用前确认输出路径和版本来源。
- 真实密钥、Token、账号和密码不应提交到仓库。

## 官方文档

组件官方说明入口：

<https://flames.iflytek.com:2443/agent/docs/components/components-overviews.html>
