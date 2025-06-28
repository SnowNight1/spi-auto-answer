# SPI自动答题工具配置文件详细说明

## 配置文件概述

`config.json` 是SPI自动答题工具的核心配置文件，包含了API设置、OCR参数、Excel题库配置、GUI界面设置等所有重要参数。正确配置此文件对工具的正常运行至关重要。

## 配置文件结构

```json
{
  "api": { ... },           // API相关配置
  "ocr": { ... },           // OCR识别配置
  "hotkey": { ... },        // 热键设置
  "excel": { ... },         // Excel题库配置
  "gui": { ... },           // GUI界面配置
  "screenshot": { ... },    // 截图区域配置
  "logging": { ... }        // 日志配置
}
```

## 详细配置说明

### 1. API配置 (api)

这是最重要的配置部分，用于连接Azure OpenAI服务。

```json
{
  "api": {
    "api_key": "YOUR_AZURE_OPENAI_API_KEY",
    "api_endpoint": "https://your-resource.openai.azure.com/",
    "api_version": "2024-02-01",
    "deployment_name": "gpt-4",
    "model": "gpt-4",
    "max_tokens": 1000,
    "temperature": 0.1
  }
}
```

#### 配置项详解：

| 配置项 | 说明 | 示例值 | 必填 |
|--------|------|--------|------|
| `api_key` | Azure OpenAI API密钥 | `"abcd1234..."` | ✅ |
| `api_endpoint` | API端点URL | `"https://myai.openai.azure.com/"` | ✅ |
| `api_version` | API版本 | `"2024-02-01"` | ✅ |
| `deployment_name` | 部署模型名称 | `"gpt-4"` | ✅ |
| `model` | 使用的模型 | `"gpt-4"` | ✅ |
| `max_tokens` | 最大响应token数 | `1000` | ❌ |
| `temperature` | 响应随机性(0-1) | `0.1` | ❌ |

#### 获取API配置信息：

1. **登录Azure Portal**: https://portal.azure.com
2. **找到OpenAI资源**: 搜索并选择您的OpenAI资源
3. **获取密钥**: 在"密钥和终结点"页面复制密钥
4. **获取终结点**: 复制终结点URL
5. **查看部署**: 在"模型部署"页面查看部署名称

#### 常见错误：
- ❌ `api_key` 使用默认值 `"YOUR_AZURE_OPENAI_API_KEY"`
- ❌ `api_endpoint` 缺少尾部斜杠 `/`
- ❌ `deployment_name` 与Azure中的部署名不匹配

### 2. OCR配置 (ocr)

控制文字识别的精度和性能。

```json
{
  "ocr": {
    "language": "jpn",
    "psm": 6,
    "oem": 3,
    "dpi": 300,
    "preprocess": {
      "resize_factor": 2.0,
      "blur_kernel": 1,
      "threshold_type": "adaptive"
    }
  }
}
```

#### 配置项详解：

| 配置项 | 说明 | 可选值 | 推荐值 |
|--------|------|--------|--------|
| `language` | OCR识别语言 | `jpn`, `eng`, `chi_sim` | `jpn` |
| `psm` | 页面分割模式 | 0-13 | `6` |
| `oem` | OCR引擎模式 | 0-3 | `3` |
| `dpi` | 图像DPI | 72-600 | `300` |
| `resize_factor` | 图像缩放倍数 | 1.0-4.0 | `2.0` |
| `blur_kernel` | 降噪核大小 | 0-5 | `1` |
| `threshold_type` | 二值化方式 | `adaptive`, `otsu` | `adaptive` |

#### PSM模式说明：
- `6`: 单一文本块 (推荐用于SPI题目)
- `7`: 单一文本行
- `8`: 单一词汇
- `13`: 原始文本行

#### 优化建议：
- 识别率低时，增加 `resize_factor` 到 3.0
- 背景复杂时，使用 `adaptive` 阈值
- 文字清晰时，可降低 `blur_kernel` 到 0

### 3. 热键配置 (hotkey)

设置触发和控制热键。

```json
{
  "hotkey": {
    "trigger_key": "F12",
    "exit_key": "F11"
  }
}
```

#### 支持的热键：
- **功能键**: `F1`-`F12`
- **字母键**: `a`-`z`
- **数字键**: `0`-`9`
- **组合键**: `ctrl+shift+a`, `alt+f1`

#### 推荐设置：
- `trigger_key`: `F12` (不常用，避免冲突)
- `exit_key`: `F11` (快速退出)

### 4. Excel题库配置 (excel)

这是最灵活的配置部分，支持完全自定义的题库结构。

