# SPI自动答题工具 - Linux到Windows迁移指南

## 📦 迁移文件清单

从Linux系统迁移到Windows E:\pg目录的完整文件列表：

### 核心程序文件
```
E:\pg\spi-auto-answer\
├── main.py                    # 主程序入口
├── ocr_handler.py            # OCR处理模块 (已优化Windows支持)
├── api_handler.py            # API调用模块
├── excel_handler.py          # Excel题库处理模块
├── gui_handler.py            # GUI悬浮窗口模块
├── hotkey_listener.py        # 热键监听模块
└── utils.py                  # 工具函数库
```

### 配置文件
```
├── config.json.windows       # Windows专用配置模板
├── config.json              # 运行时配置文件 (需要编辑)
└── requirements.txt         # Python依赖包列表
```

### 文档和说明
```
├── README.md                # 项目说明文档
├── WINDOWS_DEPLOYMENT.md    # Windows部署指南
├── FILE_LIST.md            # 文件清单说明
├── OCR_IMPLEMENTATION.md   # OCR实现细节
└── API_OPTIMIZATION_SUMMARY.md  # API优化说明
```

### 辅助脚本
```
├── scripts\
│   ├── windows_setup.bat    # Windows一键安装脚本
│   ├── setup_config.py     # 交互式配置脚本
│   └── test_dependencies.py # 依赖检查脚本
```

### Docker相关 (可选)
```
├── Dockerfile              # Docker容器配置
├── docker-compose.yml      # Docker编排配置
└── docker-entrypoint.sh    # Docker入口脚本
```

## 🚀 快速迁移步骤

### 第一步：文件迁移
1. 下载项目压缩包: `spi-auto-answer-windows.tar.gz`
2. 解压到 `E:\pg\` 目录
3. 确保最终路径为: `E:\pg\spi-auto-answer\`

### 第二步：环境准备
```cmd
# 1. 确认Python版本 (需要3.8+)
python --version

# 2. 进入项目目录
cd E:\pg\spi-auto-answer

# 3. 运行Windows安装脚本
scripts\windows_setup.bat
```

### 第三步：依赖安装
```cmd
# 手动安装Python依赖
pip install -r requirements.txt

# 安装Tesseract OCR (手动下载安装)
# 下载地址: https://github.com/UB-Mannheim/tesseract/wiki
# 安装时选择日文语言包
```

### 第四步：配置设置
```cmd
# 方法1: 使用配置脚本
python scripts\setup_config.py

# 方法2: 手动复制配置
copy config.json.windows config.json
# 然后编辑 config.json 填入API密钥
```

### 第五步：功能测试
```cmd
# 测试依赖安装
python scripts\test_dependencies.py

# 测试API连接
python main.py --test-api

# 测试OCR功能
python main.py --test-ocr
```

### 第六步：启动程序
```cmd
# 完整功能 (需要管理员权限)
# 右键命令提示符 -> 以管理员身份运行
python main.py

# 手动模式 (无需管理员权限)
python main.py --manual
```

## 🔧 Windows特定配置

### 1. Tesseract OCR路径
Windows下Tesseract的默认安装路径：
```json
{
  "ocr": {
    "tesseract_cmd": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
  }
}
```

### 2. 管理员权限
热键功能在Windows下需要管理员权限：
- 右键命令提示符 → "以管理员身份运行"
- 或使用手动模式: `python main.py --manual`

### 3. 防火墙设置
确保Python可以访问网络：
- Windows设置 → 更新和安全 → Windows安全中心
- 防火墙和网络保护 → 允许应用通过防火墙
- 添加Python到允许列表

### 4. 路径分隔符
Windows使用反斜杠(\)作为路径分隔符，配置文件中需要使用双反斜杠(\\)转义。

## 📊 性能对比

| 功能 | Linux性能 | Windows性能 | 说明 |
|------|----------|-------------|------|
| API调用 | 0.4秒 | 0.4-0.5秒 | 网络性能类似 |
| OCR识别 | 优秀 | 优秀 | Tesseract跨平台一致 |
| 热键响应 | 快速 | 快速 | 需要管理员权限 |
| 截图功能 | 稳定 | 稳定 | GUI环境依赖 |
| 内存占用 | ~50MB | ~60MB | Windows稍高 |

## 🛠️ 故障排除

### 常见问题1: Tesseract未找到
```
错误: tesseract is not installed or it's not in your PATH
解决方案:
1. 下载安装Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. 确保安装时选择了日文语言包
3. 在config.json中指定完整路径
```

### 常见问题2: 权限错误
```
错误: You must be root to use this library
解决方案:
1. 以管理员身份运行命令提示符
2. 或使用手动模式: python main.py --manual
```

### 常见问题3: 依赖包安装失败
```
错误: Microsoft Visual C++ 14.0 is required
解决方案:
1. 安装Visual Studio Build Tools
2. 或下载预编译的wheel包
```

### 常见问题4: 路径包含中文
```
错误: UnicodeDecodeError
解决方案:
1. 避免路径中包含中文字符
2. 使用英文路径如: E:\pg\spi-auto-answer\
```

## 📈 优化建议

### 1. 性能优化
- 关闭不必要的后台程序
- 使用SSD硬盘存储项目文件
- 配置足够的虚拟内存

### 2. 稳定性优化
- 定期更新依赖包版本
- 使用稳定的网络连接
- 配置自动备份API配置

### 3. 安全优化
- 妥善保管API密钥
- 定期检查防火墙设置
- 避免在公共网络使用

## 🔄 版本更新

后续更新时的操作流程：
1. 备份当前 `config.json` 文件
2. 下载新版本文件
3. 替换程序文件（保留配置文件）
4. 运行依赖检查: `python scripts\test_dependencies.py`
5. 测试功能是否正常

## 📞 技术支持

遇到问题时的检查清单：
1. ✅ Python版本 >= 3.8
2. ✅ 所有依赖包已安装
3. ✅ Tesseract OCR已安装并配置
4. ✅ API密钥和端点已正确配置
5. ✅ 网络连接正常
6. ✅ 权限设置正确

如需更多帮助，请提供：
- 操作系统版本
- Python版本
- 错误日志内容
- 配置文件内容（隐藏敏感信息）
