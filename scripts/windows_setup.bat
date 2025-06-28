@echo off
REM SPI自动答题工具 - Windows一键安装脚本
REM 运行前请确保已安装Python 3.8+

echo ==========================================
echo SPI自动答题工具 - Windows安装向导
echo ==========================================

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python已安装

REM 检查pip是否可用
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: pip不可用，请检查Python安装
    pause
    exit /b 1
)

echo ✓ pip可用

REM 升级pip
echo 正在升级pip...
python -m pip install --upgrade pip

REM 安装Python依赖
echo 正在安装Python依赖包...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo 警告: 部分依赖包安装失败，请手动检查
)

echo ✓ Python依赖安装完成

REM 检查Tesseract是否已安装
tesseract --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未检测到Tesseract OCR
    echo 请手动安装Tesseract OCR:
    echo 1. 访问: https://github.com/UB-Mannheim/tesseract/wiki
    echo 2. 下载Windows安装包
    echo 3. 安装时选择日文语言包
    echo.
) else (
    echo ✓ Tesseract OCR已安装
)

REM 检查配置文件
if not exist "config.json" (
    echo 警告: 配置文件不存在，正在创建默认配置...
    copy "config.json.template" "config.json" >nul 2>&1
    echo 请编辑config.json文件，填入您的API配置
)

echo.
echo ==========================================
echo 安装完成！
echo ==========================================
echo.
echo 下一步操作:
echo 1. 编辑config.json文件，填入API密钥
echo 2. 确保已安装Tesseract OCR
echo 3. 运行测试: python main.py --test-api
echo 4. 启动程序: python main.py
echo.
echo 如需管理员权限（热键功能），请以管理员身份运行命令提示符
echo.

pause
