# SPI自动答题工具 - Windows部署清单

## 📋 迁移文件说明

### 压缩包信息
- 文件名: `spi-auto-answer-windows-final.tar.gz`
- 大小: 约 114MB
- 包含: 完整项目文件 + Windows专用配置和脚本

### 目标目录结构
```
E:\pg\spi-auto-answer\
│
├── 📁 主程序模块
│   ├── main.py                 # 程序入口
│   ├── ocr_handler.py         # OCR模块 (已优化Windows路径)
│   ├── api_handler.py         # API模块 (快速响应优化)
│   ├── excel_handler.py       # Excel题库模块
│   ├── gui_handler.py         # GUI界面模块
│   ├── hotkey_listener.py     # 热键监听模块 (已优化权限处理)
│   └── utils.py               # 工具函数模块
│
├── 📁 配置文件
│   ├── config.json            # 运行配置 (复制自.windows模板)
│   ├── config.json.windows    # Windows配置模板
│   └── requirements.txt       # Python依赖列表
│
├── 📁 文档说明
│   ├── README.md              # 项目说明
│   ├── WINDOWS_DEPLOYMENT.md  # Windows部署指南 ⭐
│   ├── MIGRATION_GUIDE.md     # 迁移详细指南 ⭐
│   ├── FILE_LIST.md           # 文件说明
│   ├── OCR_IMPLEMENTATION.md  # OCR技术说明
│   └── API_OPTIMIZATION_SUMMARY.md # API优化说明
│
├── 📁 Windows辅助脚本 ⭐
│   ├── scripts\windows_setup.bat     # 一键安装脚本
│   ├── scripts\setup_config.py      # 配置向导
│   └── scripts\test_dependencies.py # 依赖检查工具
│
└── 📁 可选文件
    ├── Dockerfile             # Docker配置
    ├── docker-compose.yml     # Docker编排
    └── docker-entrypoint.sh   # Docker入口
```

## 🚀 Windows快速部署流程

### 准备阶段
1. **解压文件**: 将压缩包解压到 `E:\pg\` 目录
2. **确认Python**: 确保已安装 Python 3.8+
3. **下载Tesseract**: 从 https://github.com/UB-Mannheim/tesseract/wiki 下载

### 自动安装 (推荐)
```cmd
cd E:\pg\spi-auto-answer
scripts\windows_setup.bat
```

### 手动安装
```cmd
cd E:\pg\spi-auto-answer
pip install -r requirements.txt
python scripts\setup_config.py
```

### 测试验证
```cmd
python scripts\test_dependencies.py
python main.py --test-api
python main.py --test-ocr
```

### 启动使用
```cmd
# 完整功能 (需要管理员权限)
python main.py

# 手动模式 (推荐)
python main.py --manual
```

## 🔧 核心优化内容

### 1. Windows路径适配
- OCR模块自动检测Windows Tesseract路径
- 支持常见安装位置: `C:\Program Files\Tesseract-OCR\`
- 配置模板使用Windows路径格式

### 2. 权限处理优化
- 热键模块优雅处理权限不足情况
- 提供手动模式作为备选方案
- 清晰的权限要求说明

### 3. 依赖检查增强
- Windows专用依赖检查脚本
- 自动检测Tesseract安装状态
- 管理员权限状态检查

### 4. 配置向导
- 交互式配置脚本
- Windows路径自动适配
- API快速配置模式

## 📊 功能对比

| 功能模块 | Linux状态 | Windows状态 | 兼容性 |
|---------|----------|-------------|--------|
| OCR识别 | ✅ 优秀 | ✅ 优秀 | 100% |
| API调用 | ✅ 快速 | ✅ 快速 | 100% |
| 热键监听 | ✅ 正常 | ⚠️ 需管理员 | 95% |
| GUI界面 | ✅ 稳定 | ✅ 稳定 | 100% |
| Excel题库 | ✅ 完整 | ✅ 完整 | 100% |
| 手动模式 | ✅ 支持 | ✅ 推荐 | 100% |

## ⚠️ 重要注意事项

### 1. 必需安装项
- ✅ Python 3.8+ (必需)
- ✅ Tesseract OCR + 日文语言包 (必需)
- ✅ Visual C++ Redistributable (可能需要)

### 2. 权限要求
- 🔐 热键功能: 需要管理员权限
- 📁 文件读写: 普通用户权限即可
- 🌐 网络访问: 需要防火墙允许

### 3. 配置重点
- 🔑 API密钥: 必须正确配置
- 📂 Tesseract路径: 根据安装位置调整
- ⌨️ 热键设置: 可自定义或使用手动模式

## 🆘 紧急问题解决

### 问题1: 无法启动
```cmd
python scripts\test_dependencies.py
# 查看具体缺失的依赖
```

### 问题2: OCR识别失败
```cmd
# 检查Tesseract安装
tesseract --version
tesseract --list-langs
```

### 问题3: API连接失败
```cmd
python main.py --test-api
# 检查网络和API配置
```

### 问题4: 权限问题
```cmd
# 使用手动模式
python main.py --manual
```

## 📞 支持信息

遇到问题时请提供：
1. 操作系统版本 (Windows版本)
2. Python版本 (`python --version`)
3. 错误日志内容
4. Tesseract安装状态 (`tesseract --version`)
5. 配置文件内容 (隐藏敏感信息)

---
**迁移完成后，建议首先运行依赖检查和功能测试确保系统正常工作！**
