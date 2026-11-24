# 高频工具使用说明

这些工具用于减少重复的机械操作和长 JSON 反复读取。它们都使用 Python 标准库，不需要联网，不主动安装依赖。

运行前置条件：本机可以使用 `python` 命令。Windows 路径可以用引号包裹，例如：

```powershell
python "C:\path\to\taskchain-workflow-skill\scripts\inspect_taskchain.py" --help
```

## 创建任务工作区

```powershell
python scripts/init_task_workspace.py --path "C:\任务\本次任务"
```

只创建 `ai痕迹/`、`doc/`、`code/`，不会创建具体脚本、跑批目录或执行任务。

## 生成任务链全局地图

```powershell
python scripts/inspect_taskchain.py --source "C:\任务\baseInfo.json" --output "C:\任务\ai痕迹\taskchain-map.json"
```

默认选择 `bodyInfo.extendData.enable_version` 指向的版本；无法确定时停止并请用户确认，再用 `--version-id` 指定版本。输出是结构化地图，后续优先读取它，不重复完整解析原始 JSON；输出文件已存在时不会覆盖。

## 拆分任务链脚本

```powershell
python scripts/split_taskchain_scripts.py --source "C:\任务\baseInfo.json" --output-dir "C:\任务\code"
```

脚本会为每个后端脚本建立独立目录，将原始正文放在该目录的 `backup/`，并生成 `metadata.json`。目标目录中若存在同名脚本目录，工具会停止，不覆盖已有内容。

## 创建脚本新版本

```powershell
python scripts/new_script_version.py --script-dir "C:\任务\code\脚本名称" --from v001
```

`--from` 必须明确写出来源版本，例如 `backup`、`v001`。工具自动创建下一个不存在的 `vNNN` 目录，拒绝覆盖已有目录。

## 创建跑批任务目录

```powershell
python scripts/init_batch_task.py --path "C:\任务\跑批任务"
```

创建 `config/`、`result/`、`code/backup/`、`code/v001/` 和 `start.bat` 模板。它不会运行跑批脚本；真实脚本、入口参数和鉴权配置必须在需求确认后补齐。

## 清点跑批结果

```powershell
python scripts/inspect_batch_results.py --result-dir "C:\任务\跑批任务\result" --output "C:\任务\ai痕迹\result-manifest.json"
```

工具只读取结果目录并写出清单，便于后续选择需要分析的文件。结果目录不存在或格式不明时，先向用户确认，不擅自创建虚假结果。

## 安全边界

- 工具默认不删除、不覆盖、不联网、不执行跑批。
- 任何脚本版本创建都要指定来源，避免把错误版本当作当前版本。
- 工具生成的模板不包含真实密钥、Token、账号或密码。
- 用户明确授权代跑前，不调用跑批入口；一次授权不自动延续到后续对话。
- 工具的输出优先写文件，回复中只说明路径和摘要。
