#!/bin/bash

# SPI自动答题工具部署脚本

set -e

echo "SPI自动答题工具 Docker部署脚本"
echo "================================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo "错误: config.json配置文件不存在"
    echo ""
    echo "请选择配置方式:"
    echo "1. 运行配置向导: ./setup_config.sh"
    echo "2. 复制模板文件: cp config.json.template config.json"
    echo "3. 手动创建配置文件"
    exit 1
fi

# 运行配置检查
echo "检查配置文件..."
if [ -f "check_config.sh" ]; then
    if ! ./check_config.sh > /dev/null 2>&1; then
        echo "配置文件检查发现问题，请运行以下命令查看详情:"
        echo "  ./check_config.sh"
        echo ""
        read -p "是否忽略警告并继续部署? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "部署已取消，请修复配置问题后重试"
            exit 1
        fi
    else
        echo "✅ 配置文件检查通过"
    fi
fi

# 创建题库文件（如果不存在）
if [ ! -f "questions.xlsx" ]; then
    echo "创建示例题库文件..."
    python3 -c "
import pandas as pd

# 创建示例题库数据
data_math = pd.DataFrame({
    'A': [
        '1 + 1 = ?',
        '2 × 3 = ?', 
        '10 ÷ 2 = ?',
        '5² = ?',
        '√16 = ?'
    ],
    'B': ['1', '5', '4', '20', '3'],
    'C': ['2', '6', '5', '25', '4'], 
    'D': ['3', '7', '6', '30', '5'],
    'E': ['4', '8', '7', '35', '6'],
    'F': ['B', 'B', 'C', 'B', 'B']
})

data_language = pd.DataFrame({
    'A': [
        '「おはよう」の意味として最も適切なものはどれですか？',
        '「ありがとう」の英語は何ですか？',
        '「さようなら」の使用場面として適切なのは？',
        '敬語として正しいのはどれですか？',
        '「頑張って」の意味に最も近いのは？'
    ],
    'B': ['こんばんは', 'Hello', '朝の挨拶', 'いく', 'やめる'],
    'C': ['おやすみ', 'Thank you', '昼の挨拶', 'いきます', 'がんばる'],
    'D': ['こんにちは', 'Goodbye', '別れの挨拶', 'いかれる', 'つづける'],
    'E': ['C', 'B', 'C', 'B', 'C']
})

data_logic = pd.DataFrame({
    '题目': [
        'AはBより背が高い。BはCより背が高い。この時、AとCの関係は？',
        '全ての犬は動物である。ポチは犬である。ポチについて言えることは？',
        '赤いボールが3個、青いボールが2個ある。ランダムに1個取る時、赤いボールを取る確率は？',
        '電車が1時間に60km進む。2時間30分で何km進むか？',
        '5人が円形に座る。AとBが隣り合わない座り方は何通りか？'
    ],
    '选项A': ['AはCより背が高い', 'ポチは動物である', '1/5', '120km', '48通り'],
    '选项B': ['CはAより背が高い', 'ポチは動物ではない', '2/5', '150km', '72通り'],
    '选项C': ['AとCは同じ身長', 'ポチは犬ではない', '3/5', '180km', '96通り'],
    '选项D': ['関係は不明', '何も言えない', '4/5', '200km', '120通り'],
    '正确答案': ['A', 'A', 'C', 'B', 'B']
})

# 保存到Excel文件
with pd.ExcelWriter('questions.xlsx', engine='openpyxl') as writer:
    data_math.to_excel(writer, sheet_name='数学问题', index=False)
    data_language.to_excel(writer, sheet_name='语言问题', index=False) 
    data_logic.to_excel(writer, sheet_name='逻辑问题', index=False)

print('示例Excel题库文件已创建: questions.xlsx')
"
fi

# 创建日志目录
mkdir -p logs

# 构建Docker镜像
echo "构建Docker镜像..."
docker build -t spi-auto-answer .

# 启动服务
echo "启动容器..."
docker-compose up -d

# 检查容器状态
echo "检查容器状态..."
sleep 5
docker-compose ps

# 显示日志
echo "容器日志:"
docker-compose logs --tail=20

echo ""
echo "部署完成!"
echo "容器已在后台运行"
echo ""
echo "常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  进入容器: docker-compose exec spi-auto-answer bash"
echo ""
echo "配置文件位置:"
echo "  主配置: ./config.json"
echo "  题库文件: ./questions.xlsx"
echo "  日志目录: ./logs/"
