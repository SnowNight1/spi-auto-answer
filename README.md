# SPI自动答题工具使用说明

## 项目简介

SPI自动答题工具是一个专门针对日本SPI等网络测试设计的辅助工具，具备OCR文字识别、Excel题库查询、大模型API解题和悬浮窗口提示等功能。

## 主要特性

- 🔍 **OCR文字识别**: 支持日文题目识别，针对SPI测试优化
- 📚 **Excel题库查询**: 灵活的多sheet题库配置，支持模糊匹配
- 🤖 **AI智能解答**: 集成Azure OpenAI API，专业的日文SPI解题
- 🎯 **悬浮窗口提示**: 透明悬浮窗，实时显示答案
- ⌨️ **热键触发**: 一键触发，无需鼠标操作
- 🐳 **Docker部署**: 完整的容器化解决方案

## OCR技术实现

### 核心技术栈
- **OCR引擎**: Tesseract OCR 4.0+ (专业级开源OCR)
- **日文支持**: 原生支持日文识别，包含完整的平假名、片假名字符集
- **图像处理**: OpenCV + PIL 双重图像处理管道
- **智能检测**: MSER算法自动检测文字区域

### 技术特性
✅ **高精度识别**: 针对日文SPI题目优化的识别参数  
✅ **智能预处理**: 自适应二值化、降噪、锐化增强  
✅ **多重备用**: 多种OCR配置自动切换，确保识别成功  
✅ **实时优化**: 根据系统性能自动调整处理参数  
✅ **错误恢复**: 健壮的错误处理机制，依赖缺失时优雅降级  

### 实现亮点
- **屏幕截图**: `PIL.ImageGrab` + `pyautogui` 双重截图方案
- **区域检测**: MSER + 轮廓检测算法自动定位文字
- **图像预处理**: 灰度转换 → 尺寸放大 → 降噪 → 自适应二值化
- **OCR优化**: 多种PSM模式自动切换，专门的日文字符集优化
- **文本清理**: 智能去噪、错误修正、日文标点规范化

📖 **详细实现**: 参见 [OCR_IMPLEMENTATION.md](OCR_IMPLEMENTATION.md)

## 快速开始

### 1. 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- Linux/macOS/Windows (推荐Linux)

### 2. 配置文件设置

#### 方法一：使用配置向导（推荐）

```bash
# 运行交互式配置向导
./setup_config.sh
```

配置向导会引导您完成：
- Azure OpenAI API配置
- 热键设置
- Excel题库配置
- 截图区域设置
- GUI主题选择

#### 方法二：快速API配置（新增）

```bash
# 专门用于快速响应模式的API配置
./setup_fast_api.py

# 仅测试API连接
./setup_fast_api.py --test

# 查看优化建议
./setup_fast_api.py --tips
```

**快速响应优化配置**:
- max_tokens: 300（快速响应）
- temperature: 0.3（平衡准确性和速度）
- timeout: 20秒（缩短等待时间）

#### 方法三：手动配置

```bash
# 复制配置模板
cp config.json.template config.json

# 编辑配置文件
nano config.json
```

**必须配置的API信息：**
```json
{
  "api": {
    "api_key": "您的API密钥",
    "api_endpoint": "https://your-resource.openai.azure.com/",
    "deployment_name": "gpt-4",
    "model": "gpt-4",
    "max_tokens": 300,
    "temperature": 0.3,
    "timeout": 20
  }
}
```

#### 详细配置说明

📖 **完整配置指南**: [CONFIG_GUIDE.md](CONFIG_GUIDE.md)  
⚡ **API优化说明**: [API_OPTIMIZATION_SUMMARY.md](API_OPTIMIZATION_SUMMARY.md)

配置文档包含：
- 所有配置项的详细说明
- Excel题库格式和自定义配置
- 快速响应模式优化参数
- 性能优化建议
- 故障排除指南

### 3. 部署运行

```bash
# 克隆或下载项目文件
# 进入项目目录
cd spi-auto-answer

# 运行部署脚本
./deploy.sh
```

### 4. 使用方法

1. **启动应用**: 容器启动后，应用会自动运行
2. **热键触发**: 按 `F12` 键触发答题流程
3. **查看答案**: 答案会显示在悬浮窗口中
4. **退出应用**: 按 `F11` 键退出

## 配置文件详解

### 快速配置

运行配置向导：
```bash
./setup_config.sh
```

### Excel题库配置示例

支持完全自定义的列结构：

```json
{
  "excel": {
    "sheets_config": {
      "数学题": {
        "question_column": "A",
        "answer_columns": ["B", "C", "D", "E"],
        "correct_answer_column": "F"
      },
      "自定义格式": {
        "question_column": "题目",
        "answer_columns": ["选项1", "选项2", "选项3"],
        "correct_answer_column": "答案"
      }
    }
  }
}
```

