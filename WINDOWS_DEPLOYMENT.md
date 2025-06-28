# SPI自动答题工具 - Windows部署指南

## 📋 系统要求
- Windows 10/11 (64位)
- Python 3.8+ 
- 管理员权限（用于热键功能）
- 稳定的网络连接（用于API调用）

## 🚀 快速部署步骤

### 1. 解压项目文件
```cmd
# 将项目文件解压到 E:\pg\ 目录
# 最终路径应为: E:\pg\spi-auto-answer\
```

### 2. 安装Python依赖
```cmd
cd E:\pg\spi-auto-answer
pip install -r requirements.txt
```

### 3. 安装Tesseract OCR
下载并安装Tesseract OCR for Windows:
- 访问: https://github.com/UB-Mannheim/tesseract/wiki
- 下载最新版本的安装包
- 安装时**务必选择日文语言包(Japanese)**
- 默认安装路径: `C:\Program Files\Tesseract-OCR\`

### 4. 配置API密钥
编辑 `config.json` 文件，填入您的Azure OpenAI配置:
```json
{
  "api": {
    "api_key": "您的API密钥",
    "api_endpoint": "您的API端点",
    "deployment_name": "gpt-4"
  }
}
```

### 5. 运行程序
```cmd
# 测试API连接
python main.py --test-api

# 测试OCR功能
python main.py --test-ocr

# 启动程序（需要管理员权限以使用热键）
# 右键点击命令提示符 -> 以管理员身份运行
python main.py

# 或使用手动模式（无需管理员权限）
python main.py --manual
```

## 🔧 Windows特定配置

### Tesseract路径配置
如果Tesseract不在默认路径，请在 `config.json` 中指定:
```json
{
  "ocr": {
    "tesseract_cmd": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
  }
}
```

### 热键权限问题
Windows下热键功能需要管理员权限：
1. 右键点击命令提示符 -> "以管理员身份运行"
2. 或使用 `--manual` 参数启动手动模式

### 防火墙设置
确保Python程序可以访问网络：
1. Windows防火墙 -> 允许应用通过防火墙
2. 添加Python到允许列表

## 📁 Windows目录结构
```
E:\pg\spi-auto-answer\
├── main.py                    # 主程序
├── config.json               # 配置文件
├── requirements.txt          # Python依赖
├── ocr_handler.py            # OCR处理模块
├── api_handler.py            # API调用模块
├── excel_handler.py          # Excel题库模块
├── gui_handler.py            # GUI界面模块
├── hotkey_listener.py        # 热键监听模块
├── utils.py                  # 工具函数
├── Dockerfile               # Docker配置
├── docker-compose.yml       # Docker Compose配置
├── README.md                # 使用说明
├── WINDOWS_DEPLOYMENT.md    # Windows部署指南
└── scripts\                 # 辅助脚本
    ├── setup_config.py     # 快速配置脚本
    ├── test_dependencies.py # 依赖检查脚本
    └── windows_setup.bat   # Windows一键安装脚本
```

## 🛠️ 故障排除

### 1. Tesseract未找到
```
错误: tesseract is not installed or it's not in your PATH
解决: 
1. 确认Tesseract已正确安装
2. 检查PATH环境变量是否包含Tesseract路径
3. 在config.json中指定完整路径
```

### 2. 权限错误
```
错误: You must be root to use this library on linux.
解决: 在Windows下以管理员身份运行命令提示符
```

### 3. API连接失败
```
错误: API连接测试失败
解决:
1. 检查网络连接
2. 确认API密钥和端点正确
3. 检查防火墙设置
```

### 4. 截图功能失败
```
错误: 所有截图方法都失败了
解决:
1. 确认程序在图形界面环境中运行
2. 检查是否有其他程序占用屏幕资源
3. 尝试重启程序
```

## 📞 技术支持

如果遇到问题，请检查:
1. Python版本 (python --version)
2. 依赖安装情况 (pip list)
3. Tesseract安装状态 (tesseract --version)
4. 日志文件内容

## 🎯 性能优化建议

1. **内存优化**: 关闭不必要的后台程序
2. **网络优化**: 使用稳定的网络连接
3. **权限优化**: 以管理员身份运行以获得最佳性能
4. **路径优化**: 使用较短的安装路径避免路径长度限制

## 🔄 更新说明

定期检查更新:
1. 备份当前配置文件
2. 下载新版本文件
3. 恢复配置文件
4. 测试功能是否正常
