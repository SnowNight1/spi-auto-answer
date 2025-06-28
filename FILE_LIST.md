# SPI自动答题工具 - 项目文件清单

## 📁 项目结构

```
spi-auto-answer/
├── 🔧 配置文件
│   ├── config.json                 # 主配置文件 (需要用户配置)
│   ├── config.json.template        # 配置文件模板
│   └── CONFIG_GUIDE.md            # 详细配置说明文档
│
├── 🐍 Python模块
│   ├── main.py                     # 主程序入口
│   ├── utils.py                    # 工具函数模块
│   ├── ocr_handler.py             # OCR处理模块
│   ├── excel_handler.py           # Excel题库处理模块
│   ├── api_handler.py             # API调用模块
│   ├── gui_handler.py             # GUI悬浮窗口模块
│   └── hotkey_listener.py         # 热键监听模块
│
├── 🐳 Docker部署
│   ├── Dockerfile                  # Docker镜像构建文件
│   ├── docker-compose.yml         # Docker服务编排
│   └── docker-entrypoint.sh       # 容器启动脚本
│
├── 📊 数据文件
│   ├── questions.xlsx              # Excel题库文件 (自动生成示例)
│   └── requirements.txt           # Python依赖列表
│
├── 🔧 管理脚本
│   ├── deploy.sh                   # 一键部署脚本
│   ├── setup_config.sh            # 交互式配置向导
│   └── check_config.sh            # 配置文件检查器
│
├── 📁 运行时目录
│   ├── logs/                       # 日志文件目录
│   └── debug_images/              # 调试图片目录 (debug模式)
│
└── 📖 文档
    ├── README.md                   # 项目说明文档
    ├── CONFIG_GUIDE.md            # 配置详细说明
    └── FILE_LIST.md               # 本文件清单
```

## 🚀 快速开始流程

### 1. 获取项目文件
```bash
# 确保所有文件都在项目目录中
ls -la spi-auto-answer/
```

### 2. 配置系统
```bash
# 方法一: 使用配置向导 (推荐)
./setup_config.sh

# 方法二: 手动配置
cp config.json.template config.json
nano config.json
```

### 3. 检查配置
```bash
# 验证配置正确性
./check_config.sh
```

### 4. 部署运行
```bash
# 一键部署
./deploy.sh
```

## 📋 核心文件说明

### 配置相关文件

| 文件 | 用途 | 是否必需 | 说明 |
|------|------|----------|------|
| `config.json` | 主配置文件 | ✅ 必需 | 包含API密钥等关键配置 |
| `config.json.template` | 配置模板 | 📖 参考 | 用于创建配置文件的模板 |
| `CONFIG_GUIDE.md` | 配置说明 | 📖 参考 | 详细的配置参数说明 |

### 脚本工具

| 文件 | 用途 | 权限 | 说明 |
|------|------|------|------|
| `setup_config.sh` | 配置向导 | `+x` | 交互式创建配置文件 |
| `check_config.sh` | 配置检查 | `+x` | 验证配置文件正确性 |
| `deploy.sh` | 部署脚本 | `+x` | 一键部署整个系统 |

### 核心模块

| 文件 | 功能 | 依赖 |
|------|------|------|
| `main.py` | 主程序 | 所有模块 |
| `utils.py` | 工具函数 | PIL, OpenCV, logging |
| `ocr_handler.py` | OCR识别 | tesseract, pyautogui |
| `excel_handler.py` | 题库查询 | pandas, openpyxl, fuzzywuzzy |
| `api_handler.py` | API调用 | requests |
| `gui_handler.py` | 悬浮窗口 | tkinter |
| `hotkey_listener.py` | 热键监听 | keyboard |

## 🔧 配置文件重点

### 必须配置项
- `api.api_key` - Azure OpenAI API密钥
- `api.api_endpoint` - API端点URL
- `api.deployment_name` - 模型部署名称

### 可选配置项
- `hotkey.trigger_key` - 触发热键 (默认: F12)
- `ocr.language` - OCR语言 (默认: jpn)
- `excel.file_path` - 题库文件路径
- `gui.window.alpha` - 窗口透明度

## 📊 Excel题库格式

### 标准格式示例
```
| A (题目) | B (选项1) | C (选项2) | D (选项3) | E (答案) |
|----------|-----------|-----------|-----------|---------|
| 1+1=?    | 1         | 2         | 3         | B       |
```

### 自定义格式示例
```
| 题目 | 选项A | 选项B | 选项C | 正确答案 |
|------|-------|-------|-------|----------|
| 计算题 | 选择1 | 选择2 | 选择3 | 选项B    |
```

## 🐳 Docker相关

### 容器操作命令
```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 进入容器
docker-compose exec spi-auto-answer bash
```

### 数据持久化
- `./config.json` → `/app/config.json`
- `./questions.xlsx` → `/app/questions.xlsx`
- `./logs/` → `/app/logs/`

## 🔍 故障排除

### 常见问题文件
1. **配置问题** → 查看 `CONFIG_GUIDE.md`
2. **部署问题** → 查看 `deploy.sh` 输出
3. **运行问题** → 查看 `logs/spi_auto_answer.log`

### 配置验证工具
```bash
# 检查配置完整性
./check_config.sh

# 重新配置
./setup_config.sh

# 检查JSON格式
python3 -m json.tool config.json
```

## 📝 文件权限

确保以下文件有执行权限：
```bash
chmod +x deploy.sh
chmod +x setup_config.sh
chmod +x check_config.sh
chmod +x docker-entrypoint.sh
```

## 🔄 更新流程

1. 备份当前配置: `cp config.json config.json.backup`
2. 更新项目文件
3. 检查配置兼容性: `./check_config.sh`
4. 重新部署: `./deploy.sh`

## 💡 最佳实践

1. **首次使用**: 运行 `./setup_config.sh` 创建配置
2. **配置修改**: 使用 `./check_config.sh` 验证
3. **定期备份**: 备份 `config.json` 和 `questions.xlsx`
4. **日志监控**: 定期查看 `logs/` 目录
5. **性能优化**: 参考 `CONFIG_GUIDE.md` 优化建议

---

📖 **需要帮助？**
- 详细配置: [CONFIG_GUIDE.md](CONFIG_GUIDE.md)
- 项目说明: [README.md](README.md)
- 在线支持: 查看日志文件排查问题
