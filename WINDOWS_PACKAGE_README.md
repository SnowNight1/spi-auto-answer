# SPI Auto Answer Tool - Windows Deployment Package

## Windows 移植说明

这是一个为Windows环境特别优化的SPI自动答题工具部署包。该包包含了所有必要的配置文件、脚本和说明，用于在Windows环境下快速部署和运行。

## 项目结构

```
E:\pg\spi-auto-answer\
├── main.py                    # 主程序入口
├── api_handler.py            # Azure OpenAI API处理器
├── ocr_handler.py            # OCR识别处理器
├── gui_handler.py            # GUI界面处理器
├── excel_handler.py          # Excel数据处理器
├── hotkey_listener.py        # 热键监听器
├── utils.py                  # 工具函数
├── config.json               # 主配置文件
├── requirements.txt          # Python依赖列表
├── setup_windows.bat         # Windows环境安装脚本
├── start.bat                 # 启动脚本
├── config_windows/           # Windows专用配置
│   ├── config.json.template  # 配置模板
│   └── config.json.backup    # 配置备份
├── scripts/                  # 辅助脚本
│   ├── install_tesseract.bat # Tesseract自动安装
│   ├── check_env.bat         # 环境检查
│   └── test_config.py        # 配置测试
├── docs/                     # 文档
│   ├── WINDOWS_GUIDE.md      # Windows使用指南
│   ├── CONFIG_GUIDE.md       # 配置指南
│   └── TROUBLESHOOTING.md    # 故障排除
└── logs/                     # 日志目录
```

## 快速开始

1. **解压到目标目录**：
   ```
   解压到 E:\pg\spi-auto-answer\
   ```

2. **运行安装脚本**：
   ```cmd
   cd E:\pg\spi-auto-answer
   setup_windows.bat
   ```

3. **配置API密钥**：
   编辑 `config.json` 文件，填入您的Azure OpenAI API信息

4. **启动程序**：
   ```cmd
   start.bat
   ```

## 主要特性

- ✅ 完全支持Windows 10/11
- ✅ 自动安装和配置Tesseract OCR
- ✅ 优化的中文/日文OCR识别
- ✅ Azure OpenAI API集成
- ✅ 实时屏幕截图分析
- ✅ 智能答案匹配算法
- ✅ 友好的GUI界面
- ✅ 完整的错误处理和日志记录

## 系统要求

- Windows 10 或更高版本
- Python 3.8+
- 至少 4GB RAM
- 1GB 可用磁盘空间
- 网络连接（用于API调用）

## 依赖组件

本包会自动安装以下组件：
- Python packages (见 requirements.txt)
- Tesseract OCR
- 必要的字体文件
- VC++ Redistributable (如需要)

## 配置说明

详细配置说明请参见：
- `docs/CONFIG_GUIDE.md` - 配置文件详解
- `docs/WINDOWS_GUIDE.md` - Windows特定说明

## 故障排除

如遇到问题，请参考：
- `docs/TROUBLESHOOTING.md` - 常见问题解决方案
- 运行 `scripts/check_env.bat` 检查环境

## 技术支持

如需要技术支持，请：
1. 查看日志文件：`logs/spi_auto_answer.log`
2. 运行环境检查：`scripts/check_env.bat`
3. 参考故障排除文档

## 版本信息

- 版本：v2.0-Windows
- 更新日期：2024-12-28
- 支持：Windows 10/11
- 兼容性：完全兼容原Linux版本功能

---

**注意**：首次运行前请务必配置 `config.json` 文件中的API密钥！