### 常用配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `hotkey.trigger_key` | 触发热键 | `F12` |
| `ocr.language` | OCR语言 | `jpn` |
| `gui.window.alpha` | 窗口透明度 | `0.9` |
| `excel.fuzzy_match.threshold` | 匹配阈值 | `0.8` |

📖 **详细配置说明**: [CONFIG_GUIDE.md](CONFIG_GUIDE.md)

## Excel题库格式

### 示例格式

| A (题目) | B (选项1) | C (选项2) | D (选项3) | E (选项4) | F (正确答案) |
|---------|-----------|-----------|-----------|-----------|------------|
| 1+1=? | 1 | 2 | 3 | 4 | B |
| 「おはよう」の意味は？ | こんばんは | おやすみ | こんにちは | - | C |

### 自定义列配置

您可以在 `config.json` 中自定义列名和位置：

```json
{
  "excel": {
    "sheets_config": {
      "自定义Sheet": {
        "question_column": "题目",
        "answer_columns": ["选项A", "选项B", "选项C", "选项D"],
        "correct_answer_column": "正确答案"
      }
    }
  }
}
```

## Docker操作命令

```bash
# 查看容器状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 进入容器
docker-compose exec spi-auto-answer bash

# 重新构建并启动
docker-compose up --build -d
```

## 工作流程

1. **按下F12热键** → 触发答题流程
2. **屏幕截图** → 自动截取指定区域
3. **OCR识别** → 提取日文题目文字
4. **题库查询** → 在Excel题库中搜索匹配题目
5. **AI解答** → 如题库无匹配，调用OpenAI API
6. **显示答案** → 在悬浮窗口中显示结果

## 故障排除

### OCR相关工具

**依赖检查和安装:**
```bash
# 检查OCR依赖是否完整
./check_ocr_dependencies.sh

# 自动优化OCR配置
./optimize_ocr_config.sh
```

**性能测试:**
```bash
# 运行OCR性能基准测试
python3 ocr_benchmark.py

# 测试OCR模块功能
python3 -c "from ocr_handler import test_ocr_handler; test_ocr_handler()"
```

### 常见问题

1. **OCR识别率低**
   - 运行 `./check_ocr_dependencies.sh` 检查依赖
   - 使用 `./optimize_ocr_config.sh` 自动优化配置
   - 调整截图区域，确保文字清晰
   - 检查Tesseract日文语言包安装

2. **依赖包缺失**
   ```bash
   # 安装基础依赖
   pip install Pillow pytesseract opencv-python pyautogui numpy
   
   # Ubuntu/Debian系统安装Tesseract
   sudo apt-get install tesseract-ocr tesseract-ocr-jpn
   
   # 检查安装状态
   ./check_ocr_dependencies.sh
   ```

3. **API调用失败**
   - 验证API密钥和endpoint
   - 检查网络连接
   - 确认API配额

4. **热键不响应**
   - 检查键盘权限
   - 尝试更换热键
   - 查看容器日志

5. **题库查询无结果**
   - 验证Excel文件格式
   - 检查列配置
   - 调整模糊匹配阈值

### 日志查看

```bash
# 查看应用日志
docker-compose logs -f spi-auto-answer

# 查看特定时间段日志
docker-compose logs --since="1h" spi-auto-answer

# 在容器内查看日志文件
docker-compose exec spi-auto-answer tail -f /app/logs/spi_auto_answer.log
```

## 性能优化

### OCR优化
- 调整 `resize_factor` 提高识别精度
- 使用 `adaptive` 阈值处理复杂背景
- 配置合适的 `psm` 模式

### 题库查询优化
- 使用精确匹配优先策略
- 调整模糊匹配阈值
- 优化题库结构

### API调用优化
- 设置合适的 `temperature` 值
- 使用缓存避免重复调用
- 配置重试机制

## 安全注意事项

⚠️ **重要提醒**:
- 本工具仅用于个人学习和测试目的
- 不得用于正式考试作弊
- 请遵守相关法律法规和平台规则
- 保护好您的API密钥，避免泄露

## 技术支持

如遇到问题，请：

1. 查看日志文件确定错误原因
2. 检查配置文件格式
3. 验证依赖服务状态
4. 参考故障排除章节

## 更新说明

### v1.0 (当前版本)
- 完整的SPI答题功能
- Docker容器化部署
- 多语言OCR支持
- 灵活的Excel题库配置
- Azure OpenAI API集成

## 许可证

本项目仅供学习交流使用，请勿用于商业用途或违法行为。
