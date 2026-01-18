#!/bin/bash

echo "======================================"
echo "企业笔试题提取系统 - 快速验证"
echo "======================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

echo "[1/5] 检查虚拟环境..."
if [ ! -d "venv" ]; then
    echo "  创建虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "  ✓ 虚拟环境已激活"

echo ""
echo "[2/5] 安装依赖..."
pip install -q -r requirements.txt
echo "  ✓ 依赖安装完成"

echo ""
echo "[3/5] 检查配置..."
if [ ! -f ".env" ]; then
    echo "  ⚠ 未找到.env文件，从模板创建..."
    cp .env.example .env
    echo ""
    echo "  请编辑 .env 文件并配置你的API密钥："
    echo "    1. 打开 .env 文件"
    echo "    2. 填入 CLAUDE_API_KEY 或 OPENAI_API_KEY"
    echo "    3. 设置 LLM_PROVIDER 为 claude 或 openai"
    echo ""
    echo "  配置完成后，再次运行此脚本。"
    exit 0
else
    echo "  ✓ 配置文件存在"
fi

echo ""
echo "[4/5] 初始化数据库..."
python scripts/init_database.py
echo ""

echo "[5/5] 测试LLM连接..."
python scripts/test_llm.py
echo ""

echo "======================================"
echo "快速验证完成！"
echo "======================================"
echo ""
echo "下一步："
echo "  1. 将PDF文件放入 data/pdfs/ 目录"
echo "  2. 运行: python scripts/process_pdf.py data/pdfs/your_file.pdf"
echo ""
echo "或者测试示例数据（需要先将示例文本转换为PDF）"
echo ""