```json
{
  "excel": {
    "file_path": "questions.xlsx",
    "sheets_config": {
      "数学问题": {
        "question_column": "A",
        "answer_columns": ["B", "C", "D", "E"],
        "correct_answer_column": "F"
      },
      "语言问题": {
        "question_column": "A", 
        "answer_columns": ["B", "C", "D"],
        "correct_answer_column": "E"
      },
      "逻辑问题": {
        "question_column": "题目",
        "answer_columns": ["选项A", "选项B", "选项C", "选项D"],
        "correct_answer_column": "正确答案"
      }
    },
    "fuzzy_match": {
      "enabled": true,
      "threshold": 0.8,
      "max_results": 3
    }
  }
}
```

#### Sheet配置详解：

每个sheet可以独立配置列结构：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `question_column` | 题目所在列 | `"A"` 或 `"题目"` |
| `answer_columns` | 选项列数组 | `["B", "C", "D", "E"]` |
| `correct_answer_column` | 正确答案列 | `"F"` 或 `"正确答案"` |

#### 支持的列名格式：
- **字母列名**: `A`, `B`, `C`, `AA`, `AB`...
- **中文列名**: `题目`, `选项A`, `正确答案`
- **英文列名**: `Question`, `OptionA`, `Answer`

#### 模糊匹配配置：

| 配置项 | 说明 | 范围 | 推荐值 |
|--------|------|------|--------|
| `enabled` | 是否启用模糊匹配 | true/false | `true` |
| `threshold` | 匹配阈值 | 0.0-1.0 | `0.8` |
| `max_results` | 最大返回结果数 | 1-10 | `3` |

### 5. GUI界面配置 (gui)

控制悬浮窗口的外观和行为。

```json
{
  "gui": {
    "window": {
      "width": 300,
      "height": 150,
      "alpha": 0.9,
      "always_on_top": true,
      "initial_position": {
        "x": 100,
        "y": 100
      }
    },
    "font": {
      "family": "Arial Unicode MS",
      "size": 12,
      "weight": "bold"
    },
    "colors": {
      "background": "#000000",
      "text": "#00FF00",
      "border": "#FFFFFF"
    }
  }
}
```

#### 窗口配置：

| 配置项 | 说明 | 范围 | 推荐值 |
|--------|------|------|--------|
| `width` | 窗口宽度 | 200-800 | `300` |
| `height` | 窗口高度 | 100-600 | `150` |
| `alpha` | 透明度 | 0.1-1.0 | `0.9` |
| `always_on_top` | 保持最前 | true/false | `true` |

#### 字体配置：

推荐支持日文的字体：
- `Arial Unicode MS` (推荐)
- `Microsoft YaHei`
- `Noto Sans CJK`

#### 颜色主题：

**经典绿色主题** (护眼):
```json
{
  "background": "#000000",
  "text": "#00FF00",
  "border": "#FFFFFF"
}
```

**深色主题**:
```json
{
  "background": "#2b2b2b",
  "text": "#ffffff",
  "border": "#555555"
}
```

**浅色主题**:
```json
{
  "background": "#ffffff",
  "text": "#000000",
  "border": "#cccccc"
}
```

### 6. 截图配置 (screenshot)

控制截图的区域和方式。

```json
{
  "screenshot": {
    "region": {
      "x": 0,
      "y": 0,
      "width": 800,
      "height": 600
    },
    "auto_detect": true
  }
}
```

#### 区域设置：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `x` | 左上角X坐标 | `0` |
| `y` | 左上角Y坐标 | `0` |
| `width` | 截图宽度 | `800` |
| `height` | 截图高度 | `600` |
| `auto_detect` | 自动检测文字区域 | `true` |

#### 设置技巧：
1. **全屏截图**: 设置为屏幕分辨率
2. **浏览器窗口**: 通常800x600足够
3. **特定区域**: 可通过工具测量坐标

### 7. 日志配置 (logging)

控制日志记录的详细程度和存储。

```json
{
  "logging": {
    "level": "INFO",
    "file": "spi_auto_answer.log",
    "max_size": "10MB",
    "backup_count": 3
  }
}
```

#### 日志级别：

| 级别 | 说明 | 适用场景 |
|------|------|----------|
| `DEBUG` | 详细调试信息 | 开发调试 |
| `INFO` | 一般信息 | 正常使用 |
| `WARNING` | 警告信息 | 生产环境 |
| `ERROR` | 错误信息 | 问题排查 |

## 配置示例

### 基础配置示例

最小可用配置：

```json
{
  "api": {
    "api_key": "your-real-api-key-here",
    "api_endpoint": "https://your-resource.openai.azure.com/",
    "deployment_name": "gpt-4"
  },
  "excel": {
    "sheets_config": {
      "Sheet1": {
        "question_column": "A",
        "answer_columns": ["B", "C", "D"],
        "correct_answer_column": "E"
      }
    }
  }
}
```

