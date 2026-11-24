"""初始化跑批任务结构和本地启动模板，不执行跑批。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


CONFIG_TEMPLATE = {
    "input_path": "",
    "output_dir": "result",
    "notes": "按当前跑批脚本的配置格式填写；不要在此保存未授权的真实密钥。",
}

LAUNCHER_TEMPLATE = r'''@echo off
setlocal
cd /d "%~dp0"
set "ENTRY=%~dp0code\v001\main.py"
if not exist "%ENTRY%" (
    echo Entry script not found: "%ENTRY%"
    echo Place the confirmed batch script at code\v001\main.py or update this launcher.
    pause
    exit /b 1
)
python "%ENTRY%" --config "%~dp0config\config.json" --result-dir "%~dp0result"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
echo Process finished with exit code %EXIT_CODE%.
pause
exit /b %EXIT_CODE%
'''


def main() -> int:
    parser = argparse.ArgumentParser(description="创建跑批任务目录模板，不运行脚本")
    parser.add_argument("--path", required=True, help="跑批任务目录")
    args = parser.parse_args()

    root = Path(args.path).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    planned_files = [root / "config" / "config.json", root / "start.bat"]
    conflicts = [str(path) for path in planned_files if path.exists()]
    if conflicts:
        raise SystemExit("以下模板文件已存在，为避免覆盖，未写入模板：\n" + "\n".join(conflicts))

    (root / "config").mkdir(exist_ok=True)
    (root / "result").mkdir(exist_ok=True)
    (root / "code" / "backup").mkdir(parents=True, exist_ok=True)
    (root / "code" / "v001").mkdir(parents=True, exist_ok=True)
    with planned_files[0].open("w", encoding="utf-8") as handle:
        json.dump(CONFIG_TEMPLATE, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    planned_files[1].write_text(LAUNCHER_TEMPLATE, encoding="utf-8")

    print(json.dumps({
        "root": str(root.resolve()),
        "config": str(planned_files[0].resolve()),
        "result_dir": str((root / "result").resolve()),
        "launcher": str(planned_files[1].resolve()),
        "code_dir": str((root / "code").resolve()),
        "runs_batch": False,
        "launcher_note": "启动模板约定入口为 code/v001/main.py，并向其传入 --config 与 --result-dir；实际脚本接口不同时需按确认后的接口调整启动器。",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
