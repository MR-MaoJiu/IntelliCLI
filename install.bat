@echo off
REM IntelliCLI 快速安装脚本 (Windows)

echo 🚀 IntelliCLI 快速安装脚本
echo ==========================

REM 检查 Python 版本
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 python，请先安装 Python 3.8 或更高版本
    echo 💡 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python 版本: %PYTHON_VERSION%

REM 检查是否在项目目录中
if not exist "pyproject.toml" (
    echo ❌ 请在 IntelliCLI 项目根目录中运行此脚本
    pause
    exit /b 1
)

if not exist "intellicli" (
    echo ❌ 请在 IntelliCLI 项目根目录中运行此脚本
    pause
    exit /b 1
)

echo 📁 当前目录: %CD%

REM 询问安装模式
echo.
echo 请选择安装模式:
echo 1) 正常安装 - 全局安装 IntelliCLI
echo 2) 开发模式 - 可编辑安装，适合开发者
echo 3) 退出

set /p choice="请输入选择 (1-3): "

if "%choice%"=="1" (
    echo 🔧 开始正常安装...
    python -m pip install --upgrade pip
    if errorlevel 1 goto error
    python -m pip install .
    if errorlevel 1 goto error
) else if "%choice%"=="2" (
    echo 🔧 开始开发模式安装...
    python -m pip install --upgrade pip
    if errorlevel 1 goto error
    python -m pip install -e .[dev]
    if errorlevel 1 goto error
) else if "%choice%"=="3" (
    echo 👋 安装已取消
    pause
    exit /b 0
) else (
    echo ❌ 无效选择
    pause
    exit /b 1
)

REM 验证安装
echo.
echo 🧪 验证安装...

intellicli --help >nul 2>&1
if errorlevel 1 (
    echo ❌ 安装验证失败，请检查错误信息
    pause
    exit /b 1
)

echo ✅ IntelliCLI 安装成功！
echo.
echo 🎉 现在您可以在任意位置运行以下命令:
echo    • intellicli session  - 启动交互式会话
echo    • intellicli chat      - 单次对话
echo    • intellicli models    - 查看可用模型
echo    • intellicli config    - 查看配置
echo    • icli                 - 简短别名
echo.
echo 💡 首次运行时会自动启动配置向导
echo.
echo 🚀 开始使用:
echo    intellicli session
echo.
pause
exit /b 0

:error
echo ❌ 安装过程中出现错误
pause
exit /b 1 