### 高级配置示例

针对特定场景优化：

```json
{
  "api": {
    "api_key": "your-api-key",
    "api_endpoint": "https://your-resource.openai.azure.com/",
    "api_version": "2024-02-01",
    "deployment_name": "gpt-4",
    "model": "gpt-4",
    "max_tokens": 1500,
    "temperature": 0.05
  },
  "ocr": {
    "language": "jpn",
    "psm": 6,
    "preprocess": {
      "resize_factor": 3.0,
      "threshold_type": "adaptive"
    }
  },
  "excel": {
    "file_path": "spi_questions.xlsx",
    "sheets_config": {
      "数学题": {
        "question_column": "问题",
        "answer_columns": ["A", "B", "C", "D", "E"],
        "correct_answer_column": "答案"
      },
      "语言题": {
        "question_column": "题目",
        "answer_columns": ["选择1", "选择2", "选择3", "选择4"],
        "correct_answer_column": "正解"
      }
    },
    "fuzzy_match": {
      "threshold": 0.85,
      "max_results": 5
    }
  },
  "gui": {
    "window": {
      "width": 400,
      "height": 200,
      "alpha": 0.95
    },
    "colors": {
      "background": "#1a1a1a",
      "text": "#00ff41",
      "border": "#333333"
    }
  }
}
```

## 配置验证与测试

### 1. 配置文件语法检查

使用在线JSON验证器检查语法：
- https://jsonlint.com/
- https://jsonformatter.curiousconcept.com/

### 2. API连接测试

```bash
# 进入容器测试API连接
docker-compose exec spi-auto-answer python3 -c "
from api_handler import APIHandler
from utils import ConfigManager
config = ConfigManager()
api = APIHandler(config)
print('API测试:', api.test_connection())
"
```

### 3. OCR功能测试

```bash
# 测试OCR功能
docker-compose exec spi-auto-answer python3 -c "
from ocr_handler import OCRHandler
from utils import ConfigManager
config = ConfigManager()
ocr = OCRHandler(config)
print('屏幕信息:', ocr.get_screen_info())
"
```

### 4. Excel题库测试

```bash
# 测试Excel加载
docker-compose exec spi-auto-answer python3 -c "
from excel_handler import ExcelHandler
from utils import ConfigManager
config = ConfigManager()
excel = ExcelHandler(config)
print('题库统计:', excel.get_statistics())
"
```

## 常见配置问题与解决

### API配置问题

**问题**: API调用失败
```
解决方案:
1. 检查API密钥是否正确
2. 验证endpoint URL格式
3. 确认deployment_name存在
4. 检查Azure订阅状态
```

**问题**: API响应慢
```
解决方案:
1. 降低max_tokens到500-800
2. 调整temperature到0.1
3. 选择更近的Azure区域
```

### OCR配置问题

**问题**: 识别率低
```
解决方案:
1. 增加resize_factor到3.0-4.0
2. 调整PSM模式为6或7
3. 使用adaptive阈值
4. 检查截图区域设置
```

**问题**: OCR识别中文而非日文
```
解决方案:
1. 确认language设置为"jpn"
2. 检查Tesseract语言包安装
3. 验证字符白名单配置
```

### Excel配置问题

**问题**: 题库加载失败
```
解决方案:
1. 检查文件路径是否正确
2. 验证列名配置匹配
3. 确认Excel文件格式
4. 检查文件权限
```

**问题**: 搜索无结果
```
解决方案:
1. 降低匹配阈值到0.6-0.7
2. 检查问题文本清理逻辑
3. 验证数据格式一致性
```

## 性能调优建议

### 响应速度优化

1. **OCR优化**:
   - 适中的resize_factor (2.0-3.0)
   - 关闭不必要的预处理
   - 精确设置截图区域

2. **Excel查询优化**:
   - 合理的匹配阈值 (0.8)
   - 限制最大结果数 (3-5)
   - 定期清理题库数据

3. **API调用优化**:
   - 较低的temperature (0.1)
   - 适中的max_tokens (800-1000)
   - 启用题库缓存

### 内存使用优化

1. **图像处理**:
   - 避免过大的resize_factor
   - 及时释放图像资源
   - 限制调试图像保存

2. **数据缓存**:
   - 定期清理Excel缓存
   - 限制API响应历史
   - 合理的日志轮转

## 配置文件模板

我们提供了一个配置文件模板 `config.json.template`，您可以基于此模板创建自己的配置文件。

这个详细的配置说明应该能帮助用户正确配置和优化SPI自动答题工具。如果您需要更多特定方面的说明，请告诉我！
